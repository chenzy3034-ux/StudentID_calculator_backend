from dataclasses import dataclass
from decimal import Decimal

from app.calculator.errors import InvalidExpressionError
from app.calculator.tokenizer import Token, TokenType


@dataclass(frozen=True)
class NumberNode:
    value: Decimal


@dataclass(frozen=True)
class UnaryNode:
    operator: TokenType
    operand: "ExpressionNode"


@dataclass(frozen=True)
class BinaryNode:
    left: "ExpressionNode"
    operator: TokenType
    right: "ExpressionNode"


ExpressionNode = NumberNode | UnaryNode | BinaryNode


class Parser:
    """Parse calculator tokens with a recursive-descent grammar."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._position = 0

    def parse(self) -> ExpressionNode:
        expression = self._parse_expression()
        if self._current.type is not TokenType.END:
            raise InvalidExpressionError("Unexpected token after expression")
        return expression

    @property
    def _current(self) -> Token:
        return self._tokens[self._position]

    def _advance(self) -> Token:
        token = self._current
        self._position += 1
        return token

    def _parse_expression(self) -> ExpressionNode:
        node = self._parse_term()

        while self._current.type in (TokenType.PLUS, TokenType.MINUS):
            operator = self._advance().type
            node = BinaryNode(node, operator, self._parse_term())

        return node

    def _parse_term(self) -> ExpressionNode:
        node = self._parse_unary()

        while self._current.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self._advance().type
            node = BinaryNode(node, operator, self._parse_unary())

        return node

    def _parse_unary(self) -> ExpressionNode:
        if self._current.type in (TokenType.PLUS, TokenType.MINUS):
            operator = self._advance().type
            return UnaryNode(operator, self._parse_unary())

        return self._parse_primary()

    def _parse_primary(self) -> ExpressionNode:
        if self._current.type is TokenType.NUMBER:
            token = self._advance()
            if token.value is None:
                raise InvalidExpressionError("Number token has no value")
            return NumberNode(token.value)

        if self._current.type is TokenType.LEFT_PAREN:
            self._advance()
            node = self._parse_expression()
            if self._current.type is not TokenType.RIGHT_PAREN:
                raise InvalidExpressionError("Missing closing parenthesis")
            self._advance()
            return node

        raise InvalidExpressionError("Expected a number or opening parenthesis")
