import ctypes

from .utils import collect_synonyms

__all__ = ['apply_curses', 'apply_attr_curse', 'apply_class_curse',
           'curse_bool_repr', 'curse_none_repr']


def apply_curses(curse_map):
    """
    Apply all curses defined in the curse map.

    Args:
        curse_map:
            A dictionary of (type, curse) pairs.
    """

    for tt, curse in curse_map.items():
        apply_class_curse(tt, curse)


def apply_attr_curse(obj, attr, value):
    """
    Adds a new attribute to builtin object cls.
    """

    target = obj.__dict__
    proxy_dict = SlotsProxy.from_address(id(target))
    proxy_dict.dict[attr] = value


def apply_class_curse(tt, curse):
    """
    Monkey patch the builtin type tt to have all methods form the given curse
    class. Name and docstring are also updated.
    """

    curse_ns = curse if isinstance(curse, dict) else vars(curse).items()
    namespace = {k: v for (k, v) in curse_ns if not k[0] == '_'}
    functions = collect_synonyms(namespace)

    for name, func in functions.items():
        if hasattr(tt, name):
            tname = tt.__name__
            raise ValueError('%s already has a %s() method' % (tname, name))
        apply_attr_curse(tt, name, func)

    # Apply docstring (not working)
    apply_attr_curse(tt, '__doc__', curse.__doc__)


def curse_bool_repr(true='True', false='False'):
    """
    Change repr of True/False to the given input strings.
    """

    def __repr__(self):  # noqa: N802
        if self:
            return true
        else:
            return false

    apply_attr_curse(bool, '__repr__', __repr__)
    apply_attr_curse(bool, '__str__', __repr__)
    assure_generic_c_level_function(bool, str_offset())
    assure_generic_c_level_function(bool, repr_offset())


def curse_none_repr(name):
    """
    Change repr of None to the given string.
    """

    name = name or 'None'

    def __repr__():  # noqa: N802
        return name

    apply_attr_curse(type(None), '__repr__', __repr__)
    apply_attr_curse(type(None), '__str__', __repr__)
    assure_generic_c_level_function(type(None), str_offset())
    assure_generic_c_level_function(type(None), repr_offset())


#
# Low level details of implementation. When cursing, we use Ctypes in order to
# modify Python builtin objects at the C level. This allow us to make changes
# that are not allowed in Python language at the risk of really screwing things
# up.
#
# These are the same techniques used in the Forbidden Fruit python module.
#
cpython = ctypes.pythonapi


class SlotsProxy(ctypes.Structure):
    _fields_ = [
        ('ob_refcnt', ctypes.c_ssize_t),
        ('ob_type', ctypes.py_object),
        ('dict', ctypes.py_object),
    ]


class Object:
    """
    Generic type we use to inspect the location of the generic C-level
    repr and str functions.

    All methods supported must provide a placeholder implementation here.
    """
    __repr__ = __str__ = lambda self: ''


def repr_offset():
    "How many bytes after id(type) can we find the tp_repr pointer?"

    return 11 * ctypes.sizeof(ctypes.c_ssize_t)


def str_offset():
    "How many bytes after id(type) can we find the tp_str pointer?"

    # str is 6 places after repr in the type specification
    return repr_offset() + 6 * ctypes.sizeof(ctypes.c_ssize_t)


def assure_generic_c_level_function(tt, offset):
    """
    Makes sure that the given type tt uses the generic c-level function
    for some of the magic methods such as repr(), str(), etc.
    """

    ref_from_address = ctypes.c_ssize_t.from_address
    tp_func_object = ref_from_address(id(Object) + offset)
    tp_func_cursed = ref_from_address(id(tt) + offset)
    tp_func_cursed.value = tp_func_object.value
