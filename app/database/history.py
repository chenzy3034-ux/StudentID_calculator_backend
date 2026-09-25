import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from app.database.connection import connect_database
from app.database.models import CalculationHistory
from app.database.schema import initialize_database


class HistoryRepository:
    """Persist calculation history in a SQLite database file."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    def initialize(self) -> None:
        initialize_database(self._database_path)

    def insert(
        self,
        expression: str,
        result: Decimal | str,
        created_at: str | None = None,
    ) -> CalculationHistory:
        timestamp = created_at or datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )
        result_text = str(result)

        with connect_database(self._database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO calculation_history (expression, result, created_at)
                VALUES (?, ?, ?)
                """,
                (expression, result_text, timestamp),
            )
            history_id = cursor.lastrowid

        if history_id is None:
            raise RuntimeError("SQLite did not return an id for the inserted history")

        return CalculationHistory(
            id=history_id,
            expression=expression,
            result=result_text,
            created_at=timestamp,
        )

    def query_all(self) -> list[CalculationHistory]:
        with connect_database(self._database_path) as connection:
            rows = connection.execute(
                """
                SELECT id, expression, result, created_at
                FROM calculation_history
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

        return [self._row_to_history(row) for row in rows]

    def delete_by_id(self, history_id: int) -> bool:
        with connect_database(self._database_path) as connection:
            cursor = connection.execute(
                "DELETE FROM calculation_history WHERE id = ?",
                (history_id,),
            )
            return cursor.rowcount > 0

    @staticmethod
    def _row_to_history(row: sqlite3.Row) -> CalculationHistory:
        return CalculationHistory(
            id=row["id"],
            expression=row["expression"],
            result=row["result"],
            created_at=row["created_at"],
        )
