import pytest

from transpyler import Transpyler


class TestInstrospections:
    @pytest.yield_fixture(scope='class')
    def transpyler(self):
        class PyBr(Transpyler):
            translations = {
                'para': 'for',
                'em': 'in',
                ('para', 'cada'): 'for',
            }
            lang = 'pt_BR'

        if hasattr(Transpyler, '_instance'):
            del Transpyler._instance
        yield PyBr()
        del Transpyler._instance

    def test_introspections(self, transpyler):
        intro = transpyler.introspection

        assert 'True' in intro.py_constants
        assert 'True' in intro.all_constants
        assert 'StopIteration' in intro.all_exceptions
        assert 'int' in intro.all_types
        assert 'alert' in intro.all_functions
        assert 'alert' in intro.all_builtins
        assert not intro.all_submodules
        assert {'para', 'cada', 'em'}.issubset(intro.all_keywords)
