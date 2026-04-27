from __future__ import annotations

from fastapi import APIRouter

from phases.phase2_user_input_api.backend.schemas.recommendation import (
    RecommendationIntakeResponse,
    RecommendationRequest,
)
from phases.phase2_user_input_api.backend.services.normalizer import normalize_preferences

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "phase2_user_input_api"}


@router.post("/api/v1/recommendations", response_model=RecommendationIntakeResponse)
def intake_recommendation_request(payload: RecommendationRequest) -> RecommendationIntakeResponse:
    normalized = normalize_preferences(payload)
    return RecommendationIntakeResponse(
        message="Preferences validated and normalized successfully.",
        normalized_preferences=normalized,
    )

