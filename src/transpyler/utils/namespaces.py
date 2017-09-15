from unidecode import unidecode


SYNONYM_ERROR_MSG = '%s is present in global_namespace, but is also a synonym of %s'


def collect_synonyms(namespace, add_unaccented=True):
    """
    Return a dictionary with all synonyms found in the given global_namespace.

    Args:
        namespace:
             A mapping from names to values.
        add_unaccented:
            If True (default) extends with the unaccented versions of the names
            collected in the global_namespace.

    Raise a ValueError for name conflicts.
    """

    result = {}

    # Includes the aliased versions of the names defined in the input global_namespace
    for attr, func in namespace.items():
        if hasattr(func, '__synonyms__'):
            for alias in func.__synonyms__:
                result.setdefault(alias, func)

    # Collect unaccented names and maps them to the corresponding
    # functions/values
    if add_unaccented:
        for name, func in list(result.items()):
            no_accent = unidecode(name)
            if no_accent != name:
                result.setdefault(no_accent, func)

    return result


def collect_mod_namespace(mod=None):
    """
    Return a namespace dict with all public names for the given module.

    If no module is given, uses transpyler's standard lib.
    """
    import transpyler.lib as lib

    namespace = vars(mod or lib)
    return {k: v for (k, v) in namespace.items() if not k.startswith('_')}


def full_class_name(cls):
    """
    Return the full class name prepending module paths.
    """

    return '%s.%s' % (cls.__module__, cls.__name__)
