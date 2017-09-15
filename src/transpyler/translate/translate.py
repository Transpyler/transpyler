"""
This module is not imported by the user, but rather it generates translation
strings for transpyler functions.
"""

import types
from collections import defaultdict
from functools import singledispatch

from transpyler import lib
from .extract import extract_translations
from .gettext import gettext_for
from ..utils.decorators import synonyms as _synonyms
from ..utils.namespaces import collect_synonyms, collect_mod_namespace


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
    namespace = translate_namespace(lang, mod,
                                    keep_old=keep_old,
                                    synonyms=synonyms,
                                    add_unaccented=add_unaccented)
    for k, v in namespace.items():
        setattr(new_mod, k, v)

    return new_mod


def translate_namespace(lang, mod=lib, synonyms=True, add_unaccented=True,
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
        namespace[name] = translate_object(k, v)

    # Add synonyms and unaccented versions
    if synonyms:
        extra = collect_synonyms(namespace, add_unaccented=add_unaccented)
        namespace.update(extra)
    return namespace


@singledispatch
def translate_object(name, data):
    """
    Translate object using a dictionary of (attr, translation) pairs.
    """

    # FIXME: handle class:method names properly
    try:
        value = getattr(lib, name)
    except AttributeError:
        return data
    try:
        return translate_object(value, data)
    except TypeError:
        return value


@translate_object.register(types.FunctionType)
def translate_function(func, data: dict):
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


@translate_object.register(type)
def translate_type(cls: type, data: dict):  # noqa: F811
    """
    Extend class with translated method.

    Changes the name and other parameters *inplace*.
    """
    return cls
