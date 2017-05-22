import pytest

from transpyler.utils.translate import extract_translation, \
    extract_translations, translate_mod


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


class TestTranslateModule:
    def test_translate_mod(self):
        from transpyler.tests import mod

        new_mod = translate_mod('pt_BR', mod)
        public_names = {x for x in dir(new_mod) if not x.startswith('_')}
        assert public_names == {
            'cos', 'coseno', 'mostrar', 'mostre', 'print',
        }

        assert new_mod.mostre.__doc__.startswith(
            'Mostra o objeto ou texto fornecido na tela.')
            # assert new_mod.cos.__doc__ == ''

    def test_translate_standard_module_to_pt_BR(self):
        mod = translate_mod('pt_BR')

        assert mod.mostre
        assert mod.mostrar

    def test_translate_standard_module_to_es_BR(self):
        mod = translate_mod('es_BR')

        print('\n'.join(dir(mod)))
        assert mod.imprimir
