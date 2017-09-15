import re

from pygments import unistring as uni
from pygments.lexer import bygroups, default, words
from pygments.lexers.python import Python3Lexer
from pygments.token import Text, Operator, Keyword, Name, String, Number
from pygments.util import shebang_matches


def transpyler_lexer_factory(transpyler):
    """
    Return a Pygments lexer class for the given transpyler.
    """

    def analyse_text(text):
        return shebang_matches(text, r'pythonw?3(\.\d)?')

    return type(
        transpyler.pygments_class_name,
        (Python3Lexer,),
        dict(
            analyse_text=analyse_text,
            name=transpyler.name,
            aliases=[transpyler.display_name],
            filenames=transpyler.file_extensions,
            mimetypes=transpyler.mimetypes,
            flags=re.MULTILINE | re.UNICODE,
            uni_name="[%s][%s]*" % (uni.xid_start, uni.xid_continue),
            tokens=make_transpyled_tokens(transpyler),
        )
    )


def make_transpyled_tokens(transpyler):
    """
    Return a list of pygments make_transpyled_tokens from a transpyler object.
    """

    keywords = transpyler.introspection.all_keywords
    constants = transpyler.introspection.all_constants
    exceptions = transpyler.introspection.all_exceptions
    builtins = transpyler.introspection.all_builtins

    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)

    tokens = Python3Lexer.tokens.copy()

    tokens['keywords'] = [
        (words(keywords, suffix=r'\b'), Keyword),
        (words(constants, suffix=r'\b'), Keyword.Constant),
    ]
    tokens['builtins'] = [
        (words(builtins, prefix=r'(?<!\.)', suffix=r'\b'), Name.Builtin),
        (r'(?<!\.)(self|Ellipsis|NotImplemented)\b', Name.Builtin.Pseudo),
        (words(exceptions, prefix=r'(?<!\.)', suffix=r'\b'),
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
    return tokens
