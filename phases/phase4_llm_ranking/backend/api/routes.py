from __future__ import annotations

from fastapi import APIRouter

from phases.phase4_llm_ranking.backend.schemas.ranking import RankRequest, RankResponse
from phases.phase4_llm_ranking.backend.services.ranker import rank_with_llm

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "phase4_llm_ranking"}


@router.post("/api/v1/recommendations/final", response_model=RankResponse)
def rank_final_recommendations(payload: RankRequest) -> RankResponse:
    return rank_with_llm(payload)

