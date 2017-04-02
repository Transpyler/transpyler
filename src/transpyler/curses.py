import ctypes

from transpyler.utils import collect_synonyms

cpython = ctypes.pythonapi


class SlotsProxy(ctypes.Structure):
    _fields_ = [
        ('ob_refcnt', ctypes.c_ssize_t),
        ('ob_type', ctypes.py_object),
        ('dict', ctypes.py_object),
    ]


def add_attr_curse(obj, attr, value):
    """
    Adds a new attribute to builtin object cls.
    """

    target = obj.__dict__
    proxy_dict = SlotsProxy.from_address(id(target))
    proxy_dict.dict[attr] = value


def apply_curse_to_class(tt, curse):
    """
    Monkey patch the builtin type tt to have all methods form the given curse
    class. Name and docstring are also updated.
    """

    namespace = {k: v for (k, v) in vars(curse).items() if not k[0] == '_'}
    functions = collect_synonyms(namespace)
    for name, func in functions.items():
        if hasattr(tt, name):
            tname = tt.__name__
            raise ValueError('%s already has a %s() method' % (tname, name))
        add_attr_curse(tt, name, func)

    # Apply docstring (not working)
    add_attr_curse(tt, '__doc__', curse.__doc__)


def apply_curses(curse_map):
    """
    Apply all curses defined in the curse map.

    Args:
        curse_map:
            A dictionary of (type, curse) pairs.
    """

    for tt, curse in curse_map.items():
        apply_curse_to_class(tt, curse)


class _object:
    """
    Generic type we use to inspect the location of the generic C-level
    repr and str functions.

    All methods supported must provide a placeholder implementation here.
    """

    __repr__ = __str__ = lambda self: ''


def _repr_offset():
    """How many bytes after id(type) can we find the tp_repr pointer?"""

    return 11 * ctypes.sizeof(ctypes.c_ssize_t)


def _str_offset():
    """How many bytes after id(type) can we find the tp_str pointer?"""

    # str is just 6 places after repr in the type specification
    return _repr_offset() + 6 * ctypes.sizeof(ctypes.c_ssize_t)


def _assure_generic_c_level_function(tt, offset):
    """
    Makes sure that the given type tt uses the generic c-level function
    for some of the magic methods such as repr(), str(), etc.
    """

    ref_from_address = ctypes.c_ssize_t.from_address
    tp_func_object = ref_from_address(id(_object) + offset)
    tp_func_cursed = ref_from_address(id(tt) + offset)
    tp_func_cursed.value = tp_func_object.value


def curse_bool_repr(true='True', false='False'):
    """
    Change repr of True/False to the given input strings.
    """

    def __repr__(self):
        if self:
            return true
        else:
            return false

    add_attr_curse(bool, '__repr__', __repr__)
    add_attr_curse(bool, '__str__', __repr__)
    _assure_generic_c_level_function(bool, _str_offset())
    _assure_generic_c_level_function(bool, _repr_offset())


def curse_none_repr(name):
    """
    Change repr of None to the given string.
    """

    name = name or 'None'

    def __repr__():
        return name

    add_attr_curse(type(None), '__repr__', __repr__)
    add_attr_curse(type(None), '__str__', __repr__)
    _assure_generic_c_level_function(type(None), _str_offset())
    _assure_generic_c_level_function(type(None), _repr_offset())
