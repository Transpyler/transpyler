import importlib
from ast import PyCF_ONLY_AST

from IPython.core.compilerop import CachingCompiler
from IPython.utils import py3compat
from ipykernel.ipkernel import IPythonKernel
from ipykernel.zmqshell import ZMQInteractiveShell
from lazyutils import lazy
from traitlets import Type

from transpyler.utils import with_transpyler_attr
from transpyler.transpyler import get_transpyler_from_name


class TranspylerShell(ZMQInteractiveShell):
    """
    A IPython based shell for transpyled languages.

    A shell is used by the kernel to interact with code.
    """

    @lazy
    def transpyler(self):
        return self.parent.transpyler

    def init_user_ns(self):
        """
        Additional symbols for the shell environment.
        """

        super().init_user_ns()
        ns = self.user_ns
        self.transpyler.update_user_ns(ns)

    def ex(self, cmd):
        return super().ex(self.transpyler.transpile(cmd))

    def ev(self, cmd):
        return super().ev(self.transpyler.transpile(cmd))


class TranspylerKernel(IPythonKernel):
    """
    A meta kernel based backend to use Transpyled languages in Jupyter/iPython.
    """

    transpyler = None

    @lazy
    def implementation(self):
        return 'i' + self.transpyler.name

    @lazy
    def implementation_version(self):
        return self.transpyler.version

    @lazy
    def language(self):
        return self.transpyler.name

    @lazy
    def language_version(self):
        return self.transpyler.language_version

    @lazy
    def banner(self):
        return self.transpyler.get_console_banner()

    @lazy
    def language_info(self):
        transpyler = self.transpyler
        return {
            'mimetype': transpyler.mimetype,
            'file_extension': transpyler.file_extension,
            'codemirror_mode': {
                "version": 3,
                "name": "ipython"
            },
            'pygments_lexer': 'python',
        }

    shell_class = Type(TranspylerShell)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.transpyler is None:
            raise ValueError('transpyler was not defined')
        monkey_patch(self.transpyler)
        self.transpyler.init()

    def do_execute(self, code, *args, **kwargs):
        code = self.transpyler.transpile(code)
        return super().do_execute(code, *args, **kwargs)

    def do_is_complete(self, code):
        return super().do_is_complete(self.transpyler.transpile(code))


def start_kernel(transpyler):
    """
    Start Pytuga Jupyter kernel.
    """

    from ipykernel.kernelapp import IPKernelApp

    kernel_class = with_transpyler_attr(TranspylerKernel, transpyler)
    IPKernelApp.launch_instance(kernel_class=kernel_class)


# We mokey-patch a few modules and functions to replace Python's compile
# function with pytuga's version. This is potentially fragile, but it seems to
# work well so far.
def monkey_patch(transpyler):
    def ast_parse(self, source, filename='<unknown>', symbol='exec'):
        flags = self.flags | PyCF_ONLY_AST
        return transpyler.compile(source, filename, symbol, flags, 1)

    CachingCompiler.ast_parse = ast_parse
    py3compat.compile = transpyler.compile


# Find correct transpyler instance from argv and execute start_kernel
if __name__ == '__main__':
    import sys

    idx = sys.argv.index('--type')
    sys.argv.pop(idx)
    transpyler_class = sys.argv.pop(idx)
    path, _, name = transpyler_class.rpartition('.')
    transpyler_class = getattr(importlib.import_module(path), name)
    start_kernel(get_transpyler_from_name(transpyler_class))
