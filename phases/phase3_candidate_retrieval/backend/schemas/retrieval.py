from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from phases.phase2_user_input_api.backend.schemas.recommendation import RecommendationRequest


class ShortlistRequest(RecommendationRequest):
    # Publicly, shortlist size is no longer required. We use a fixed internal limit.
    pass


class Candidate(BaseModel):
    candidate_id: int
    name: str
    city: str
    locality: Optional[str] = None
    cuisines: Optional[str]
    rating: Optional[float]
    avg_cost_for_two: Optional[float]
    votes: Optional[int] = None
    tags: Optional[str] = None
    matched_signals: list[str]
    pre_rank_score: float


class ShortlistResponse(BaseModel):
    message: str
    candidates_found: int
    candidates: list[Candidate]

