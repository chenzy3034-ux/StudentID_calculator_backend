from app.database import CalculationHistory, HistoryRepository


class HistoryNotFoundError(LookupError):
    """Raised when a requested calculation history record does not exist."""


def list_history(repository: HistoryRepository) -> list[CalculationHistory]:
    return repository.query_all()


def delete_history(history_id: int, repository: HistoryRepository) -> None:
    if not repository.delete_by_id(history_id):
        raise HistoryNotFoundError(f"History record {history_id} does not exist")
