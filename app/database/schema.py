from pathlib import Path

from app.database.connection import connect_database


CREATE_CALCULATION_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS calculation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def initialize_database(database_path: str | Path) -> None:
    """Create all required database tables if they do not already exist."""
    with connect_database(database_path) as connection:
        connection.execute(CREATE_CALCULATION_HISTORY_TABLE)
