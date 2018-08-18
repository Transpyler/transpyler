from ipykernel.zmqshell import ZMQInteractiveShell
from lazyutils import lazy


class TranspylerShell(ZMQInteractiveShell):
    """
    A IPython based shell for transpyled languages.

    A shell is used by the kernel to interact with code.
    """

    @lazy
    def transpyler(self):
        return self.parent.transpyler

    def init_user_ns(self):
        super().init_user_ns()
        self.transpyler.exit_callback = self.exiter

    def init_create_namespaces(self, user_module=None, user_ns=None):
        super().init_create_namespaces(user_module, user_ns)

        ns = self.transpyler.namespace
        self.user_ns.update(ns)
        self.user_global_ns.update(ns)
        self.user_module.__dict__.update(ns)

    def ex(self, cmd):
        return super().ex(self.transpyler.transpile(cmd))

    def ev(self, cmd):
        return super().ev(self.transpyler.transpile(cmd))
