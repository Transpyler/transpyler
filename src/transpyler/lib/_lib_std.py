import time as _time


#
# Standard Python functions
#
def range(*args):
    """
    range(stop) -> range object
    range(start, stop[, step]) -> range object

    Return an object that produces a sequence of integers from start (inclusive)
    to stop (exclusive) by step.  range(i, j) produces i, i+1, i+2, ..., j-1.
    start defaults to 0, and stop is omitted!  range(4) produces 0, 1, 2, 3.
    These are exactly the valid indices for a list of 4 elements.
    When step is given, it specifies the increment (or decrement).
    """
    return _range(*args)


#
# Time control
#
def sleep(seconds):
    """
    Delay execution for a given number of seconds.

    The argument may be a floating point number for subsecond precision.
    """
    return _sleep(seconds)


def exit(msg=0):
    """
    Finish program execution and provides an exit code.

    If msg is not given, the program finishes in a successful state. An
    exit code different from zero or a string tells that there were an error
    during execution.
    """
    return _exit(msg)


#
# Conversions/representations of numerical types
#
def integer(x):
    "Converts argument to an integer."
    return _integer(x)


def real(x):
    "Convert argument to a real number (number with decimal places)."
    return _real(x)


def complex(x):
    "Convert argument to a complex number."
    return _complex(x)


def boolean(x):
    """Convert argument to a boolean value.

    Zero and empty sequences are converted to False. All other values are True.
    """
    return _boolean(x)


def binary(x):
    "Convert integer to a string with its binary representation."
    return _binary(x)


def octal(x):
    "Convert integer to a string with its octal representation."
    return _octal(x)


def hexadecimal(x):
    "Convert integer to a string with its hexadecimal representation"
    return _hexadecimal(x)


def character(x):
    """
    Convert number to its corresponding character in the ASCII/Unicode tables.
    """
    return _character(x)


# These functions can be replaced/mocked and have a proper behavior in a
# graphical environment or in tests.
_range = range
_sleep = _time.sleep
_integer = int
_real = float
_complex = complex
_string = str
_boolean = bool
_binary = bin
_octal = oct
_hexadecimal = hex
_character = chr


def _exit(msg):
    raise SystemExit(msg)
