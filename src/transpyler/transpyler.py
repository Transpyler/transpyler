import builtins as _builtins
import codeop
import importlib
from collections import OrderedDict

import click
from lazyutils import lazy

from transpyler.utils import pretty_callable
from transpyler.utils.translate import translate_mod, gettext_for
from transpyler.utils.utils import has_qt
from .language_info import LanguageInfo
from .lexer import Lexer

# Save useful builtin functions
_compile = _builtins.compile
_exec = _builtins.exec
_eval = _builtins.eval
_input = _builtins.input
_print = _builtins.print

INSTANCES_FOR_NAME = {}


class SingletonMeta(type):
    """
    Base metaclass for classes that have a single instance.
    """

    def __call__(cls, *args, **kwargs):
        try:
            return cls._instance
        except AttributeError:
            Transpyler._instance = super().__call__(*args, **kwargs)
            return cls._instance


class Transpyler(metaclass=SingletonMeta):
    """
    Base class for all new Transpylers.

    A transpyler is a singleton object.

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
    short_banner = lazy(lambda self: self.display_name)
    lexer = lazy(lambda self: self.lexer_factory(self))
    gettext = lazy(lambda self: gettext_for(self.i10n_lang or 'en'))

    @lazy
    def name(self):
        cls_name = self.__class__.__name__.lower()
        if cls_name == 'Transpyler':
            raise AttributeError('must define a .name attribute')
        elif cls_name.endswith('transpyler'):
            return cls_name[:-10]
        else:
            return cls_name

    @lazy
    def namespace(self):
        return self.make_global_namespace()

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

    # --------------------------------------------------------------------------
    # System functions
    def init(self, ns=None):
        """
        Initializes transpyler runtime.

        Args:
            ns (dict):
                A dictionary with extra functions to be added to the
                globals namespace at runtime.
        """

        self.apply_curses()
        self.namespace.update(ns or {})

    def apply_curses(self):
        """
        Apply any required curses.

        Default implementation does nothing.
        """

    def compile(self, source, filename, mode, flags=0, dont_inherit=False,
                compile_function=_compile):
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
        return compile_function(source, filename, mode, flags, dont_inherit)

    def exec(self, source, globals=None, locals=None, exec_function=None):
        """
        Similar to the built-in function exec() for transpyled code.

        The additional exec_function() argument allows to define a function to
        replace Python's builtin compile().

        Args:
            source (str or code):
                Code to be executed.
            globals, locals:
                A globals/locals dictionary
            exec_function (callable):
                A possible replacement for Python's built-in exec().
        """

        exec_function = exec_function or _exec
        code = self.transpile(source) if isinstance(source, str) else source
        globals = {} if globals is None else globals
        globals.update(self.namespace)

        if locals is None:
            return exec_function(code, globals)
        else:
            return exec_function(code, globals, locals)

    def eval(self, source, globals=None, locals=None, eval_function=_eval):
        """
        Similar to the built-in function eval() for transpyled code.

        The additional eval_function() argument allows to define a function to
        replace Python's builtin compile().

        Args:
            source (str or code):
                Code to be executed.
            globals, locals:
                A globals/locals dictionary
            eval_function (callable):
                A possible replacement for Python's built-in eval().
        """
        return self.exec(source, globals, locals, exec_function=eval_function)

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

        try:
            pytuga_src = self.transpile(src)
        except SyntaxError:
            return True
        return codeop.compile_command(pytuga_src, filename, symbol) is None

    def core_functions(self) -> OrderedDict:
        """
        Return a namespace dictionary with the the exec/eval/compile/transpile
        functions.

        This is useful to expose on a module to offer a exec-like interface to
        users.

        Return:
            An ordered mapping with the exec, eval, compile and transpile
            functions.
        """

        return OrderedDict([
            ('exec', self.exec),
            ('eval', self.eval),
            ('compile', self.compile),
            ('transpile', self.transpile),
        ])

    # --------------------------------------------------------------------------
    # Console helpers
    def translate(self, st):
        """
        Translates string to the requested language.
        """
        return self.gettext.gettext(st)

    def console_banner(self, short=False):
        """
        Return a string with the console banner.
        """

        if short:
            return self.short_banner
        return getattr(self, 'banner', self.short_banner)

    def make_exiter_function(self, function):
        """
        Wraps the exiter function in a nice wrapped
        """

        @pretty_callable(self.translate('exiter.doc'))
        def exit():
            return function()

        exit.__name__ = self.translate('exiter.name')
        exit.__doc__ = self.translate('exiter.doc')
        return exit

    def make_global_namespace(self):
        """
        Return a dictionary with the default global namespace for transpyler
        runtime.
        """
        ns = {}

        load_modules_queue = []

        # Load modules from list of modules
        for mod in self.builtin_modules:
            mod = importlib.import_module(mod)
            load_modules_queue.append(mod)

        # Load default translations from using the i10n_lang option
        if self.i10n_lang:
            mod = translate_mod(self.i10n_lang)
            load_modules_queue.append(mod)

        # Load all modules in queue
        for mod in load_modules_queue:
            for name in dir(mod):
                if name.startswith('_') or name.isupper():
                    continue
                ns[name] = getattr(mod, name)

        return ns

    def make_turtle_namespace(self, backend=None):
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

    # --------------------------------------------------------------------------
    # External execution
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

        # Select the console application
        if console == 'auto':
            try:
                import IPython
            except ImportError:
                console = 'console'
            else:
                console = 'jupyter'

        if console == 'qtconsole':
            from .jupyter import start_jupyter
            start_jupyter(self, gui=True)
        elif console == 'jupyter':
            from .jupyter import start_jupyter
            start_jupyter(self, gui=False)
        elif console == 'console':
            from .console import start_console
            start_console(self)

    def start_notebook(self):
        """
        Starts a jupyter notebook with the current transpyler.
        """

        from .jupyter import start_notebook
        start_notebook(self)

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
        @click.option('--cli', '-c', is_flag=True, default=False,
                      help='start gui-less console.')
        @click.option('--console', is_flag=True, default=False,
                      help='start a simple gui-less console.')
        @click.option('--notebook/--no-notebook', '-n', default=False,
                      help='starts notebook server.')
        def main(cli, notebook, console):
            if cli:
                return self.start_console(console='auto')
            if console:
                return self.start_console(console='console')
            if notebook:
                return self.start_notebook()

            if has_qt():
                return self.start_qturtle()
            else:
                click.echo('Could not start GUI. Do you have Qt installed?',
                           err=True)
                return self.start_console(console='nogui')

        return main()

