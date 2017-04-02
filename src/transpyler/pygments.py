import re

from pygments import unistring as uni
from pygments.lexer import bygroups, default, words
from pygments.lexers.python import Python3Lexer, PythonTracebackLexer
from pygments.token import Text, Operator, Keyword, Name, String, Number
from pygments.util import shebang_matches

from pytuga import core as tuga_introspect
from pytuga import keyword

KEYWORDS = keyword.kwlist
CONSTANTS = keyword.constants
EXCEPTIONS = tuga_introspect.py_exceptions + tuga_introspect.exceptions
BUILTINS = tuga_introspect.py_builtins + tuga_introspect.builtins
NAME = 'Transpyled'
ALIASES = ['transpyled']
FILENAMES = ['pytp']
MIMETYPES = ['text/x-transpyled', 'application/x-transpyled']


class TranspyledLexer(Python3Lexer):
    """
    A lexer for transpyler based languages.

    This is just the standard Python
    """

    name = NAME
    aliases = ALIASES
    filenames = FILENAMES
    mimetypes = MIMETYPES

    flags = re.MULTILINE | re.UNICODE

    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)

    tokens = Python3Lexer.tokens.copy()  # @UndefinedVariable

    tokens['keywords'] = [
        (words(KEYWORDS, suffix=r'\b'), Keyword),
        (words(CONSTANTS, suffix=r'\b'), Keyword.Constant),
    ]
    tokens['builtins'] = [
        (words(BUILTINS, prefix=r'(?<!\.)', suffix=r'\b'), Name.Builtin),
        (r'(?<!\.)(self|Ellipsis|NotImplemented)\b', Name.Builtin.Pseudo),
        (words(EXCEPTIONS, prefix=r'(?<!\.)', suffix=r'\b'),
         Name.Exception),
    ]
    tokens['numbers'] = [
        (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
        (r'0[oO][0-7]+', Number.Oct),
        (r'0[bB][01]+', Number.Bin),
        (r'0[xX][a-fA-F0-9]+', Number.Hex),
        (r'\d+', Number.Integer)
    ]
    tokens['backtick'] = []
    tokens['name'] = [
        (r'@\w+', Name.Decorator),
        (uni_name, Name),
    ]
    tokens['funcname'] = [
        (uni_name, Name.Function, '#pop')
    ]
    tokens['classname'] = [
        (uni_name, Name.Class, '#pop')
    ]
    tokens['import'] = [
        (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
        (r'\.', Name.Namespace),
        (uni_name, Name.Namespace),
        (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
        default('#pop')  # all else: go back
    ]
    tokens['fromimport'] = [
        (r'(\s+)(import)\b', bygroups(Text, Keyword), '#pop'),
        (r'\.', Name.Namespace),
        (uni_name, Name.Namespace),
        default('#pop'),
    ]
    tokens['strings'] = [
        # the old style '%s' % (...) string formatting (still valid in Py3)
        (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
         '[hlL]?[diouxXeEfFgGcrs%]', String.Interpol),
        # the new style '{}'.format(...) string formatting
        (r'\{'
         '((\w+)((\.\w+)|(\[[^\]]+\]))*)?'  # field name
         '(\![sra])?'  # conversion
         '(\:(.?[<>=\^])?[-+ ]?#?0?(\d+)?,?(\.\d+)?[bcdeEfFgGnosxX%]?)?'
         '\}', String.Interpol),
        # backslashes, quotes and formatting signs must be parsed one at a time
        (r'[^\\\'"%\{\n]+', String),
        (r'[\'"\\]', String),
        # unhandled string formatting sign
        (r'%|(\{{1,2})', String)
        # newlines are an error (use "nl" state)
    ]

    def analyse_text(text):  # @NoSelf
        return shebang_matches(text, r'pythonw?3(\.\d)?')


class PytugaTracebackLexer(PythonTracebackLexer):
    pass
