from __future__ import annotations

from phases.phase2_user_input_api.backend.schemas.recommendation import NormalizedPreferences, RecommendationRequest


BUDGET_RANGES: dict[str, tuple[int, int | None]] = {
    "low": (0, 500),
    "medium": (501, 1500),
    "high": (1501, None),
}

CUISINE_SYNONYMS: dict[str, str] = {
    "north indian": "North Indian",
    "south indian": "South Indian",
    "chinese": "Chinese",
    "italian": "Italian",
    "fast food": "Fast Food",
    "continental": "Continental",
}


def _normalize_cuisine(value: str) -> str:
    lowered = value.strip().lower()
    return CUISINE_SYNONYMS.get(lowered, value.strip().title())


def _normalize_preference(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def normalize_preferences(payload: RecommendationRequest) -> NormalizedPreferences:
    if payload.budget_min is not None or payload.budget_max is not None:
        budget_min = int(payload.budget_min or 0)
        budget_max = int(payload.budget_max) if payload.budget_max is not None else None
    else:
        tier = payload.budget_tier.value if payload.budget_tier is not None else "medium"
        budget_min, budget_max = BUDGET_RANGES[tier]
    cuisines = [_normalize_cuisine(v) for v in payload.cuisines]
    preferences = [_normalize_preference(v) for v in payload.additional_preferences]

    return NormalizedPreferences(
        location=payload.location.title(),
        budget_tier=payload.budget_tier,
        budget_min=budget_min,
        budget_max=budget_max,
        cuisines=list(dict.fromkeys(cuisines)),
        min_rating=round(payload.min_rating, 1),
        additional_preferences=list(dict.fromkeys(preferences)),
        max_results=payload.max_results,
    )

