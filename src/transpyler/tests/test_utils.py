import sys

from transpyler.utils import *
from transpyler.utils import synonyms, normalize_accented_keywords


class TestUtilityFunctions:
    def test_has_qt(self):
        try:
            import PyQt5
            assert has_qt()
        except ImportError:
            assert not has_qt()

    def test_clear_argv(self):
        argv = [sys.executable, 'foo.py', '--help']
        clear_argv(argv)
        assert argv == [sys.executable, 'foo.py']

        argv = ['my-program', 'foo.py', '--help']
        clear_argv(argv)
        assert argv == ['my-program']

    def test_pretty_function(self):
        @pretty_callable('type foo() to call it')
        def foo():
            return 42

        assert repr(foo) == 'type foo() to call it'
        assert foo() == 42
        assert foo.__name__ == 'foo'

    def test_with_transpyler_class(self):
        class Foo:
            pass

        Bar = with_transpyler_attr(Foo, 'transpyler')
        assert Bar.transpyler == 'transpyler'


class TestStringFunctions:
    """
    Utility functions for string processing
    """

    def test_keep_spaces(self):
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

    def test_humanize_names(self):
        assert humanize_name('SomeName') == 'Some Name'
        assert humanize_name('some_name') == 'some name'

    def test_unhumanize_names(self):
        assert unhumanize_name('Some Name') == 'SomeName'
        assert unhumanize_name('some name') == 'some_name'

    def test_split_docstring(self):
        split_docstring('foo\nbar\n\nfoobar.') == ['foo\nbar', 'foobar']
        split_docstring('foo\nbar\n\n  foobar.') == ['foo\nbar\n\n  foobar']


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
