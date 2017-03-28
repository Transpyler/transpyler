import sys

from mock import mock

from transpyler.tools.google_translate import translate_functions, \
    translate_function, get_args


def f(x, y=1, *args, z=1, d=2, **kwargs):
    """
    Some function!
    """


def g(x, y=1, *args, z=1, d=2, **kwargs):
    """
    Some other function!
    """


def test_get_correct_args():
    args = get_args(f)
    assert args == [('x', None), ('y', '1'), ('*args', None), ('z', '1'),
                    ('d', '2'), ('**kwargs', None)]


def test_google_translate_function():
    # Python 3.3 and 3.4 syntax breaks with complex g function.
    func = f if sys.version_info[1] >= 5 else g

    with mock.patch('textblob.TextBlob.translate', lambda x, y, z: str(x)):
        src = translate_function(func, 'pt-br')
    compile('\n' + src + '\n', '<input>', 'exec')


def test_google_translate_builtin():
    with mock.patch('textblob.TextBlob.translate', lambda x, y, z: str(x)):
        src = translate_functions([dir], 'pt-br')[0]
    compile(src, '<input>', 'exec')
