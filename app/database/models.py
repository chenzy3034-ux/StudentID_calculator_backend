from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationHistory:
    id: int
    expression: str
    result: str
    created_at: str
