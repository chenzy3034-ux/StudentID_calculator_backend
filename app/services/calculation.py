from app.calculator import evaluate_expression
from app.database import CalculationHistory, HistoryRepository


def calculate_and_store(
    expression: str,
    repository: HistoryRepository,
) -> CalculationHistory:
    """Evaluate an expression and persist it only after evaluation succeeds."""
    result = evaluate_expression(expression)
    return repository.insert(expression=expression, result=result)
