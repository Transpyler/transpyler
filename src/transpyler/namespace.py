from collections.abc import Mapping

from .translate import translate_namespace, translator_factory
from .utils import extract_namespace, pretty_callable


class Namespace(Mapping):
    @property
    def namespace(self):
        if self._namespace is None:
            self._namespace = namespace(self.transpyler)
        return self._namespace

    def __init__(self, transpyler):
        self.transpyler = transpyler
        self._namespace = None

    def __len__(self):
        return len(self.namespace)

    def __iter__(self):
        return iter(self.namespace)

    def __getitem__(self, key):
        return self.namespace[key]


def namespace(transpyler):
    ns = global_functions(transpyler)

    # Load turtle functions
    if transpyler.has_turtle_functions and transpyler.turtle_backend:
        turtle_ns = turtle_functions(transpyler.turtle_backend)
        ns.update(turtle_ns)

    # Load special functions
    ns['exit'] = exit_function(transpyler.exit_callback, transpyler.translate)

    # Load default translations from using the lang option
    if transpyler.lang:
        translated = translate_namespace(ns, transpyler.lang)
        ns.update(translated)

    return ns


def global_functions(transpyler):
    """
    Return a dictionary with the default global namespace for the
    transpyler runtime.
    """
    from . import lib

    ns = extract_namespace(lib)
    return ns


def turtle_functions(backend):
    """
    Return a dictionary with all turtle-related functions.
    """

    if backend == 'tk':
        from .turtle.tk import make_turtle_namespace

        ns = make_turtle_namespace()
    elif backend == 'qt':
        from .turtle.qt import make_turtle_namespace

        ns = make_turtle_namespace()
    else:
        raise ValueError('invalid backend: %r' % backend)

    return ns


#
# Special functions
#
def exit_function(function, translate=translator_factory('en')):
    """
    Wraps the exit function into a callable object that prints a nice
    message for its repr.
    """

    @pretty_callable(translate('exit.doc'))
    def exit():
        return function()

    exit.__name__ = translate('exit.name')
    exit.__doc__ = translate('exit.doc')
    return exit
