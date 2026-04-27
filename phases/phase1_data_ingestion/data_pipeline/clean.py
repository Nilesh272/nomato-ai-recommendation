from __future__ import annotations

import re
from typing import Any

import pandas as pd


CANONICAL_COLUMNS = [
    "name",
    "city",
    "locality",
    "cuisines",
    "avg_cost_for_two",
    "rating",
    "votes",
    "tags",
]


COLUMN_CANDIDATES: dict[str, list[str]] = {
    "name": ["restaurant_name", "name", "res_name"],
    "city": ["city", "location", "rest_city"],
    "locality": ["locality", "area", "address", "subzone"],
    "cuisines": ["cuisines", "cuisine", "category"],
    "avg_cost_for_two": ["average_cost_for_two", "cost_for_two", "avg_cost_for_two", "price_for_two"],
    "rating": ["aggregate_rating", "rating", "user_rating"],
    "votes": ["votes", "rating_votes", "num_votes"],
    "tags": ["highlights", "tags", "features"],
}


def _normalize_header(col: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", col.lower()).strip("_")


def _find_matching_column(raw_columns: list[str], candidates: list[str]) -> str | None:
    normalized = {_normalize_header(c): c for c in raw_columns}
    for candidate in candidates:
        key = _normalize_header(candidate)
        if key in normalized:
            return normalized[key]
    return None


def build_column_mapping(raw_df: pd.DataFrame) -> dict[str, str]:
    mapping: dict[str, str] = {}
    raw_columns = list(raw_df.columns)
    for target, candidates in COLUMN_CANDIDATES.items():
        matched = _find_matching_column(raw_columns, candidates)
        if matched:
            mapping[target] = matched
    return mapping


def _to_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (float, int)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[^0-9.]+", "", value.strip())
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _to_int(value: Any) -> int | None:
    as_float = _to_float(value)
    return int(as_float) if as_float is not None else None


def _normalize_cuisines(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, list):
        tokens = [str(v).strip().title() for v in value if str(v).strip()]
    else:
        tokens = [v.strip().title() for v in str(value).split(",") if v.strip()]
    return ", ".join(dict.fromkeys(tokens)) if tokens else None


def _normalize_text(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text if text else None


def to_canonical(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Map source schema into canonical columns and normalize values."""
    mapping = build_column_mapping(raw_df)
    if "name" not in mapping or "city" not in mapping:
        raise ValueError("Source dataset must include mappable name and city/location columns.")

    rows: list[dict[str, Any]] = []
    for _, row in raw_df.iterrows():
        canonical: dict[str, Any] = {col: None for col in CANONICAL_COLUMNS}
        for target, source in mapping.items():
            canonical[target] = row.get(source)

        canonical["name"] = _normalize_text(canonical["name"])
        canonical["city"] = _normalize_text(canonical["city"])
        canonical["locality"] = _normalize_text(canonical["locality"])
        canonical["cuisines"] = _normalize_cuisines(canonical["cuisines"])
        canonical["avg_cost_for_two"] = _to_float(canonical["avg_cost_for_two"])
        canonical["rating"] = _to_float(canonical["rating"])
        canonical["votes"] = _to_int(canonical["votes"])
        canonical["tags"] = _normalize_text(canonical["tags"])
        rows.append(canonical)

    return pd.DataFrame(rows, columns=CANONICAL_COLUMNS)

