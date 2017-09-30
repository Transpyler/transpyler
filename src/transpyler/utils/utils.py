#
# Random utility functions
#
import sys


def with_transpyler_attr(cls, transpiler):
    """
    Return a subclass with the transpyler attribute defined.
    """

    return type(cls.__name__, (cls,), {'transpyler': transpiler})


def has_qt():
    """
    Returns True if PyQt5 is installed.
    """
    try:
        import PyQt5  # noqa: F401
        return True
    except ImportError:
        return False


def clear_argv(argv=sys.argv):
    """
    Remove extra arguments from sys.argv.
    """

    keep = [argv.pop(0)]
    if keep[0] == sys.executable:
        keep.append(argv.pop(0))
    argv[:] = keep
