import pytest

from transpyler import math
from transpyler.math import sin, cos, tan, sign, product, Vec, vec, dot


class TestMathFunctions:
    def test_trigonometric_functions(self):
        assert cos(0) == -cos(180) == 1
        assert cos(90) == cos(90 + 180) == 0

        assert sin(0) == sin(180) == 0
        assert sin(90) == -sin(90 + 180) == 1

        assert tan(0) == 0
        assert tan(45) == 1
        assert tan(90) > 1e10

    def test_common_functions(self):
        assert math.sqrt(4) == 2.0
        assert math.exp(0) == 1
        assert math.log(math.e) == 1
        assert math.log10(10) == 1
        assert math.log2(2) == 1

    def test_truncation_funcs(self):
        assert math.abs(-1) == math.abs(1) == 1
        assert math.trunc(1.2) == 1.0
        assert math.round(1.234, 2) == 1.23
        assert math.round(1.2) == 1
        assert math.round(1.9) == 2
        assert math.ceil(1.2) == 2.0

    def test_seq_funcs(self):
        assert math.sum([1, 2, 3, 4]) == 10
        assert math.sum([]) == 0
        assert product([1, 2, 3]) == 6
        assert product([]) == 1
        assert min([1, 2, 3]) == 1
        assert min(1, 2, 3) == 1
        assert max([1, 2, 3]) == 3
        assert max(1, 2, 3) == 3

    def test_random_functions(self):
        for _ in range(30):
            assert 1 <= math.dice() <= 6
            assert 0 <= math.random() <= 1.0
            assert 1 <= math.randint(1, 10) <= 10

        assert {math.randint(1, 2) for _ in range(20)} == {1, 2}

    def test_sign(self):
        assert sign(0) == 0
        assert sign(1) == sign(1.5) == 1
        assert sign(-1) == sign(-1.5) == -1

    def test_basic_vec_properties(self):
        u = Vec(1, 0)
        v = Vec(0, 1)
        assert repr(u) == '(1, 0)'
        assert 2 * u == u * 2 == Vec(2, 0)
        assert u + v == Vec(1, 1)
        assert u - u == Vec(0, 0)
        assert -u == (-1) * u
        assert abs(u) == abs(v) == v.norm() == 1
        assert u == u.normalized()
        assert u == (2 * u).normalized()
        assert u.rotate(90) == v
        assert u.perp() == v
        assert Vec.from_angle(90) == v
        assert (1, 0) + u == 2 * u
        assert (1, 0) - u == 0 * u
        assert u.perp() == -u.perp(invert=True)

    def test_vec_function(self):
        assert vec((1, 2)) == vec(1, 2) == Vec(1, 2)

    def test_dot_product(self):
        assert dot(vec(0, 1), vec(1, 0)) == 0

    def test_sign_error(self):
        with pytest.raises(ValueError):
            sign([])
