from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum, auto

from app.calculator.errors import InvalidExpressionError


class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    END = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: Decimal | None = None


_SINGLE_CHARACTER_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
}


def tokenize(expression: str) -> list[Token]:
    """Convert a mathematical expression into a restricted token stream."""
    if not expression or expression.isspace():
        raise InvalidExpressionError("Expression cannot be empty")

    tokens: list[Token] = []
    position = 0

    while position < len(expression):
        character = expression[position]

        if character.isspace():
            position += 1
            continue

        token_type = _SINGLE_CHARACTER_TOKENS.get(character)
        if token_type is not None:
            tokens.append(Token(token_type))
            position += 1
            continue

        if character.isdigit() or character == ".":
            start = position
            decimal_points = 0
            digit_count = 0

            while position < len(expression):
                current = expression[position]
                if current.isdigit():
                    digit_count += 1
                    position += 1
                elif current == ".":
                    decimal_points += 1
                    position += 1
                else:
                    break

            number_text = expression[start:position]
            if decimal_points > 1 or digit_count == 0:
                raise InvalidExpressionError(f"Invalid number: {number_text}")

            try:
                value = Decimal(number_text)
            except InvalidOperation as error:
                message = f"Invalid number: {number_text}"
                raise InvalidExpressionError(message) from error

            tokens.append(Token(TokenType.NUMBER, value))
            continue

        raise InvalidExpressionError(
            f"Unexpected character at position {position}: {character!r}"
        )

    tokens.append(Token(TokenType.END))
    return tokens
