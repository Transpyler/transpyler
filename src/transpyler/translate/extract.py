import types
from collections import OrderedDict
from functools import singledispatch

from ..utils import normalize_docstring


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
def extract_translation_function(obj):
    result = extract_translation.dispatch(object)(obj)
    vars = obj.__code__.co_varnames
    if vars:
        result['args'] = ', '.join(vars)
    return result


@extract_translation.register(type)
def extract_translation_type(obj):
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
