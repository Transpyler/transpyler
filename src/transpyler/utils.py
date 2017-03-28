import functools
import re

from unidecode import unidecode

__all__ = [
    # Remove accents
    'unidecode',

    # Handle synonyms
    'synonyms', 'collect_synonyms', 'register_synonyms',

    # Other decorators
    'normalize_accented_keywords',

    # Utility functions
    'keep_spaces',
]

HEADING_SPACE = re.compile(r'^\s*')
ENDING_SPACE = re.compile(r'\s*$')
SYNONYM_ERROR_MSG = '%s is present in namespace, but is also a synonym of %s'


def synonyms(*args):
    """
    Decorator that marks synonyms of a function name.
    """

    fmt_args = ['**%s**' % x for x in args]

    def decorator(func):
        if len(args) == 1:
            data = fmt_args[0]
        else:
            data = ', '.join(fmt_args[:-1])
            data += ' ou ' + fmt_args[-1]

        func.__synonyms__ = args
        func.__doc__ += (
            '\n\n'
            'Notes\n'
            '-----\n\n'
            'Também pode ser chamada como ' + data)
        return func

    return decorator


def collect_synonyms(namespace, add_unaccented=True):
    """
    Return a dictionary with all synonyms found in the given namespace.

    Raise a ValueError for name conflicts.
    """

    map = {}
    map.update(collect_aliases(namespace))
    if add_unaccented:
        map.update(collect_unaccented(namespace))
    return map


def collect_unaccented(namespace):
    map = {}
    unaccent = unidecode
    for name, func in list(map.items()):
        no_accent = unaccent(name)
        if no_accent != name:
            if no_accent in map:
                raise ValueError(SYNONYM_ERROR_MSG % (no_accent, name))
            map[no_accent] = func
    return map


def collect_aliases(namespace):
    map = {}
    for attr, func in namespace.items():
        try:
            for alias in func.__synonyms__:
                map[alias] = func
                if alias in namespace:
                    raise ValueError(SYNONYM_ERROR_MSG % (alias, attr))
        except AttributeError:
            continue
    return map


def register_synonyms(global_ns):
    """
    Register all synonyms in the given namespace dictionary.
    """

    D = collect_synonyms(global_ns)
    global_ns.update(D)


def normalize_accented_keywords(func):
    """
    Decorate function so all accented keywords are passed unaccented to the
    real implementation.
    """

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        decode = unidecode
        kwargs = {decode(k): v for (k, v) in kwargs.items()}
        return func(*args, **kwargs)

    return decorated


def keep_spaces(result, src):
    """
    Keep the same number of heading and trailing whitespace in result as
    compared to src.

    Example:
        >>> keep_spaces(' foo', 'bar\n\n')
        'foo\n\n'
    """

    if not src:
        return result.strip()

    # Find head and tail
    head = tail = ''
    if src[0].isspace():
        head = HEADING_SPACE.search(src).group()
    elif head == src:
        head, tail = '', head
    if src[-1].isspace():
        tail = ENDING_SPACE.search(src).group()
    return head + result.strip() + tail
