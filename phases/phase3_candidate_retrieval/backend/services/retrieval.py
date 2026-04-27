from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from phases.phase2_user_input_api.backend.services.normalizer import normalize_preferences
from phases.phase3_candidate_retrieval.backend.schemas.retrieval import Candidate, ShortlistRequest

DEFAULT_DB_PATH = Path("phases/phase1_data_ingestion/data_pipeline/zomato.db")
MODEL_CANDIDATE_LIMIT = 25


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def _build_query(req: ShortlistRequest, city: str) -> tuple[str, list[Any]]:
    loc = city.lower()
    sql = """
        SELECT restaurant_id, name, city, locality, cuisines, rating, avg_cost_for_two, votes, tags
        FROM restaurants
        WHERE (
            lower(city) = ?
            OR lower(locality) LIKE ?
            OR lower(city) LIKE ?
        )
          AND (rating IS NULL OR rating >= ?)
    """
    params: list[Any] = [loc, f"%{loc}%", f"%{loc}%", req.min_rating]

    normalized = normalize_preferences(req)
    if normalized.budget_max is None:
        sql += " AND (avg_cost_for_two IS NULL OR avg_cost_for_two >= ?)"
        params.append(normalized.budget_min)
    else:
        sql += " AND (avg_cost_for_two IS NULL OR (avg_cost_for_two >= ? AND avg_cost_for_two <= ?))"
        params.extend([normalized.budget_min, normalized.budget_max])

    if normalized.cuisines:
        cuisine_clauses = []
        for cuisine in normalized.cuisines:
            cuisine_clauses.append("lower(cuisines) LIKE ?")
            params.append(f"%{cuisine.lower()}%")
        sql += " AND (" + " OR ".join(cuisine_clauses) + ")"

    return sql, params


def _compute_signals_and_score(row: dict[str, Any], req: ShortlistRequest) -> tuple[list[str], float]:
    normalized = normalize_preferences(req)
    matched_signals: list[str] = []

    rating = float(row["rating"]) if row.get("rating") is not None else None
    cost = float(row["avg_cost_for_two"]) if row.get("avg_cost_for_two") is not None else None

    rating_score = (rating / 5.0) * 40.0 if rating is not None else 10.0
    if rating is not None and rating >= normalized.min_rating:
        matched_signals.append("rating_match")

    cuisine_score = 0.0
    cuisines_blob = (row.get("cuisines") or "").lower()
    if normalized.cuisines:
        matched_count = sum(1 for c in normalized.cuisines if c.lower() in cuisines_blob)
        cuisine_score = (matched_count / len(normalized.cuisines)) * 30.0
        if matched_count > 0:
            matched_signals.append("cuisine_match")
    else:
        cuisine_score = 15.0

    budget_score = 5.0
    if cost is None:
        budget_score = 5.0
    elif normalized.budget_max is None and cost >= normalized.budget_min:
        budget_score = 20.0
        matched_signals.append("within_budget")
    elif normalized.budget_max is not None and normalized.budget_min <= cost <= normalized.budget_max:
        budget_score = 20.0
        matched_signals.append("within_budget")
    else:
        budget_score = 5.0

    preference_score = 0.0
    searchable = " ".join(
        [
            str(row.get("name") or ""),
            str(row.get("locality") or ""),
            str(row.get("cuisines") or ""),
            str(row.get("tags") or ""),
        ]
    ).lower()
    if normalized.additional_preferences:
        matched_pref = sum(1 for pref in normalized.additional_preferences if pref.replace("_", " ") in searchable)
        preference_score = (matched_pref / len(normalized.additional_preferences)) * 10.0
        if matched_pref > 0:
            matched_signals.append("preference_match")

    score = round(rating_score + cuisine_score + budget_score + preference_score, 2)
    return matched_signals, score


def _apply_diversity_limit(candidates: list[Candidate], shortlist_size: int) -> list[Candidate]:
    locality_counter: dict[str, int] = defaultdict(int)
    selected: list[Candidate] = []
    overflow: list[Candidate] = []

    for candidate in candidates:
        key = (candidate.city or "").lower() + "|" + ((candidate.cuisines or "").split(",")[0].strip().lower())
        if locality_counter[key] < 3:
            selected.append(candidate)
            locality_counter[key] += 1
        else:
            overflow.append(candidate)

        if len(selected) >= shortlist_size:
            return selected

    for candidate in overflow:
        if len(selected) >= shortlist_size:
            break
        selected.append(candidate)

    return selected


def get_shortlist(req: ShortlistRequest, db_path: Path = DEFAULT_DB_PATH) -> list[Candidate]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        sql, params = _build_query(req, req.location)
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    scored: list[Candidate] = []
    for row in rows:
        as_dict = _row_to_dict(row)
        signals, score = _compute_signals_and_score(as_dict, req)
        scored.append(
            Candidate(
                candidate_id=int(as_dict["restaurant_id"]),
                name=str(as_dict["name"]),
                city=str(as_dict["city"]),
                locality=as_dict.get("locality"),
                cuisines=as_dict.get("cuisines"),
                rating=float(as_dict["rating"]) if as_dict.get("rating") is not None else None,
                avg_cost_for_two=float(as_dict["avg_cost_for_two"]) if as_dict.get("avg_cost_for_two") is not None else None,
                votes=int(as_dict["votes"]) if as_dict.get("votes") is not None else None,
                tags=as_dict.get("tags"),
                matched_signals=signals,
                pre_rank_score=score,
            )
        )

    scored.sort(key=lambda c: c.pre_rank_score, reverse=True)
    return _apply_diversity_limit(scored, MODEL_CANDIDATE_LIMIT)

