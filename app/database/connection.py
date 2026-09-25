import os
import sqlite3
from pathlib import Path


_BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = _BACKEND_ROOT / "data" / "calculator.db"


def get_database_path() -> Path:
    """Return the configured persistent SQLite database file path."""
    configured_path = os.getenv("CALCULATOR_DATABASE_PATH")
    if configured_path:
        return Path(configured_path).expanduser()
    return DEFAULT_DATABASE_PATH


def connect_database(database_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite file connection configured for named-column access."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
