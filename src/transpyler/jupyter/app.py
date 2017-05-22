import os

from jupyter_client import KernelManager
from jupyter_console.app import ZMQTerminalIPythonApp
from jupyter_console.ptshell import ZMQTerminalInteractiveShell


class TranspylerMixin:
    transpyler = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.transpyler is None:
            raise ValueError('did not set transpyler instance')


class TranspylerKernelManager(TranspylerMixin, KernelManager):
    """
    Default kernel manager for transpyler apps.
    """
    kernel_script_path = os.path.join(os.path.dirname(__file__), 'kernel.py')
    kernel_name = property(lambda self: self.transpyler.name)


class ZMQTerminalTranspylerApp(TranspylerMixin, ZMQTerminalIPythonApp):
    """
    A Transpyler terminal app.
    """

    name = 'transpyler'


# ZMQTerminalInteractiveShell class. It is a singleton, hence we don't expect
# problems.
#
# These hacks customize the messages shown during shell initialization.
def monkey_patch():
    def show_banner(self):
        print(self.kernel_info.get('banner', ''))

    ZMQTerminalInteractiveShell.show_banner = show_banner


monkey_patch()
