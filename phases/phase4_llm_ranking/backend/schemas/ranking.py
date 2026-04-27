from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from phases.phase3_candidate_retrieval.backend.schemas.retrieval import ShortlistRequest


class RankedRecommendation(BaseModel):
    rank: int = Field(..., ge=1)
    restaurant_name: str
    explanation: str
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    candidate_id: Optional[int] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    cuisines: Optional[str] = None
    rating: Optional[float] = None
    avg_cost_for_two: Optional[float] = None
    votes: Optional[int] = None
    tags: Optional[str] = None
    pre_rank_score: Optional[float] = None


class RankRequest(ShortlistRequest):
    top_k: int = Field(default=5, ge=1, le=10)


class RankResponse(BaseModel):
    message: str
    fallback_used: bool
    shortlist_count: int
    recommendations: list[RankedRecommendation]

