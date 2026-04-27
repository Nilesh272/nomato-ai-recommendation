import sqlite3
from pathlib import Path

from phases.phase3_candidate_retrieval.backend.schemas.retrieval import ShortlistRequest
from phases.phase3_candidate_retrieval.backend.services.retrieval import get_shortlist


def _seed_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE restaurants (
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
        """
    )
    conn.executemany(
        """
        INSERT INTO restaurants
        (name, city, locality, cuisines, avg_cost_for_two, rating, votes, tags, source_dataset, source_split)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'test', 'train')
        """,
        [
            ("Spice Hub", "Bangalore", "Indiranagar", "North Indian, Chinese", 900, 4.6, 120, "quick service, family friendly"),
            ("Pasta Point", "Bangalore", "Koramangala", "Italian", 1100, 4.2, 80, "cozy"),
            ("Budget Bites", "Bangalore", "HSR", "North Indian", 450, 4.1, 200, "quick service"),
            ("Other City Place", "Delhi", "CP", "North Indian", 900, 4.8, 90, "family friendly"),
        ],
    )
    conn.commit()
    conn.close()


def test_shortlist_applies_hard_filters_and_scoring(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _seed_db(db_path)

    req = ShortlistRequest(
        location="Bangalore",
        budget_tier="medium",
        cuisines=["north indian"],
        min_rating=4.0,
        additional_preferences=["quick service"],
        max_results=5,
        shortlist_size=20,
    )
    results = get_shortlist(req, db_path=db_path)
    assert len(results) >= 1
    assert results[0].name == "Spice Hub"
    assert "within_budget" in results[0].matched_signals
    assert "cuisine_match" in results[0].matched_signals
    assert "preference_match" in results[0].matched_signals


def test_shortlist_excludes_city_mismatch(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _seed_db(db_path)

    req = ShortlistRequest(
        location="Delhi",
        budget_tier="medium",
        cuisines=["north indian"],
        min_rating=4.0,
        additional_preferences=[],
        max_results=5,
        shortlist_size=20,
    )
    results = get_shortlist(req, db_path=db_path)
    assert len(results) == 1
    assert results[0].city == "Delhi"

