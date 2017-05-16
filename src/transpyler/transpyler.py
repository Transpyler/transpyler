import builtins as _builtins
import codeop

import click
from lazyutils import lazy

from transpyler.utils.utils import has_qt
from .builtins import Builtins
from .language_info import LanguageInfo
from .lexer import Lexer

# Save useful builtin functions
_compile = _builtins.compile
_exec = _builtins.exec
_eval = _builtins.eval
_input = _builtins.input
_print = _builtins.print

INSTANCES_FOR_NAME = {}


class Transpyler:
    """
    Base class for all new Transpylers.

    Very simple Python variations can be created by subclassing Transpyler::

        class PyBr(Transpyler):
            translations = {
                'para': 'for',            # single token translations
                'em': 'in',
                ('para', 'cada'): 'for',  # token sequence translations
                ('faça', ':'): ':',
            }

    Now we can create an object with exec(), eval() and compile() functions that
    handle the newly defined transpyler:

        pybr = PyBr()
        global_ns = {}

        pybr.exec('''
        x, y = 1, 1
        para cada i em [1, 2, 3, 4, 5] faça:
            x, y = y, x + y
        ''', global_ns)

        assert globals_ns['x'] == 8
        assert globals_ns['y'] == 13
    """

    # Cache builtins
    _compile = _compile
    _exec = _exec
    _eval = _eval
    _input = _input
    _print = _print

    # Subclasses
    lexer_factory = Lexer
    builtins_factory = Builtins

    # Constants
    i10n_lang = None
    standard_lib = None
    translations = None
    invalid_tokens = None
    language_version = '0.1.0'
    version = '0.1.0'
    codemirror_mode = 'python'
    file_extension = 'py'
    builtin_modules = ()

    # Language info
    info_factory = LanguageInfo
    info = lazy(lambda self: self.info_factory(self))
    mimetype = lazy(lambda self: 'text/x-%s' % self.name)
    mimetypes = lazy(lambda self: [self.mimetype])

    # Computed constants
    display_name = lazy(lambda self: self.name.title().replace('_', ' '))
    lexer = lazy(lambda self: self.lexer_factory(self))
    builtins_manager = lazy(lambda self: self.builtins_factory(self))
    short_banner = lazy(lambda self: self.display_name)
    _namespace_cache = lazy(lambda self: self.get_builtins_namespace())

    @lazy
    def name(self):
        cls_name = self.__class__.__name__.lower()
        if cls_name == 'Transpyler':
            raise AttributeError('must define a .name attribute')
        elif cls_name.endswith('transpyler'):
            return cls_name[:-10]
        else:
            return cls_name

    def __init__(self, **kwargs):
        self._forbidden = False
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._has_init = False

        # Check validity
        if self.name is None:
            raise ValueError('Transpyler requires a "name" attribute.')

        # Save instance in instance dictionary
        if self.name not in INSTANCES_FOR_NAME:
            INSTANCES_FOR_NAME[self.name] = self
        if type(self) not in INSTANCES_FOR_NAME:
            INSTANCES_FOR_NAME[type(self)] = self
        if type(self).__module__ not in INSTANCES_FOR_NAME:
            path = type(self).__module__
            while path:
                INSTANCES_FOR_NAME[path] = self
                path, _, _ = path.rpartition('.')

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.name)

    def update_user_ns(self, ns):
        """
        Update user global_namespace that is initialized when a transpyler starts an
        interactive shell.

        This function should be overriden by subclasses. It receives the current
        global_namespace and should update it inplace.
        """

    def init(self, extra_builtins=None, curses=True, apply_builtins=True):
        """
        Initializes transpyler runtime.

        Args:
            curses:
                Load curses that enable translation for builtin python types by
                hacking them at C-level.
            extra_builtins (dict):
                A dictionary with extra builtin functions to be added to the
                runtime.
        """

        if not self._has_init:
            if curses:
                self.apply_curses()
            self._has_init = True
        if extra_builtins:
            self.builtins_manager.update(extra_builtins)
        if apply_builtins:
            self.builtins_manager.load_as_builtins()

    def apply_curses(self):
        """
        Apply any required curses.

        Default implementation does nothing.
        """

    def compile(self, source, filename, mode, flags=0, dont_inherit=False,
                compile_function=None):
        """
        Similar to the built-in function compile() for Transpyled code.

        The additional compile_function() argument allows to define a function
        to replace Python's builtin compile().

        Args:
            source (str or code):
                Code to be executed.
            filename:
                File name associated with code. Use '<input>' for strings.
            mode:
                One of 'exec' or 'eval'. The second allows only simple
                statements that generate a value and is used by the eval()
                function.
            forbidden (bool):
                If true, initialize the forbidden lib functionality to enable
                i18n for Python builtins in C-level.
            compile_function (callable):
                A possible replacement for Python's built-in compile().
        """

        source = self.transpile(source)
        compile_function = compile_function or self._compile
        return compile_function(source, filename, mode, flags, dont_inherit)

    def exec(self, source, globals=None, locals=None, forbidden=False,
             exec_function=None, builtins=False, _builtins_to_globals=True):
        """
        Similar to the built-in function exec() for transpyled code.

        The additional exec_function() argument allows to define a function to
        replace Python's builtin compile().

        Args:
            source (str or code):
                Code to be executed.
            globals, locals:
                A globals/locals dictionary
            builtins (bool):
                If given, execute with builtins injected on Python's builtins
                module.
            forbidden (bool):
                If true, initialize the forbidden lib functionality to enable
                i18n for Python builtins in C-level.
            exec_function (callable):
                A possible replacement for Python's built-in exec().
        """

        if builtins:
            with self.builtins_manager.restore_after():
                return self.exec(source, globals, locals,
                                 forbidden=forbidden,
                                 _builtins_to_globals=False,
                                 exec_function=exec_function)

        exec_function = exec_function or _exec

        if globals is None:
            globals = _builtins.globals()
        if _builtins_to_globals:
            globals.update(self._namespace_cache)

        code = self.transpile(source) if isinstance(source, str) else source

        if locals is None:
            return exec_function(code, globals)
        else:
            return exec_function(code, globals, locals)

    def eval(self, source, globals=None, locals=None, forbidden=False,
             eval_function=None, builtins=False):
        """
        Similar to the built-in function eval() for transpyled code.

        The additional eval_function() argument allows to define a function to
        replace Python's builtin compile().

        Args:
            source (str or code):
                Code to be executed.
            globals, locals:
                A globals/locals dictionary
            builtins (bool):
                If given, update builtins with functions in tugalib.
            forbidden (bool):
                If true, initialize the forbidden lib functionality to enable
                i18n for Python builtins in C-level.
            eval_function (callable):
                A possible replacement for Python's built-in eval().
        """

        eval_function = eval_function or _eval
        return self.exec(source, globals, locals, forbidden=forbidden,
                         builtins=builtins, exec_function=eval_function)

    def transpile(self, src):
        """
        Convert source to Python.
        """

        return self.lexer.transpile(src)

    def is_incomplete_source(self, src, filename="<input>", symbol="single"):
        """
        Test if a given source code is incomplete.

        Incomplete code may appear in users interactions when user is typing a
        multi line command:

        for x in range(10):
            ... should continue here, but user already pressed enter!
        """

        pytuga_src = self.transpile(src)
        return codeop.compile_command(pytuga_src, filename, symbol) is None

    def get_console_banner(self, short=False):
        """
        Return a string with the console banner.
        """

        if short:
            return self.short_banner
        return getattr(self, 'banner', self.short_banner)

    def get_functions(self, module=None):
        """
        Return a namespace dictionary with the the exec/eval/compile/transpile
        functions.

        This is useful to expose on a module to offer a exec-like interface to
        users.
        """

        return {
            'exec': self.exec,
            'eval': self.eval,
            'compile': self.compile,
            'transpile': self.transpile,
        }

    def get_builtins_namespace(self):
        """
        Return a dictionary with the default builtins global_namespace for transpyler.
        """

        ns = self.builtins_manager.get_namespace()
        return ns

    def get_turtle_namespace(self, backend=None):
        """
        Return a dictionary with all turtle-related functions.
        """

        if backend == 'tk':
            from transpyler.turtle.tk import namespace

            return namespace()

        elif backend == 'qt':
            from transpyler.turtle.qt import namespace

            return namespace

        else:
            raise ValueError('invalid backend: %r' % backend)

    #
    # External execution
    #
    def start_console(self, console='auto', turtle='auto'):
        """
        Starts a regular python console with the current transpyler.

        Args:
            console:
                Can be one of 'jupyter', 'console', 'qtconsole', 'auto'. This
                chooses the default console application. The default behavior
                (auto) is to try jupyter and fallback to console if it is
                not available.
            turtle:
                Sets the turtle backend. It can be either 'qt', 'tk', 'none' or
                'auto'. The defaut strategy (auto) is to try the qt first and
                fallback to tk.
        """
        from .jupyter import start_jupyter

        start_jupyter(self, gui=False)

    def start_notebook(self):
        """
        Starts a jupyter notebook with the current transpyler.
        """
        raise NotImplementedError

    def start_qturtle(self):
        """
        Starts a QTurtle application with the current transpyler.
        """

        if not has_qt():
            raise SystemExit('PyQt5 is necessary to run the turtle '
                             'application.')

        from qturtle.mainwindow import start_application

        start_application(self)

    def start_main(self):
        """
        Starts the default main application.
        """

        @click.command()
        @click.option('--cli/--no-cli', '-c', default=False,
                      help='start gui-less console.')
        @click.option('--notebook/--no-notebook', '-n', default=False,
                      help='starts notebook server.')
        def main(cli, notebook):
            if cli:
                return self.start_console(console='nogui')
            if notebook:
                return self.start_notebook()

            if has_qt():
                return self.start_qturtle()
            else:
                click.echo('Could not start GUI. Do you have Qt installed?',
                           err=True)
                return self.start_console(console='nogui')

        return main()


def get_transpyler_from_name(key):
    """
    Return a transpyler instance for the given transpyler name or type.
    """

    try:
        return INSTANCES_FOR_NAME[key]
    except:
        import importlib

        path = key
        while path:
            try:
                importlib.import_module(path)
                return INSTANCES_FOR_NAME[key]
            except (ImportError, KeyError):
                pass
            path, _, _ = path.rpartition('.')


# Defines the default transpyler instance
simple_transpyler = Transpyler(name='transpyled')
