import builtins as _builtins
from types import ModuleType

from lazyutils import lazy


class Introspection:
    """
    Introspection facilities for a transpyled Transpyler.
    """

    #
    # Original python names and constants
    #
    py_constants = ['True', 'False', 'None']

    @lazy
    def py_exceptions(self):
        return [
            name for (name, value) in vars(_builtins).items()
            if isinstance(value, type) and issubclass(value, Exception)
        ]

    @lazy
    def py_types(self):
        return [
            name for (name, value) in vars(_builtins).items()
            if isinstance(value, type) and not issubclass(value, Exception)
        ]

    @lazy
    def py_functions(self):
        return [
            name for (name, value) in vars(_builtins).items()
            if name not in self.py_types and name not in self.py_exceptions
        ]

    @lazy
    def py_builtins(self):
        return self.py_types + self.py_functions

    py_submodules = []
    py_keywords = []

    #
    # Names derived from the transpyler
    #
    namespace = lazy(lambda self: self.transpyler.namespace)
    all_names = lazy(lambda self: list(self.namespace))
    constants = lazy(
        lambda self:
        [name for (name, value) in self.namespace.items()
         if isinstance(value, (int, float, bool))]
    )
    exceptions = lazy(
        lambda self:
        [name for (name, value) in self.namespace.items()
         if isinstance(value, type) and issubclass(value, Exception)]
    )
    types = lazy(
        lambda self:
        [name for (name, value) in self.namespace.items()
         if isinstance(value, type) and not issubclass(value, Exception)]
    )
    functions = lazy(
        lambda self:
        [name for (name, value) in self.namespace.items()
         if not isinstance(value, type) and callable(value)]
    )
    submodules = lazy(
        lambda self:
        [name for (name, value) in self.namespace.items()
         if isinstance(value, ModuleType)]
    )
    builtins = lazy(lambda self: self.functions + self.types)
    keywords = []

    #
    # Combined lists
    #
    all_constants = lazy(
        lambda self: unique(self.constants + self.py_constants)
    )
    all_exceptions = lazy(
        lambda self: unique(self.exceptions + self.py_exceptions)
    )
    all_types = lazy(
        lambda self: unique(self.types + self.py_types)
    )
    all_functions = lazy(
        lambda self: unique(self.functions + self.py_functions)
    )
    all_submodules = lazy(
        lambda self: unique(self.submodules + self.py_submodules)
    )
    all_builtins = lazy(
        lambda self: unique(self.builtins + self.py_builtins)
    )
    all_keywords = lazy(
        lambda self: unique(self.keywords + self.py_keywords)
    )

    def __init__(self, transpyler):
        self.transpyler = transpyler


def unique(lst):
    out = []
    for x in lst:
        if x not in out:
            out.append(x)
    return out
