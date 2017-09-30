#
# Test common transpyler examples for python transpyler
#
import pytest

from transpyler import Transpyler


class TranspyledLanguage:
    @pytest.fixture
    def fibo_code(self):
        return (
            'x, y = 1, 1\n'
            'for i in [1, 2, 3, 4, 5]:\n'
            '    x, y = y, x + y'
        )

    @pytest.fixture
    def invariants(self):
        return [
            # Arithmetic operations
            '1 + 1', '2 - 1', '3 * 2', '4 / 5.5',

            # Simple function calls
            'print("hello world")',
        ]

    def test_transpile(self, transpyler):
        assert transpyler.transpile('1 + 1') == '1 + 1'

    def test_eval(self, transpyler):
        assert transpyler.eval('1 + 1') == 2

    def test_exec(self, transpyler):
        ns = {}
        transpyler.exec('x = 42', ns)
        assert ns['x'] == 42

    def test_compile(self, transpyler):
        ns = {}
        code = transpyler.compile('x = 1 + 1', '<file>', 'exec')
        transpyler.exec(code, ns)
        assert ns['x'] == 2

    def test_is_incomplete(self, transpyler):
        assert transpyler.is_incomplete_source('[1, 2, 3') is True
        assert transpyler.is_incomplete_source('[1, 2, 3]') is False

    def test_transpilation_keep_invariants(self, invariants, transpyler):
        for src in invariants:
            transpyler.transpile(src) == src

    def test_invariants_equal_to_python(self, invariants, transpyler):
        for src in invariants:
            res_py = eval(src)
            res = transpyler.eval(src)
            assert res_py == res

    def test_empty_string_is_no_op(self, transpyler):
        assert transpyler.transpile('') == ''

    def test_raise_syntax_error_for_bad_code(self, transpyler):
        with pytest.raises(SyntaxError):
            transpyler.exec('AA BB CC', {})

    def test_fibonacci_transpile(self, transpyler, fibo_code):
        user = transpyler.transpile(fibo_code)
        res = (
            'x, y = 1, 1\n'
            'for i in [1, 2, 3, 4, 5]:\n'
            '    x, y = y, x + y'
        )
        code1 = compile(user, '<file>', 'exec')
        code2 = compile(res, '<file>', 'exec')
        assert code1.co_code == code2.co_code

    def test_fibonacci_results(self, transpyler, fibo_code):
        D = {}
        transpyler.exec(fibo_code, D)
        assert D['x'] == 8
        assert D['y'] == 13


# ------------------------------------------------------------------------------
# Python transpyler tests
# ------------------------------------------------------------------------------
class PythonTranspylerFixtures:
    """
    Mixin class with all fixtures used with the Python Transpyler object
    """

    @pytest.yield_fixture(scope='class')
    def transpyler(self):
        class Python(Transpyler):
            pass

        yield Python()
        del Transpyler._instance


class TestPythonLanguage(PythonTranspylerFixtures, TranspyledLanguage):
    pass


# ------------------------------------------------------------------------------
# PyBr tests
# ------------------------------------------------------------------------------
class PyBrFixtures:
    """
    Mixin class with all fixtures used with the PyBr Transpyler object
    """

    @pytest.yield_fixture(scope='class')
    def transpyler(self):
        class PyBr(Transpyler):
            translations = {
                'para': 'for',
                'em': 'in',
                ('para', 'cada'): 'for',
                ('faça', ':'): ':',
            }
            lang = 'pt_BR'

        if hasattr(Transpyler, '_instance'):
            del Transpyler._instance
        yield PyBr()
        del Transpyler._instance

    @pytest.fixture
    def fibo_code(self):
        return (
            'x, y = 1, 1\n'
            'para cada i em [1, 2, 3, 4, 5] faça:\n'
            '    x, y = y, x + y'
        )


class TestPyBrLanguage(PyBrFixtures, TranspyledLanguage):
    """
    Concrete tests for the dummy PyBr transpyler.
    """

    def test_pybr_eval(self, transpyler):
        assert transpyler.eval('1 em (1, 2)', {}) is True

    def test_default_namespace(self, transpyler):
        ns = transpyler.make_global_namespace()
        assert 'cos' in ns
        assert 'mostre' in ns

    def test_translate(self, transpyler):
        assert transpyler.translate('file') == 'arquivo'
