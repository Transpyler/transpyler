from mock import mock

from transpyler.tools.google_translate import translate_functions, translate_function, get_args

def function(x, y=1, *args, z=1, d=2, **kwargs):
    """
    Some function!
    """
    pass


def test_get_correct_args():
    args = get_args(function)
    assert args == [('x', None), ('y', '1'), ('*args', None), ('z', '1'),
                    ('d', '2'), ('**kwargs', None)]


def test_google_translate_function():
    with mock.patch('textblob.TextBlob.translate', lambda x, y, z: str(x)):
        src = translate_function(function, 'pt-br')
    print(src)
    compile('\n' + src + '\n', '<input>', 'exec')


def test_google_translate_builtin():
    with mock.patch('textblob.TextBlob.translate', lambda x, y, z: str(x)):
        src = translate_functions([dir], 'pt-br')[0]
    print(src)
    compile(src, '<input>', 'exec')
