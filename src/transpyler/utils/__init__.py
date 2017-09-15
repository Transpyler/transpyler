# flake8: noqa
from .decorators import synonyms, normalize_accented_keywords, pretty_callable
from .string import keep_spaces, humanize_name, unhumanize_name, \
    normalize_docstring, split_docstring
from .utils import with_transpyler_attr, clear_argv, has_qt
from .namespaces import full_class_name, collect_synonyms, collect_mod_namespace
