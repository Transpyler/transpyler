"""
Useful mathematical functions and objects.

These functions are used mostly by the turtle interface.
"""

import math as _math
import random as _random
from collections import namedtuple as _namedtuple
from numbers import Number, Real

_dg = _math.pi / 180
pi = _math.pi
e = _math.e


# Trigonometric functions
def cos(angle):
    """Cosine of an angle (in degrees)"""

    angle = angle % 360
    if angle in (90, 270):
        return 0.0
    return _math.cos(angle * _dg)


def sin(angle):
    """Sine of an angle (in degrees)"""

    angle = angle % 360
    if angle in (0, 180):
        return 0.0
    return _math.sin(angle * _dg)


def tan(angle):
    """Tangent of an angle (in degrees)"""

    angle = angle % 180
    if angle == 45:
        return 1.0
    return _math.tan(angle * _dg)


# Other functions
def sqrt(x: Real) -> Real:
    """
    Return the square root of a positive number.
    """
    return _math.sqrt(x)


def exp(x: Real) -> Real:
    """
    Return the exponential of a number.
    """
    return _math.exp(x)


def log(x: Real) -> Real:
    """
    Return the natural logarithm of x.

    Aliases: log | ln
    """
    return _math.log(x)


ln = log


def log10(x: Real) -> Real:
    """
    Return the logarithm of x in base 10.
    """
    return _math.log10(x)


def log2(x: Real) -> Real:
    """
    Return the logarithm of x in base 2.
    """
    return _math.log2(x)


def sign(x):
    """
    Return 1 if x is positive, -1 if it is negative and 0 if it is null.

    Examples:
        >>> sign(-32.0)
        -1
    """
    try:
        if x == 0:
            return 0
        elif x > 0:
            return 1
        elif x < 0:
            return -1
    except TypeError:
        pass
    raise ValueError(sign.ERROR)


sign.ERROR = 'argument does not have a well defined sign'

# Rounding
_abs, _round = abs, round


def abs(x) -> Number:
    """
    Return the absolute value of the argument.
    """
    return _abs(x)


def round(number: Number, ndigits=None) -> Number:
    """
    Round a number to a given precision in decimal digits (default 0 digits).
    ndigits may be negative.

    Examples:
        >>> round(1.9)
        2
        >>> round(3.141516, 2)
        3.14
    """
    if ndigits is None:
        return _round(number)
    return _round(number, ndigits)


def ceil(number: Real) -> int:
    """
    Return the ceiling of x as an Integral.
    This is the smallest integer >= x.
    """
    return _math.ceil(number)


def trunc(number: Real) -> int:
    """
    Truncates x to the nearest Integral toward 0.
    """
    return _math.trunc(number)


# Operations on collections of numbers
_min, _max, _sum = min, max, sum


def sum(seq, start=0.0):
    """
    Return the sum of all numbers in the sequence.
    """
    return _sum(seq, start)


def product(seq, start=1.0):
    """
    Return the product of all numbers in the sequence.
    """

    result = start
    for x in seq:
        result *= x
    return result


def min(*args, **kwargs):
    """
    Return the minimum value in the arguments.

    It called with a single sequence, return the minimum value on that sequence.
    """
    return _min(*args)


def max(*args, **kwargs):
    """
    Return the maximum value in the arguments.

    It called with a single sequence, return the maximum value on that sequence.
    """
    return _max(*args)


# Random numbers
def dice(n=6):
    """
    Simulate a dice trow (return a random number between 1 and 6.

    Call with an explicit argument to throw a dice with a different number of
    faces

    Examples:
        >>> dice(20)                                            # doctest: +SKIP
        13
    """
    return _random.randint(1, n)


def random():
    """
    Return a random number between 0 and 1.
    """
    return _random.random()


def randint(a, b):
    """
    Return a random integer between a and b (inclusive).
    """
    return _random.randint(a, b)


# Vectors and linear algebra
class Vec(_namedtuple('Vec', ['x', 'y'])):
    """
    A tuple-based 2D vector.

    Supports all basic arithmetic operations.
    """

    @classmethod
    def from_angle(cls, angle, length=1):
        """
        Creates vector from angle and length.
        """
        return cls(cos(angle), sin(angle))

    def __new__(cls, x, y):
        return super(Vec, cls).__new__(cls, x + 0., y + 0.)

    def __repr__(self):
        return '(%g, %g)' % (self.x, self.y)

    def __add__(self, other):
        x, y = other
        return Vec(x + self.x, y + self.y)

    def __sub__(self, other):
        x, y = other
        return Vec(self.x - x, self.y - y)

    def __mul__(self, other):
        return Vec(other * self.x, other * self.y)

    def __truediv__(self, other):
        return Vec(self.x / other, self.y / other)

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self * (-1) + other

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __abs__(self):
        return _math.sqrt(self.x ** 2 + self.y ** 2)

    def norm(self):
        """
        Vector norm.
        """
        return self.__abs__()

    def normalized(self):
        """
        Return unity vector.
        """
        return self / abs(self)

    def perp(self, invert=False):
        """
        Returns a perpendicular vector rotated 90 degrees counter-clockwise.
        """

        if invert:
            return Vec(self.y, -self.x)
        return Vec(-self.y, self.x)

    def rotate(self, angle):
        """
        Return rotated vector by the given angle.
        """

        x, y = self
        c, s = cos(angle), sin(angle)
        return Vec(x * c - y * s, x * s + y * c)


def vec(x, y=None):
    """
    Return a vector with the given (x, y) components.
    """

    if y is None:
        x, y = x
    return Vec(x, y)


def dot(u, v):
    """
    The dot product (scalar product) of two vectors.
    """
    return _sum(x * y for (x, y) in zip(u, v))
