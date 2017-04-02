import os

from jupyter_client import KernelManager
from jupyter_console.app import ZMQTerminalIPythonApp
from jupyter_console.ptshell import ZMQTerminalInteractiveShell


class TranspylerKernelManager(KernelManager):
    transpyler = None

    @property
    def kernel_name(self):
        return self.transpyler.name

    @property
    def kernel_script_path(self):
        return os.path.join(os.path.dirname(__file__), 'kernel.py')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.transpyler is None:
            raise ValueError('did not set transpyler instance')


class ZMQTerminalTranspylerApp(ZMQTerminalIPythonApp):
    """
    A Transpyler terminal app.
    """

    transpyler = None
    name = 'transpyler'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.transpyler is None:
            raise ValueError('did not set transpyler instance')


# ZMQTerminalInteractiveShell class. It is a singleton, hence we don't expect
# problems.
#
# These hacks customize the messages shown during shell initialization.
def monkey_patch():
    def show_banner(self):
        print(self.kernel_info.get('banner', ''))

    ZMQTerminalInteractiveShell.show_banner = show_banner


monkey_patch()
