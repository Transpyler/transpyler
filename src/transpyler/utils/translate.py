"""
This module is not imported by the user, but rather it generates translation
strings for transpyler functions.
"""

import gettext
import os
import sys
import types
from collections import OrderedDict, defaultdict
from functools import singledispatch

import polib

from transpyler import lib
from transpyler.utils.string import normalize_docstring
from .decorators import synonyms as _synonyms
from .namespaces import collect_synonyms, collect_mod_namespace

I10N_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'l10n')
PO_HEADER = """#
msgid ""
msgstr ""
"Project-Id-Version: \\n"
"Language: %s\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""


#
# Gettext utilities
#
def gettext_for(lang):
    """
    Return a GNUTranslation class for the given language.

    Example:
        >>> trans = gettext_for('pt_BR')
        >>> _ = trans.gettext
        >>> _('hello world!')                                   # doctest: +SKIP
        'olá mundo!'
    """
    lang = lang.replace('-', '_')

    try:
        with open(os.path.join(I10N_PATH, lang + '.mo'), 'rb') as F:
            result = gettext.GNUTranslations(F)
    except FileNotFoundError:
        result = gettext.NullTranslations()
    return result


def create_pot_file(translations, path=None):
    """
    Save contents on a POT file from a dictionary of (id, string) translation
    pairs.

    It interprets the id as a comment in the POT file and the string is the
    msgid field. The msgstr field is always empty.
    """

    pot = polib.POFile()
    pot.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'fabiomacedomendes@gmail.com',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }

    # We keep a dictionary from msgids's to comments in order to keep all
    # entries unique. Duplicate entries simply duplicate comments
    entries = {}
    for key, data in translations.items():
        entry = polib.POEntry(msgid=data, comment=key)
        if data in entries:
            entries[data].comment += '\n' + key
        else:
            entries[data] = entry
            pot.append(entry)
    if path:
        pot.save(path)
    return pot


#
# Extract translations: these functions generate a .pot file from a python
# module
#
def extract_translations(namespace):
    """
    Extract all translation strings from namespace.

    Return a dictionary mapping ids to their corresponding values. The values
    would typically be inserted in a POT file. Translators would then generate
    PO files for each desired language.

    >>> extract_translations(ns)                                # doctest: +SKIP
    {
        'cos.name': 'cos',
        'cos.args': 'x',
        'cos.doc': 'Returns the cosine of a number',
        ...
    }

    Notes:
        If the namespace have a 'TRANSLATIONS' key mapping to a dictionary,
        it is used to update the result. The contents of TRANSLATIONS override
        any translation string computed automatically.
    """
    result = OrderedDict()
    extra_translations = namespace.get('TRANSLATIONS', {})

    for k, v in namespace.items():
        if k.startswith('_') or k == 'TRANSLATIONS':
            continue

        translations = extract_translation(v)
        if translations:
            for name, st in translations.items():
                name = name if name.startswith(':') else '.' + name
                result[k + name] = st
        else:
            result[k] = k

    result.update(extra_translations)
    return result


@singledispatch
def extract_translation(obj):
    """
    Returns a dictionary mapping paths inside a single object to translatable
    strings. If there is nothing to translate, it returns an empty dict.
    """

    # Objects that define __name__, __doc__ and __synonyms__
    result = OrderedDict()

    if hasattr(obj, '__name__'):
        result['name'] = obj.__name__
        for syn in getattr(obj, '__synonyms__', ()):
            result['name'] += '\n' + syn

    if hasattr(obj, '__doc__') and obj.__doc__:
        result['doc'] = normalize_docstring(obj.__doc__)

    return result


@extract_translation.register(types.FunctionType)
def _(obj):
    result = extract_translation.dispatch(object)(obj)
    vars = obj.__code__.co_varnames
    if vars:
        result['args'] = ', '.join(vars)
    return result


@extract_translation.register(type)
def _(obj):
    result = extract_translation.dispatch(object)(obj)

    for attr in dir(obj):
        if attr.startswith('_'):
            continue
        method = getattr(obj, attr, None)

        if isinstance(method, types.FunctionType):
            trans = extract_translation(method)
            for k, v in trans.items():
                result[':%s.%s' % (attr, k)] = v
        else:
            result[':%s' % attr] = attr

    return result


#
# Translate objects: these functions produce translated versions of
# modules/namespaces from a given translation .po file.
#
def translate_mod(lang, mod=lib, path='', synonyms=True,
                  add_unaccented=True, keep_old=True):
    """
    Translates a module and register the translation in the given sys.modules
    path.

    Examples:
        >>> translate_mod('pt_BR')
        <module 'lib'>

    Args:
        lang:
            The desired output language.
        mod:
            Optional module object. If not given, translates transpyler.lib.

    Returns:
        A module object.
    """

    new_mod = types.ModuleType(path or mod.__name__)
    namespace = translated_namespace(lang, mod,
                                     keep_old=keep_old,
                                     synonyms=synonyms,
                                     add_unaccented=add_unaccented)
    for k, v in namespace.items():
        setattr(new_mod, k, v)

    return new_mod


def translated_namespace(lang, mod=lib, synonyms=True, add_unaccented=True,
                         keep_old=True):
    """
    Return a namespace dict with the given ``lib``` module translated according
    to the request ``lang``.

    If no lib is given, uses the default transpyler.lib.
    """

    _ = gettext_for(lang).gettext
    obj_mapping = defaultdict(dict)
    ns = collect_mod_namespace(mod)
    strings = extract_translations(ns)
    strings = {tuple(k.split('.')): v for k, v in strings.items()}
    for k, v in strings.items():
        name, *args = k
        if v:
            obj_mapping[name]['.'.join(args)] = _(v)

    # Create namespace
    namespace = dict(mod.__dict__) if keep_old else {}
    for k, v in obj_mapping.items():
        name = _(k).partition('\n')[0].strip()
        namespace[name] = translate(k, v)

    # Add synonyms and unaccented versions
    if synonyms:
        extra = collect_synonyms(namespace, add_unaccented=add_unaccented)
        namespace.update(extra)
    return namespace


@singledispatch
def translate(name, data):
    """
    Translate object using a dictionary of (attr, translation) pairs.
    """

    # FIXME: handle class:method names properly
    try:
        value = getattr(lib, name)
    except AttributeError:
        return data
    try:
        return translate(value, data)
    except TypeError:
        return value


@translate.register(types.FunctionType)
def _(func, data: dict):
    """
    Return a translated version of func.
    """

    names = data['name'].strip().splitlines()
    name, *synonyms = names
    varnames = tuple(map(str.strip, data.get('args', '').split(',')))
    varnames = tuple(x for x in varnames if x)
    assert len(varnames) == len(func.__code__.co_varnames), \
        '%s: size of argument names list changed during translation (from %s ' \
        'to %s)' % (name, func.__code__.co_varnames, varnames)

    #
    # Copy the code object and change the varnames parameter
    # (Not for the faint of heart)
    #
    # code(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
    #  constants, names, varnames, filename, name, firstlineno,
    #  lnotab[, freevars[, cellvars]])
    #
    code = func.__code__
    new_code = types.CodeType(
        code.co_argcount, code.co_kwonlyargcount, code.co_nlocals,
        code.co_stacksize, code.co_flags, code.co_code, code.co_consts,
        code.co_names, varnames, code.co_filename, code.co_name,
        code.co_firstlineno, code.co_lnotab, code.co_freevars,
        code.co_cellvars
    )

    # Create a function copy
    translated = types.FunctionType(
        new_code,
        func.__globals__,
        name=name,
        argdefs=func.__defaults__,
        closure=func.__closure__
    )
    translated.__dict__.update(func.__dict__)
    translated.__doc__ = data.get('doc', '')
    translated.__kwdefaults__ = func.__kwdefaults__
    return _synonyms(*synonyms)(translated)


@translate.register(type)
def _(cls: type, data: dict):
    """
    Extend class with translated method.

    Changes the name and other parameters *inplace*.
    """
    return cls


#
# Automatic translations
#
def google_translate(lang, verbose=True, prompt=True):
    """
    Fill translations for the given PO file using google translate.
    """
    from textblob import TextBlob as Blob
    from textblob.exceptions import NotTranslated

    # Utility functions
    echo = print \
        if verbose or prompt else lambda *args, **kwargs: None
    showline = lambda: print('\n' + '-' * 40) \
        if verbose or prompt else lambda: None
    ask = lambda: input('\nTranslate? [Y/n]').lower() in ('y', '') \
        if prompt else lambda: True

    # Prepare
    google_lang = lang.replace('_', '-')
    popath = os.path.join(I10N_PATH, lang + '.po')
    if os.path.exists(popath):
        echo('Loading file: %r' % popath, '\n\n')
        pofile = polib.pofile(popath)
    else:
        echo('Creating file: %r' % popath, '\n\n')
        with open(popath, 'w', encoding='utf-8') as F:
            F.write(PO_HEADER % lang.replace('-', '_'))

            potpath = os.path.join(I10N_PATH, 'transpyler.pot')
            with open(potpath, encoding='utf8') as Fpot:
                save = False
                for line in Fpot.readlines():
                    if save:
                        F.write(line)
                    elif line.isspace():
                        save = True

        pofile = polib.pofile(popath)

    # Translator functions
    def gtranslate(x):
        if not x:
            return ''
        try:
            result = '%s' % Blob(x).translate('en', google_lang)
        except NotTranslated:
            result = x

        if x[0].isupper():
            return result
        else:
            return result[0].lower() + result[1:]

    def translate(text, id):
        map = {
            'doc': translate_doc,
            'name': translate_name,
            'args': translate_args,
        }
        return map.get(id, gtranslate)(text)

    def translate_doc(text):
        sections = []
        for section in split_docstring(text):
            translated = gtranslate(section)
            sections.append(translated)
        return '\n\n'.join(map(lambda x: '%s' % x, sections))

    def translate_name(name):
        translated = gtranslate(name.replace('_', ' '))
        if name.islower():
            translated = translated.lower()
        elif name[0].islower():
            translated = translated[0].lower() + translated[1:]
        return translated.replace(' ', '_').replace('-', '_')

    def translate_args(text):
        return ', '.join(map(translate_name, text.split(',')))

    # Mainloop: handle all missing translations and pass them to google
    # translate
    for entry in pofile:
        if entry.msgstr:
            continue

        echo('\n'.join('#. ' + line for line in entry.comment.splitlines()))
        echo(entry.msgid)
        if ask():
            id = entry.comment.rpartition('.')[-1]
            entry.msgstr = translate(entry.msgid, id)
            entry.flags.append('fuzzy')

            # Show message
            showline()
            echo('\nTRANSLATION\n')
            echo(entry.msgstr)
            showline()

            # Save
            pofile.save()


def split_docstring(text):
    """
    Split docstring in several sections.
    """

    parts = ['']
    text = normalize_docstring(text)
    parts[0], *lines = text.splitlines()

    for line in lines:
        if not line:
            parts.append('')
        elif line.startswith(' '):
            parts[-1] += '\n' + line
        elif parts[-1] == '':
            parts[-1] += line
        else:
            parts[-1] += ' ' + line

    return parts
