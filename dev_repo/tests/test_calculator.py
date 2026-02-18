import pytest
from src.calculator import add, subtract, multiply, divide, calculate


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -4) == -5


def test_subtract_positive_numbers():
    assert subtract(10, 7) == 3


def test_subtract_negative_result():
    assert subtract(3, 5) == -2


def test_multiply_positive_numbers():
    assert multiply(4, 5) == 20


def test_multiply_by_zero():
    assert multiply(7, 0) == 0


def test_divide_positive_numbers():
    assert divide(10, 2) == 5.0


def test_divide_non_integer_result():
    assert divide(7, 2) == 3.5


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)


def test_invalid_operator():
    with pytest.raises(ValueError):
        calculate(2, 3, '^')
