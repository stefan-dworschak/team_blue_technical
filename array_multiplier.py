# Enables forward self-references (e.g. ArrayNumber returning ArrayNumber) without quoting.
from __future__ import annotations

import argparse


class ArrayNumber:
    """Represents a non-negative integer as a list of single digits (big-endian).

    Supports addition via the + operator.
    """

    def __init__(self, digits: list[int]) -> None:
        self._digits = digits if digits else [0]

    @classmethod
    def from_int(cls, value: int) -> ArrayNumber:
        if value == 0:
            return cls([0])

        digits = []
        while value > 0:
            digits.append(value % 10)
            value //= 10

        digits.reverse()
        return cls(digits)

    @property
    def digits(self) -> list[int]:
        return list(self._digits)

    def __add__(self, other: ArrayNumber) -> ArrayNumber:
        """Add two ArrayNumbers using only single-digit addition with carry."""
        a = list(reversed(self._digits))
        b = list(reversed(other._digits))
        length = max(len(a), len(b))
        result: list[int] = []
        carry = 0

        for i in range(length):
            digit_a = a[i] if i < len(a) else 0
            digit_b = b[i] if i < len(b) else 0
            total = digit_a + digit_b + carry
            result.append(total % 10)
            carry = total // 10

        if carry:
            result.append(carry)

        result.reverse()
        return ArrayNumber(result)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ArrayNumber):
            return self._digits == other._digits
        return NotImplemented

    def __repr__(self) -> str:
        return f"ArrayNumber({self._digits})"

    def __str__(self) -> str:
        return "".join(str(d) for d in self._digits)


class ArrayMultiplier:
    """Multiplies two ArrayNumbers using only addition.

    Uses long multiplication: for each digit d of the multiplier at position p,
    add the multiplicand d times, shifted left by p positions.
    """

    def multiply(self, a: ArrayNumber, b: ArrayNumber) -> ArrayNumber:
        result = ArrayNumber([0])
        b_digits = list(reversed(b.digits))

        for position, digit in enumerate(b_digits):
            if digit == 0:
                continue
            shifted = ArrayNumber(a.digits + [0] * position)
            for _ in range(digit):
                result = result + shifted

        return result

    def factorial(self, n: int) -> ArrayNumber:
        """Compute n! using array-based multiplication."""
        result = ArrayNumber([1])
        for i in range(2, n + 1):
            result = self.multiply(result, ArrayNumber.from_int(i))
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Array-based multiplication using only addition.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    factorial_parser = subparsers.add_parser("factorial", help="Compute n! using array-based multiplication.")
    factorial_parser.add_argument("n", type=int, help="Non-negative integer to compute the factorial of.")

    multiply_parser = subparsers.add_parser("multiply", help="Multiply two non-negative integers.")
    multiply_parser.add_argument("a", type=int, help="First non-negative integer.")
    multiply_parser.add_argument("b", type=int, help="Second non-negative integer.")

    args = parser.parse_args()
    multiplier = ArrayMultiplier()

    if args.command == "factorial":
        if args.n < 0:
            parser.error("n must be non-negative")
        print(multiplier.factorial(args.n))
    elif args.command == "multiply":
        if args.a < 0 or args.b < 0:
            parser.error("a and b must be non-negative")
        result = multiplier.multiply(ArrayNumber.from_int(args.a), ArrayNumber.from_int(args.b))
        print(result)
