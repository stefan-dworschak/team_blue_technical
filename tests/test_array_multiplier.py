import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from array_multiplier import ArrayMultiplier, ArrayNumber

FACTORIAL_100 = (
    "93326215443944152681699238856266700490715968264381621468592963895217599993229915"
    "608941463976156518286253697920827223758251185210916864000000000000000000000000"
)


class TestArrayNumber(unittest.TestCase):
    def test_from_int(self) -> None:
        num = ArrayNumber.from_int(123)
        self.assertEqual(num.digits, [1, 2, 3])

    def test_from_int_zero(self) -> None:
        num = ArrayNumber.from_int(0)
        self.assertEqual(num.digits, [0])

    def test_from_int_single_digit(self) -> None:
        num = ArrayNumber.from_int(7)
        self.assertEqual(num.digits, [7])

    def test_str(self) -> None:
        self.assertEqual(str(ArrayNumber.from_int(456)), "456")
        self.assertEqual(str(ArrayNumber.from_int(0)), "0")

    def test_addition_simple(self) -> None:
        a = ArrayNumber.from_int(123)
        b = ArrayNumber.from_int(456)
        self.assertEqual(str(a + b), "579")

    def test_addition_with_carry(self) -> None:
        a = ArrayNumber.from_int(99)
        b = ArrayNumber.from_int(1)
        self.assertEqual(str(a + b), "100")

    def test_addition_different_lengths(self) -> None:
        a = ArrayNumber.from_int(1000)
        b = ArrayNumber.from_int(1)
        self.assertEqual(str(a + b), "1001")

    def test_addition_with_zero(self) -> None:
        a = ArrayNumber.from_int(42)
        b = ArrayNumber.from_int(0)
        self.assertEqual(str(a + b), "42")

    def test_equality(self) -> None:
        self.assertEqual(ArrayNumber.from_int(42), ArrayNumber.from_int(42))
        self.assertNotEqual(ArrayNumber.from_int(42), ArrayNumber.from_int(43))


class TestArrayMultiplier(unittest.TestCase):
    def setUp(self) -> None:
        self.multiplier = ArrayMultiplier()

    def test_simple_multiplication(self) -> None:
        a = ArrayNumber.from_int(15)
        b = ArrayNumber.from_int(2)
        result = self.multiplier.multiply(a, b)
        self.assertEqual(str(result), "30")

    def test_multiply_by_zero(self) -> None:
        a = ArrayNumber.from_int(123)
        b = ArrayNumber.from_int(0)
        self.assertEqual(str(self.multiplier.multiply(a, b)), "0")

    def test_multiply_by_one(self) -> None:
        a = ArrayNumber.from_int(999)
        b = ArrayNumber.from_int(1)
        self.assertEqual(str(self.multiplier.multiply(a, b)), "999")

    def test_multiply_single_digits(self) -> None:
        a = ArrayNumber.from_int(7)
        b = ArrayNumber.from_int(8)
        self.assertEqual(str(self.multiplier.multiply(a, b)), "56")

    def test_multiply_larger_numbers(self) -> None:
        a = ArrayNumber.from_int(123)
        b = ArrayNumber.from_int(456)
        self.assertEqual(str(self.multiplier.multiply(a, b)), "56088")

    def test_multiply_commutative(self) -> None:
        a = ArrayNumber.from_int(37)
        b = ArrayNumber.from_int(89)
        r1 = self.multiplier.multiply(a, b)
        r2 = self.multiplier.multiply(b, a)
        self.assertEqual(str(r1), str(r2))


class TestFactorial(unittest.TestCase):
    def setUp(self) -> None:
        self.multiplier = ArrayMultiplier()

    def test_factorial_0(self) -> None:
        self.assertEqual(str(self.multiplier.factorial(0)), "1")

    def test_factorial_1(self) -> None:
        self.assertEqual(str(self.multiplier.factorial(1)), "1")

    def test_factorial_5(self) -> None:
        self.assertEqual(str(self.multiplier.factorial(5)), "120")

    def test_factorial_10(self) -> None:
        self.assertEqual(str(self.multiplier.factorial(10)), "3628800")

    def test_factorial_100(self) -> None:
        result = str(self.multiplier.factorial(100))
        self.assertEqual(result, FACTORIAL_100)
