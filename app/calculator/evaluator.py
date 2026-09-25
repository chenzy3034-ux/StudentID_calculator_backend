from decimal import Decimal

from app.calculator.errors import DivisionByZeroExpressionError
from app.calculator.parser import BinaryNode, ExpressionNode, NumberNode, UnaryNode
from app.calculator.tokenizer import TokenType


def evaluate(node: ExpressionNode) -> Decimal:
    """Evaluate a parsed expression tree without executing user-provided code."""
    if isinstance(node, NumberNode):
        return node.value

    if isinstance(node, UnaryNode):
        operand = evaluate(node.operand)
        return operand if node.operator is TokenType.PLUS else -operand

    left = evaluate(node.left)
    right = evaluate(node.right)

    if node.operator is TokenType.PLUS:
        return left + right
    if node.operator is TokenType.MINUS:
        return left - right
    if node.operator is TokenType.MULTIPLY:
        return left * right
    if right == 0:
        raise DivisionByZeroExpressionError("Division by zero is not allowed")
    return left / right
