import functools
from gettext import gettext as _

from unidecode import unidecode

def synonyms(*args, api_function=True):
    """
    Decorator that marks synonyms/aliases of a function.

    Examples:

        .. code-block:: python

            @synonyms('fd', 'fwd')
            def forward(x):
                print('go forward')
    """

    fmt_args = [':func:`%s`' % x for x in args]

    def decorator(func):
        synonyms = getattr(func, '__synonyms__', ())
        func.__synonyms__ = tuple(synonyms) + args

        if hasattr(func, '__doc__'):
            data = ', '.join(fmt_args[:])
            func.__doc__ = \
                (func.__doc__ or '') + \
                ('\n\n'
                 'Notes:\n'
                 '    %s: %s') % (_('Synonyms'), data)

        if api_function:
            func = is_api_function(func)

        return func

    return decorator


def is_api_function(func):
    """
    Decorator that marks a function as a public API function for a transpyled
    language.
    """

    func._is_api_function = True
    return func


def normalize_accented_keywords(func):
    """
    Decorator that remove accents from keyword names and pass unaccented
    versions to the implementation function.
    """

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        decode = unidecode
        kwargs = {decode(k): v for (k, v) in kwargs.items()}
        return func(*args, **kwargs)

    return decorated


#
# Make objects that execute code with side effects with a simple call of repr()
# This is useful in the terminal to implement "commands" such as exit
#
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
