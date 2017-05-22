import pytest

from transpyler import Transpyler


@pytest.yield_fixture
def python():
    """
    A new transpyler that makes no changes in comparison with the default
    interpreter.
    """

    class Python(Transpyler):
        pass

    yield Python()
    del Transpyler._instance


@pytest.yield_fixture
def pybr():
    class PyBr(Transpyler):
        translations = {
            'para': 'for',
            'em': 'in',
            ('para', 'cada'): 'for',
            ('faça', ':'): ':',
        }
        i10n_lang = 'pt_BR'

    yield PyBr()
    del Transpyler._instance


@pytest.fixture
def pybr_code():
    return '''
x, y = 1, 1
para cada i em [1, 2, 3, 4, 5] faça:
    x, y = y, x + y
'''
