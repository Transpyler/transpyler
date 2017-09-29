import builtins as _builtins
import codeop
import importlib
import types

from lazyutils import lazy

from .info import Info
from .introspection import Introspection
from .lexer import Lexer
from .utils import pretty_callable
from .translate.gettext import gettext_for
from .translate.translate import translate_namespace
from .utils.utils import has_qt

# Save useful builtin functions
_compile = _builtins.compile
_exec = _builtins.exec
_eval = _builtins.eval
_input = _builtins.input
_print = _builtins.print


class SingletonTranspyler(type):
    """
    Base metaclass for classes that have a single instance.
    """

    _subclasses = []

    def __init__(cls, *args, **kwargs):  # noqa: N805
        super().__init__(*args, **kwargs)
        type(cls)._subclasses.append(cls)

    def __call__(cls, *args, **kwargs):  # noqa: N805
        try:
            return cls._instance
        except AttributeError:
            Transpyler._instance = super().__call__(*args, **kwargs)
            return cls._instance

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Transpyler._subclasses == None:
            Transpyler()
        return Singleton._subclasses 


class Transpyler(metaclass=SingletonTranspyler):
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

    # Factories and subclasses
    lexer_factory = Lexer
    info_factory = Info
    introspection_factory = Introspection

    # Constants
    lang = 'en'
    has_turtle_functions = False
    turtle_backend = None
    standard_lib = None
    translations = None
    invalid_tokens = None
    language_version = '0.1.0'
    version = '0.1.0'
    codemirror_mode = 'python'
    file_extension = 'py'

    # Language info and instrospection
    introspection = lazy(lambda self: self.introspection_factory)
    info = lazy(lambda self: self.info_factory(self))
    mimetypes = lazy(lambda self: [self.mimetype])
    mimetype = lazy(lambda self: 'text/x-%s' % self.name)
    link_docs = lazy(
        lambda self:
        "http://%s.readthedocs.io/%s/latest/" % (self.name, self.lang)
    )
    link_github = lazy(
        lambda self: "http://github.com/transpyler/%s/" % self.name
    )

    # Computed constants
    display_name = lazy(lambda self: self.name.title().replace('_', ' '))
    short_banner = lazy(
        lambda self: self.translate(
            '%s %s\n'
            'Type "help", "copyright" or "license" for more information.' %
            (self.display_name, self.version))
    )
    long_banner = lazy(lambda self: self.short_banner)
    lexer = lazy(lambda self: self.lexer_factory(self))
    gettext = lazy(lambda self: gettext_for(self.lang))

    @lazy
    def name(self):
        cls_name = self.__class__.__name__.lower()
        if cls_name == 'transpyler':
            return 'transpyler'
        elif cls_name.endswith('transpyler'):
            return cls_name[:-10]
        else:
            return cls_name

    @lazy
    def namespace(self):
        return self.recreate_namespace()

    def __init__(self, **kwargs):
        self._forbidden = False
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._has_init = False

        assert self.name, 'Name cannot be empty'

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.name)

    #
    #  System functions
    #
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

        compile_function = compile_function or _compile
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

        args = (globals,) if locals is None else (globals, locals)
        return exec_function(code, *args)

    def eval(self, source, globals=None, locals=None, eval_function=None):
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
        eval_function = eval_function or _eval
        code = self.transpile(source) if isinstance(source, str) else source
        globals = {} if globals is None else globals
        globals.update(self.namespace)

        args = (globals,) if locals is None else (globals, locals)
        return eval_function(code, *args)

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

    @classmethod
    def core_functions(cls):
        """
        Return an dictionary with a small namespace for the core functions in
        the transpyler API:

        * init: init runtime
        * compile: compile a string of source code
        * exec: execute a string of source code
        * eval: evaluate a string of source code and return the resulting object
        * transpile: transpile source code to Python
        * namespace: return a dictionary with builtin functions
        * is_complete_source: check if string can be executed as-is or if it
        requires additional lines of code in order to execute.
        """

        def init(ns=None):
            return cls().init(ns)

        def compile(source, filename, mode, flags=0, dont_inherit=False,
                    compile_function=None):
            return cls().compile(
                source, filename, mode, flags=flags,
                dont_inherit=dont_inherit, compile_function=compile_function
            )

        def exec(source, globals=None, locals=None, exec_function=None):
            return cls().exec(
                source, globals=globals, locals=locals,
                exec_function=exec_function,
            )

        def eval(source, globals=None, locals=None, eval_function=None):
            return cls().eval(
                source, globals=globals, locals=locals,
                eval_function=eval_function,
            )

        def transpile(src):
            return cls().transpile(src)

        def is_incomplete_source(src, filename="<input>", symbol="single"):
            return cls().is_incomplete_source(src, filename, symbol)

        def namespace(turtle=None):
            """
            Return a dictionary with all public functions.

            If turtle is given and it is either 'qt' or 'tk', it includes the
            corresponding turtle functions into the namespace.
            """
            transpyler = cls()
            transpyler.has_turtle_functions = turtle is not None
            transpyler.turtle_backend = turtle
            transpyler.init()
            return transpyler.namespace

        # Update docstrings
        init.__doc__ = cls.init.__doc__
        compile.__doc__ = cls.compile.__doc__
        exec.__doc__ = cls.exec.__doc__
        eval.__doc__ = cls.eval.__doc__
        transpile.__doc__ = cls.transpile.__doc__
        is_incomplete_source.__doc__ = cls.is_incomplete_source.__doc__

        return dict(
            init=init, compile=compile, exec=exec, eval=eval,
            transpile=transpile, is_incomplete_source=is_incomplete_source,
            namespace=namespace,
        )

    #
    # Utilities
    #
    def translate(self, st):
        """
        Translates string to the requested language.
        """
        return self.gettext.gettext(st)

    #
    # Console helpers
    #
    def console_banner(self, short=False):
        """
        Return a string with the console banner.
        """

        if short:
            return self.short_banner
        return getattr(self, 'banner', self.short_banner)

    def make_exit_function(self, function):
        """
        Wraps the exit function into a callable object that prints a nice
        message for its repr.
        """

        @pretty_callable(self.translate('exiter.doc'))
        def exit():
            return function()

        exit.__name__ = self.translate('exiter.name')
        exit.__doc__ = self.translate('exiter.doc')
        return exit

    def make_global_namespace(self):
        """
        Return a dictionary with the default global namespace for the
        transpyler runtime.
        """
        from transpyler import lib
        
        ns = extract_namespace(lib)

        # Load default translations from using the lang option
        if self.lang:
            translated = translate_namespace(ns, self.lang)
            ns.update(translated)

        return ns

    def make_turtle_namespace(self, backend):
        """
        Return a dictionary with all turtle-related functions.
        """

        if backend == 'tk':
            from transpyler.turtle.tk import make_turtle_namespace

            ns = make_turtle_namespace()

        elif backend == 'qt':
            from transpyler.turtle.qt import make_turtle_namespace

            ns = make_turtle_namespace()

        else:
            raise ValueError('invalid backend: %r' % backend)

        if self.lang:
            translated = translate_namespace(ns, self.lang)
            ns.update(translated)
        
        return ns            

    def recreate_namespace(self):
        """
        Recompute the default namespace for the transpyler object.
        """
        ns = self.make_global_namespace()

        if self.has_turtle_functions:
            if self.turtle_backend is None:
                raise RuntimeError(
                    '.turtle_backend of transpyler object must be set to '
                    'either "tk" or "qt"'
                )
            turtle_ns = self.make_turtle_namespace(self.turtle_backend)
            ns.update(turtle_ns)
        self.namespace = ns
        return ns

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

        # Select the console application
        if console == 'auto':
            try:
                import IPython  # noqa: F401
            except ImportError:
                console = 'console'
            else:
                console = 'jupyter'

        if console == 'qtconsole':
            from .jupyter import start_jupyter
            start_jupyter(transpyler=self, gui=True)

        elif console == 'jupyter':
            from .jupyter import start_jupyter
            start_jupyter(transpyler=self, gui=False)

        elif console == 'console':
            from .console import start_console
            start_console(transpyler=self)

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

        import click

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


#
# Utility functions
#

def extract_namespace(mod):
    """
    Return a dictionary with module public variables.
    """

    return {
        name: getattr(mod, name) for name in dir(mod) 
        if not name.startswith('_')
    } 