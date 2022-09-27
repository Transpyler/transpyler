"""
This module is not imported by the user, but rather it generates translation
strings for transpyler functions.
"""

import types
from collections import defaultdict
from functools import singledispatch

from .extract import extract_translations
from .gettext import gettext_for
from ..utils.decorators import synonyms as _synonyms
from ..utils.namespaces import collect_synonyms


def translate_namespace(ns, lang, synonyms=True, add_unaccented=True):
    """
    Return a dict with the given namespace translated according to the
    requested ``lang``.
    """

    _ = gettext_for(lang).gettext
    translation_data = defaultdict(dict)
    translation_strings = extract_translations(ns)
    for name, value in translation_strings.items():
        # Translate methods in a class
        if ':' in name:
            classname, method = name.split(':')
            name, sep, post = method.partition('.')
            class_dict = translation_data[classname]
            method_dict = class_dict.setdefault(name, {})
            method_dict[post] = _(value)

        # Translate a function or regular object
        else:
            name, sep, post = name.partition('.')
            translation_data[name][post] = _(value)

    # Create namespace
    namespace = dict(ns)
    for name, data in translation_data.items():
        if name not in ns:
            continue
        obj = ns[name]
        translated_name = _(name).partition('\n')[0].strip()
        namespace[translated_name] = apply_translations(obj, data)

    # Add synonyms and unaccented versions
    if synonyms:
        extra = collect_synonyms(namespace, add_unaccented=add_unaccented)
        namespace.update(extra)
    return namespace


@singledispatch
def apply_translations(obj, data):
    """
    Translate object by applying translation data to object.
    """
    return obj


@apply_translations.register(types.FunctionType)
def apply_translations_function(func, data: dict):
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
        code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount, code.co_nlocals,
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


@apply_translations.register(type)
def apply_translations_type(cls: type, data: dict):  # noqa: F811
    """
    Extend class with translated method.

    Changes the name and other parameters *inplace*.
    """

    return cls


def translator_factory(lang):
    """
    Return a translator function that receives a string and return a translated
    version using gettext.
    """
    gettext = gettext_for(lang)
    return gettext.gettext
