from app.database.connection import get_database_path
from app.database.history import HistoryRepository
from app.database.models import CalculationHistory


def get_history_repository() -> HistoryRepository:
    return HistoryRepository(get_database_path())


__all__ = [
    "CalculationHistory",
    "HistoryRepository",
    "get_history_repository",
]
