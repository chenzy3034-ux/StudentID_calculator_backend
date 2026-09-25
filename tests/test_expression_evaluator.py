from decimal import Decimal

import pytest

from app.calculator import (
    DivisionByZeroExpressionError,
    InvalidExpressionError,
    evaluate_expression,
)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 + 2", Decimal("3")),
        ("10 - 3", Decimal("7")),
        ("4 * 5", Decimal("20")),
        ("10 / 2", Decimal("5")),
        ("1 + 2 * 3", Decimal("7")),
        ("(1 + 2) * 3", Decimal("9")),
        ("-5 + 8", Decimal("3")),
        ("3 * -2", Decimal("-6")),
        ("3.5 + 1.2", Decimal("4.7")),
        ("-(2 + 3)", Decimal("-5")),
        ("+(2 + 3)", Decimal("5")),
    ],
)
def test_valid_expressions(expression: str, expected: Decimal) -> None:
    assert evaluate_expression(expression) == expected


def test_division_by_zero() -> None:
    with pytest.raises(DivisionByZeroExpressionError):
        evaluate_expression("10 / 0")


@pytest.mark.parametrize("expression", ["1 + * 2", "", "   "])
def test_invalid_expressions(expression: str) -> None:
    with pytest.raises(InvalidExpressionError):
        evaluate_expression(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "1 + unknown",
        "1..2 + 3",
        "(1 + 2",
        "1 2",
        "2(3)",
        "()",
    ],
)
def test_additional_invalid_expressions(expression: str) -> None:
    with pytest.raises(InvalidExpressionError):
        evaluate_expression(expression)
