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
    'keep_spaces', 'pretty_callable', 'with_transpyler_attr',
]

HEADING_SPACE = re.compile(r'^\s*')
ENDING_SPACE = re.compile(r'\s*$')
SYNONYM_ERROR_MSG = '%s is present in get_namespace, but is also a synonym of %s'


def synonyms(*args):
    """
    Decorator that marks synonyms of a function name.
    """

    fmt_args = ['**%s**' % x for x in args]

    def decorator(func):
        data = ', '.join(fmt_args[:])
        func.__synonyms__ = args
        func.__doc__ = (func.__doc__ or '') + (
            '\n\n'
            'Notes\n'
            '-----\n\n'
            'Sinônimos: ' + data)
        return func

    return decorator


def collect_synonyms(namespace, add_unaccented=True):
    """
    Return a dictionary with all synonyms found in the given get_namespace.

    Raise a ValueError for name conflicts.
    """

    map = {}
    map.update(collect_aliases(namespace))
    if add_unaccented:
        map.update(collect_unaccented(map))
    return map


def collect_unaccented(namespace):
    map = {}
    for name, func in list(namespace.items()):
        no_accent = unidecode(name)
        if no_accent != name:
            map.setdefault(no_accent, func)
    return map


def collect_aliases(namespace):
    map = {}
    for attr, func in namespace.items():
        try:
            for alias in func.__synonyms__:
                map.setdefault(alias, func)
        except AttributeError:
            continue
    return map


def register_synonyms(global_ns, add_unaccented=True):
    """
    Register all synonyms in the given get_namespace dictionary.
    """

    D = collect_synonyms(global_ns, add_unaccented=add_unaccented)
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
    if src[-1].isspace():
        tail = ENDING_SPACE.search(src).group()
    return head + result.strip() + tail


def full_class_name(cls):
    """
    Return the full class name prepending module paths.
    """

    return '%s.%s' % (cls.__module__, cls.__name__)


class PrettyCallable:
    """
    Callable that whose repr() is a given message.
    """

    def __init__(self, func, name=None, doc=None, str=None,
                 autoexec=False, autoexec_message=None):
        self.__func = func
        self.__autoexec = autoexec
        self.__autoexec_message = autoexec_message
        self.__repr = str or 'please call %s()' % self.__name__

    def __call__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)

    def __repr__(self):
        if self.__autoexec:
            self.__func()
            return self.__autoexec_message or ''
        return self.__repr

    def __getattr__(self, attr):
        return getattr(self.__func, attr)


def pretty_callable(str=None, **kwargs):
    """
    Decorate function to be a pretty callable.

    Example:
        >>> @pretty_callable('call exit() to finish interactive shell')
        ... def exit():
        ...     raise SystemExit
    """

    def decorator(func):
        return PrettyCallable(func, str=str, **kwargs)

    return decorator


def with_transpyler_attr(cls, transpiler):
    """
    Return a subclass with the transpyler attribute defined.
    """

    return type(cls.__name__, (cls,), {'transpyler': transpiler})
