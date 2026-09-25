import sqlite3
from decimal import Decimal
from pathlib import Path

from app.database.history import HistoryRepository


def create_repository(database_path: Path) -> HistoryRepository:
    repository = HistoryRepository(database_path)
    repository.initialize()
    return repository


def test_initialize_creates_calculation_history_table(tmp_path: Path) -> None:
    database_path = tmp_path / "calculator.db"
    create_repository(database_path)

    with sqlite3.connect(database_path) as connection:
        columns = connection.execute(
            "PRAGMA table_info(calculation_history)"
        ).fetchall()

    assert [column[1] for column in columns] == [
        "id",
        "expression",
        "result",
        "created_at",
    ]


def test_insert_history(tmp_path: Path) -> None:
    repository = create_repository(tmp_path / "calculator.db")

    history = repository.insert(
        "1 + 2",
        Decimal("3"),
        created_at="2026-09-25T01:00:00+00:00",
    )

    assert history.id == 1
    assert history.expression == "1 + 2"
    assert history.result == "3"
    assert history.created_at == "2026-09-25T01:00:00+00:00"


def test_query_history(tmp_path: Path) -> None:
    repository = create_repository(tmp_path / "calculator.db")
    older = repository.insert(
        "1 + 2",
        "3",
        created_at="2026-09-25T01:00:00+00:00",
    )
    newer = repository.insert(
        "4 * 5",
        "20",
        created_at="2026-09-25T02:00:00+00:00",
    )

    assert repository.query_all() == [newer, older]


def test_history_persists_across_repository_instances(tmp_path: Path) -> None:
    database_path = tmp_path / "calculator.db"
    first_process = create_repository(database_path)
    inserted = first_process.insert("(1 + 2) * 3", "9")

    restarted_process = create_repository(database_path)

    assert restarted_process.query_all() == [inserted]


def test_delete_history_by_id(tmp_path: Path) -> None:
    repository = create_repository(tmp_path / "calculator.db")
    retained = repository.insert("1 + 2", "3")
    deleted = repository.insert("10 / 2", "5")

    assert repository.delete_by_id(deleted.id) is True
    assert repository.query_all() == [retained]


def test_delete_nonexistent_history_id(tmp_path: Path) -> None:
    repository = create_repository(tmp_path / "calculator.db")

    assert repository.delete_by_id(999) is False
    assert repository.query_all() == []
