"""SQLite database helpers for persistent backend storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    """Thin SQLite wrapper for schema initialization and connections."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        """Create required tables if they do not already exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    request_payload TEXT NOT NULL,
                    summary_payload TEXT NOT NULL,
                    market_snapshot_payload TEXT NOT NULL,
                    signals_payload TEXT NOT NULL,
                    patterns_payload TEXT NOT NULL,
                    pipeline_payload TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    alert TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
                );

                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    symbols TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor = connection.execute("PRAGMA table_info(alerts)")
            columns = [col["name"] for col in cursor.fetchall()]
            if "updated_at" not in columns:
                connection.execute("ALTER TABLE alerts ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")

    def connect(self) -> sqlite3.Connection:
        """Return a SQLite connection configured for dict-like row access."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection
