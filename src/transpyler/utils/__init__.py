# Decorators
from .decorators import (
    synonyms, is_api_function, normalize_accented_keywords, pretty_callable
)

# Utility
from .string import keep_spaces
from .utils import with_transpyler_attr, clear_argv, has_qt
from transpyler.utils.namespaces import full_class_name

# Namespaces
from .namespaces import collect_synonyms