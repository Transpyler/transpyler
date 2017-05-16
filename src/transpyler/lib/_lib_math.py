import math as _math
import random as _random

# Standard mathematical functions and constants
pi = _math.pi
e = _math.exp(1)
sqrt = _math.sqrt
exp = _math.exp
log = ln = _math.log
log10 = _math.log10
log2 = _math.log2
abs = abs
round = round
ceil = _math.ceil
trunc = _math.trunc


# Trigonometric functions (transform arguments to degrees from radians)
def __trig_factory(func):
    from functools import wraps
    from math import pi

    cte = pi / 180

    @wraps(func)
    def f(x):
        return func((x % 360) * cte)

    return f


sin = __trig_factory(_math.sin)
cos = __trig_factory(_math.cos)
tan = __trig_factory(_math.tan)


# Complex functions
def sign(x):
    """
    Return 1 if x is positive, -1 if it is negative and 0 if it is null.

    Examples:
        >>> sign(-32.0)
        -1
    """
    if x == 0:
        return 0
    elif x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        raise ValueError(sign.ERROR)


sign.ERROR = 'argument does not have a well defined sign'

# Functions that operate on lists of numbers (or number-like things)
max = max
min = min
sum = sum
all = all
any = any


def product(seq, start=1.0):
    """
    Return the product of all numbers in the sequence.
    """

    result = start
    for x in seq:
        result *= x
    return result


# Random numbers
random = _random.random
randint = _random.randint


def dice(n=6):
    """
    Simulate a dice trow (return a random number between 1 and 6.

    Call with an explicit argument to throw a dice with a different number of
    faces

    Examples:
        >>> dice(20)                                            # doctest: +SKIP
        13
    """
    return _random.randint(1, 6)
