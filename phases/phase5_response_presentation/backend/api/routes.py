from __future__ import annotations

from fastapi import APIRouter

from phases.phase4_llm_ranking.backend.services.ranker import rank_with_llm
from phases.phase5_response_presentation.backend.schemas.presentation import (
    PresentationRequest,
    PresentationResponse,
)
from phases.phase5_response_presentation.backend.services.formatter import format_for_presentation

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "phase5_response_presentation"}


@router.post("/api/v1/recommendations/present", response_model=PresentationResponse)
def present_recommendations(payload: PresentationRequest) -> PresentationResponse:
    rank_response = rank_with_llm(payload)
    return format_for_presentation(payload, rank_response)

