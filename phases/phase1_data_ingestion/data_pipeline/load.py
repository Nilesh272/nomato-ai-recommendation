from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from phases.phase1_data_ingestion.data_pipeline.validate import ValidationReport


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS restaurants (
    restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    locality TEXT,
    cuisines TEXT,
    avg_cost_for_two REAL,
    rating REAL,
    votes INTEGER,
    tags TEXT,
    source_dataset TEXT NOT NULL,
    source_split TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants(city);
CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants(rating);
CREATE INDEX IF NOT EXISTS idx_restaurants_cost ON restaurants(avg_cost_for_two);
CREATE INDEX IF NOT EXISTS idx_restaurants_cuisines ON restaurants(cuisines);

CREATE TABLE IF NOT EXISTS etl_runs (
    run_id TEXT PRIMARY KEY,
    source_dataset TEXT NOT NULL,
    source_split TEXT NOT NULL,
    source_fingerprint TEXT,
    status TEXT NOT NULL,
    total_rows INTEGER NOT NULL,
    valid_rows INTEGER NOT NULL,
    invalid_rows INTEGER NOT NULL,
    quality_report_json TEXT NOT NULL,
    error_message TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT
);
"""


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    _migrate_etl_runs(conn)
    conn.commit()


def _migrate_etl_runs(conn: sqlite3.Connection) -> None:
    """Best-effort migrations for additive columns in SQLite."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(etl_runs)").fetchall()}
    if "source_fingerprint" not in cols:
        conn.execute("ALTER TABLE etl_runs ADD COLUMN source_fingerprint TEXT;")


def start_run(
    conn: sqlite3.Connection,
    run_id: str,
    source_dataset: str,
    source_split: str,
    source_fingerprint: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO etl_runs (
            run_id, source_dataset, source_split, source_fingerprint, status, total_rows, valid_rows, invalid_rows,
            quality_report_json, started_at
        ) VALUES (?, ?, ?, ?, 'running', 0, 0, 0, ?, ?)
        """,
        (run_id, source_dataset, source_split, source_fingerprint, json.dumps({}), _utc_now_iso()),
    )
    conn.commit()


def finish_run(
    conn: sqlite3.Connection,
    run_id: str,
    status: str,
    total_rows: int,
    valid_rows: int,
    report: ValidationReport | dict[str, Any],
    error_message: str | None = None,
) -> None:
    report_dict: dict[str, Any]
    if isinstance(report, ValidationReport):
        report_dict = report.__dict__
    else:
        report_dict = report

    conn.execute(
        """
        UPDATE etl_runs
        SET status = ?, total_rows = ?, valid_rows = ?, invalid_rows = ?, quality_report_json = ?,
            error_message = ?, completed_at = ?
        WHERE run_id = ?
        """,
        (
            status,
            total_rows,
            valid_rows,
            total_rows - valid_rows,
            json.dumps(report_dict),
            error_message,
            _utc_now_iso(),
            run_id,
        ),
    )
    conn.commit()


def replace_restaurants(
    conn: sqlite3.Connection,
    df: pd.DataFrame,
    source_dataset: str,
    source_split: str,
) -> None:
    payload = df.copy()
    payload["source_dataset"] = source_dataset
    payload["source_split"] = source_split
    with conn:
        conn.execute("DELETE FROM restaurants")
        payload.to_sql("restaurants", conn, if_exists="append", index=False)

