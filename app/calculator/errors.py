class ExpressionError(ValueError):
    """Base exception for errors caused by a user expression."""


class InvalidExpressionError(ExpressionError):
    """Raised when an expression cannot be tokenized or parsed."""


class DivisionByZeroExpressionError(ExpressionError):
    """Raised when an expression attempts to divide by zero."""
