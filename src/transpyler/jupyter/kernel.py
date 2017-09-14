import importlib
from ast import PyCF_ONLY_AST

from IPython.core.compilerop import CachingCompiler
from IPython.utils import py3compat
from ipykernel.ipkernel import IPythonKernel
from lazyutils import lazy
from traitlets import Type

from .shell import TranspylerShell
from transpyler.utils import with_transpyler_attr


class TranspylerKernel(IPythonKernel):
    """
    A meta kernel based backend to use Transpyled languages in Jupyter/iPython.
    """

    transpyler = None
    implementation = lazy(lambda self: 'i' + self.transpyler.name)
    implementation_version = lazy(lambda self: self.transpyler.version)
    language = lazy(lambda self: self.transpyler.name)
    language_version = lazy(lambda self: self.transpyler.language_version)
    banner = lazy(lambda self: self.transpyler.console_banner())
    language_info = lazy(lambda self: self.transpyler.info.get_language_info())
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
    Start Jupyter kernel.
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
    transpyler_class_name = sys.argv.pop(idx)
    path, _, name = transpyler_class_name.rpartition('.')
    transpyler_class = getattr(importlib.import_module(path), name)
    start_kernel(transpyler_class())
