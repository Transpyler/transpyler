import transpyler.lib as lib
from transpyler.utils import *
from transpyler.utils import synonyms, normalize_accented_keywords
from transpyler.utils.translate import translate_mod


def test_keep_spaces():
    f = keep_spaces
    assert f(' foo ', '') == 'foo'
    assert f('foo', 'bar') == 'foo'
    assert f(' \nfoo', 'bar') == 'foo'
    assert f(' \nfoo\n ', 'bar') == 'foo'
    assert f('foo', ' \nbar') == ' \nfoo'
    assert f('\n foo\n ', ' \nbar') == ' \nfoo'
    assert f('\n foo', ' \nbar') == ' \nfoo'
    assert f('foo\n', ' \nbar') == ' \nfoo'
    assert f('foo', ' \nbar\n ') == ' \nfoo\n '
    assert f('\n foo', ' \nbar\n ') == ' \nfoo\n '
    assert f('\n foo\n ', ' \nbar\n ') == ' \nfoo\n '
    assert f('foo\n ', ' \nbar\n ') == ' \nfoo\n '
    assert f('foo\n   bar', 'ham\n   spam') == 'foo\n   bar'


def test_pretty_function():
    @pretty_callable('type foo() to call it')
    def foo():
        return 42

    assert repr(foo) == 'type foo() to call it'
    assert foo() == 42
    assert foo.__name__ == 'foo'


def test_with_transpyler_class():
    class Foo:
        pass

    Bar = with_transpyler_attr(Foo, 'transpyler')
    assert Bar.transpyler == 'transpyler'


class TestSynonyms:
    def test_collect_synonyms(self):
        @synonyms('foobar', 'bar')
        def foo(x, y):
            pass

        sym_ns = collect_synonyms({'foo': foo})
        assert sym_ns['foobar'] is foo
        assert sym_ns['bar'] is foo
        assert 'foo' not in sym_ns

    def test_collect_synonyms_unaccented(self):
        @synonyms('fôo', 'bár')
        def fôobar(x, y):
            pass

        foo = fôobar
        sym_ns = collect_synonyms({'fôobar': foo}, add_unaccented=True)
        assert sym_ns == {
            'foo': foo,
            'bar': foo,
            'fôo': foo,
            'bár': foo,
        }

    def test_normalized_kwargs(self):
        @normalize_accented_keywords
        def foo(bar, baz):
            return bar + 2 * baz

        assert foo(1, 2) == 5
        assert foo(bar=1, baz=2) == 5
        assert foo(bár=1, báz=2) == 5


class TestTranslate:
    def test_translate_module(self):
        mod = translate_mod('pt_BR')
        assert mod is not lib

        f = mod.concatenar
        g = lib.concatenate
        args = ('foo', 'bar', 1, 2, 3)
        assert f is not g
        assert f(*args) == g(*args)
