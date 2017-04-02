import contextlib
import builtins as _builtins
import importlib

from lazyutils import lazy


class Builtins:
    """
    Manage the builtin functions for the new transpyler.
    """

    @lazy
    def modules(self):
        try:
            return list(self.transpyler.builtin_modules)
        except (AttributeError, TypeError):
            return []

    @lazy
    def _namespace(self):
        ns = {}
        for mod in self.modules:
            mod = importlib.import_module(mod)
            for name in dir(mod):
                if name.startswith('_') or name.isupper():
                    continue
                ns[name] = getattr(mod, name)
        return ns

    def __init__(self, transpyler=None):
        self.transpyler = transpyler

    def get_namespace(self):
        """
        Return a dictionary with all public functions.
        """

        return dict(self._namespace)

    def update(self, *args, **kwargs):
        """
        Update builtins with new functions.
        """

        ns = self._namespace
        ns.update(*args, **kwargs)

    def load_as_builtins(self):
        """
        Load all registered builtin functions as Python's builtins.
        """

        for k, v in self.get_namespace().items():
            setattr(_builtins, k, v)

    @contextlib.contextmanager
    def restore_after(self):
        """
        Apply current builtins to Python's builtins module and restore
        state afterwards.
        """

        old_builtins = vars(_builtins)
        new_builtins = self.get_namespace()

        for k, v in new_builtins.items():
            setattr(_builtins, k, v)

        try:
            yield
        finally:
            for k in dir(_builtins):
                if k in new_builtins:
                    if k in old_builtins:
                        setattr(_builtins, k, old_builtins[k])
                    else:
                        delattr(_builtins, k)
