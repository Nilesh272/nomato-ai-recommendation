from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationReport:
    total_rows: int
    valid_rows: int
    missing_name_or_city: int
    invalid_rating_rows: int
    invalid_cost_rows: int
    duplicate_rows: int


def validate_canonical(df: pd.DataFrame) -> tuple[pd.DataFrame, ValidationReport]:
    """Validate and return filtered canonical dataframe + report."""
    total_rows = len(df)
    base = df.copy()

    missing_name_or_city_mask = base["name"].isna() | base["city"].isna()
    invalid_rating_mask = base["rating"].notna() & ((base["rating"] < 0) | (base["rating"] > 5))
    invalid_cost_mask = base["avg_cost_for_two"].notna() & (base["avg_cost_for_two"] < 0)

    duplicate_mask = base.duplicated(subset=["name", "locality", "city"], keep="first")

    invalid_mask = missing_name_or_city_mask | invalid_rating_mask | invalid_cost_mask | duplicate_mask
    valid = base[~invalid_mask].copy()

    report = ValidationReport(
        total_rows=total_rows,
        valid_rows=len(valid),
        missing_name_or_city=int(missing_name_or_city_mask.sum()),
        invalid_rating_rows=int(invalid_rating_mask.sum()),
        invalid_cost_rows=int(invalid_cost_mask.sum()),
        duplicate_rows=int(duplicate_mask.sum()),
    )
    return valid, report

