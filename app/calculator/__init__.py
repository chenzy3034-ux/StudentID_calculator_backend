from decimal import Decimal

from app.calculator.errors import (
    DivisionByZeroExpressionError,
    ExpressionError,
    InvalidExpressionError,
)
from app.calculator.evaluator import evaluate
from app.calculator.parser import Parser
from app.calculator.tokenizer import tokenize


def evaluate_expression(expression: str) -> Decimal:
    """Tokenize, parse, and safely evaluate a calculator expression."""
    return evaluate(Parser(tokenize(expression)).parse())


__all__ = [
    "DivisionByZeroExpressionError",
    "ExpressionError",
    "InvalidExpressionError",
    "evaluate_expression",
]
