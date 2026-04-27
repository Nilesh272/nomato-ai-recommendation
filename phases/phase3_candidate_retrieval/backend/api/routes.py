from __future__ import annotations

from fastapi import APIRouter

from phases.phase3_candidate_retrieval.backend.schemas.retrieval import ShortlistRequest, ShortlistResponse
from phases.phase3_candidate_retrieval.backend.services.retrieval import get_shortlist

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "phase3_candidate_retrieval"}


@router.post("/api/v1/recommendations/shortlist", response_model=ShortlistResponse)
def shortlist_candidates(payload: ShortlistRequest) -> ShortlistResponse:
    candidates = get_shortlist(payload)
    return ShortlistResponse(
        message="Candidate shortlist generated successfully.",
        candidates_found=len(candidates),
        candidates=candidates,
    )

