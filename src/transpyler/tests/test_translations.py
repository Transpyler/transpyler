import pytest

from transpyler import lib
from transpyler.tests import mod
from transpyler.translate import extract_translations, extract_translation, \
    translate_namespace


class TestExtractTranslations:
    @pytest.fixture
    def func(self):
        def f(x, y=0):
            """
            Test function.
            """
            return x + y

        return f

    @pytest.fixture
    def cls(self):
        class Foo:
            "docstring"

            def f(self, x):
                "method docstring"
                return x

        return Foo

    def test_extract_translation_from_func(self, func):
        trans = extract_translation(func)
        assert trans == {'args': 'x, y', 'doc': 'Test function.', 'name': 'f'}

    def test_extract_translation_from_class(self, cls):
        trans = extract_translation(cls)
        assert trans == {
            'name': 'Foo', 'doc': 'docstring',
            ':f.name': 'f', ':f.args': 'self, x', ':f.doc': 'method docstring',
        }

    def test_extract_translations_from_namespace(self, func, cls):
        trans = extract_translations({
            'f': func,
            'Foo': cls,
            'TRANSLATIONS': {'foobar': 'barfoo'}
        })

        assert trans == {
            'Foo.name': 'Foo', 'Foo.doc': 'docstring',
            'Foo:f.name': 'f', 'Foo:f.args': 'self, x',
            'Foo:f.doc': 'method docstring',
            'f.args': 'x, y', 'f.doc': 'Test function.', 'f.name': 'f',
            'foobar': 'barfoo',
        }


class TestTranslate:
    def test_translated_function_works_properly(self):
        ns_orig = {'sqrt': lib.sqrt}
        ns_trans = translate_namespace(ns_orig, 'pt_BR')

        print(ns_trans)
        raiz = ns_trans['raiz']
        sqrt = ns_orig['sqrt']
        assert ns_orig is not ns_trans
        assert raiz is not sqrt
        assert raiz(4) == sqrt(4) == 2.0

    def test_translate_mod_to_pt_BR(self):
        ns = translate_namespace(vars(mod), 'pt_BR')
        assert set(x for x in ns if not x.startswith('_')) == {
            'cos', 'coseno', 'mostrar', 'mostre', 'print',
        }

        msg = 'Mostra o objeto ou texto fornecido na tela.'
        assert ns['mostre'].__doc__.startswith(msg)

    def test_translate_mod_to_es_BR(self):
        ns = translate_namespace(vars(mod), 'es_BR')
        assert set(x for x in ns if not x.startswith('_')) == {
            'cos', 'imprimir', 'print',
        }

        msg = 'Muestra el objeto o texto proporcionado en la pantalla.'
        assert ns['imprimir'].__doc__.startswith(msg)
