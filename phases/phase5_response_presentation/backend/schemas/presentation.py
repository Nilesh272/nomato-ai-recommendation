from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from phases.phase4_llm_ranking.backend.schemas.ranking import RankRequest


class PresentedRecommendation(BaseModel):
    rank: int
    restaurant_id: Optional[int] = None
    restaurant_name: str
    city: Optional[str] = None
    locality: Optional[str] = None
    cuisine: str
    rating: str
    estimated_cost: str
    votes: Optional[int] = None
    tags: Optional[str] = None
    ai_generated_explanation: str
    sort_key_ai_rank: int
    sort_key_cost: float


class EmptyStateSuggestion(BaseModel):
    suggestion: str


class PresentationResponse(BaseModel):
    message: str
    fallback_used: bool
    recommendations: list[PresentedRecommendation]
    empty_state_suggestions: list[EmptyStateSuggestion]


class PresentationRequest(RankRequest):
    sort_mode: str = "ai_ranked"

