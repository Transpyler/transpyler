import builtins as _builtins
import codeop

from lazyutils import lazy

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
    Base class for a new transpyled transpyler.

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

    translations = None
    invalid_tokens = None
    language_version = '0.1.0'
    version = '0.1.0'
    codemirror_mode = 'python'
    file_extension = 'py'
    _compile = _compile
    _exec = _exec
    _eval = _eval
    _input = _input
    _print = _print
    lexer_factory = Lexer
    builtins_factory = Builtins
    info_factory = LanguageInfo

    @lazy
    def name(self):
        cls_name = self.__class__.__name__.lower()
        if cls_name == 'Transpyler':
            return 'transpyler'
        elif cls_name.endswith('transpyler'):
            return cls_name[:-10]
        else:
            return cls_name

    @lazy
    def mimetype(self):
        return 'text/x-%s' % self.name

    @lazy
    def display_name(self):
        return self.name.title()

    @lazy
    def lexer(self):
        return self.lexer_factory(self)

    @lazy
    def builtins(self):
        return self.builtins_factory(self)

    @lazy
    def info(self):
        return self.info_factory(self)

    @lazy
    def _namespace_cache(self):
        return self.get_builtins_namespace()

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

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.name)

    def update_user_ns(self, ns):
        """
        Update user namespace that is initialized when a Transpyled transpyler
        starts an interactive shell.
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
            self.builtins.update(extra_builtins)
        if apply_builtins:
            self.builtins.load_as_builtins()

    def apply_curses(self):
        """
        Apply any required curses.

        Default implementation does nothing.
        """

    def compile(self, source, filename, mode, flags=0, dont_inherit=False,
                compile_function=None):
        """
        Similar to the built-in function compile() for Pytuguês code.

        The additional compile_function() argument allows to define a function to
        replace Python's builtin compile().

        Args:
            source (str or code):
                Code to be executed.
            filename:
                File name associated with code. Use '<input>' for strings.
            mode:
                One of 'exec' or 'eval'. The second allows only simple statements
                that generate a value and is used by the eval() function.
            forbidden (bool):
                If true, initialize the forbidden lib functionality to enable i18n
                for Python builtins in C-level.
            compile_function (callable):
                A possible replacement for Python's built-in compile().
        """

        source = self.transpile(source)
        compile_function = compile_function or self._compile
        return compile_function(source, filename, mode, flags, dont_inherit)

    def exec(self, source, globals=None, locals=None, forbidden=False,
             exec_function=None, builtins=False, _builtins_to_globals=True):
        """
        Similar to the built-in function exec() for Pytuguês code.

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
                If true, initialize the forbidden lib functionality to enable i18n
                for Python builtins in C-level.
            exec_function (callable):
                A possible replacement for Python's built-in exec().
        """

        if builtins:
            with self.builtins.restore_after():
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

    def get_builtins_namespace(self):
        """
        Return a dictionary with the default builtins get_namespace for transpyler.
        """

        return self.builtins.get_namespace()

    def get_console_banner(self):
        """
        Return a string with the console banner.
        """

        try:
            return self.banner
        except AttributeError:
            return 'Warning: please define .get_console_banner() method of your ' \
                   'transpyler.'


def get_transpyler_from_name(key):
    """
    Return a transpyler instance for the given transpyler name or type.
    """

    return INSTANCES_FOR_NAME[key]


# Defines the default transpyler instance
transpyler = Transpyler(name='default_transpyler')
