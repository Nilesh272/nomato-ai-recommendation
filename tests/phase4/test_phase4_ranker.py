from __future__ import annotations

from phases.phase3_candidate_retrieval.backend.schemas.retrieval import Candidate
from phases.phase4_llm_ranking.backend.schemas.ranking import RankRequest
from phases.phase4_llm_ranking.backend.services import ranker


def _sample_candidates() -> list[Candidate]:
    return [
        Candidate(
            candidate_id=1,
            name="Spice Hub",
            city="Bangalore",
            cuisines="North Indian",
            rating=4.6,
            avg_cost_for_two=900.0,
            matched_signals=["rating_match", "within_budget", "cuisine_match"],
            pre_rank_score=92.5,
        ),
        Candidate(
            candidate_id=2,
            name="Pasta Point",
            city="Bangalore",
            cuisines="Italian",
            rating=4.3,
            avg_cost_for_two=1100.0,
            matched_signals=["rating_match", "within_budget"],
            pre_rank_score=81.2,
        ),
    ]


def _request() -> RankRequest:
    return RankRequest(
        location="Bangalore",
        budget_tier="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
        additional_preferences=["quick service"],
        max_results=5,
        shortlist_size=20,
        top_k=2,
    )


def test_rank_with_llm_success(monkeypatch) -> None:
    monkeypatch.setattr(ranker, "get_shortlist", lambda request: _sample_candidates())
    monkeypatch.setattr(
        ranker,
        "invoke_groq_ranking",
        lambda prompt: {
            "content_json": {
                "recommendations": [
                    {"rank": 1, "restaurant_name": "Spice Hub", "explanation": "Great fit.", "confidence": 0.92},
                    {"rank": 2, "restaurant_name": "Pasta Point", "explanation": "Also relevant.", "confidence": 0.78},
                ]
            }
        },
    )

    response = ranker.rank_with_llm(_request())
    assert response.fallback_used is False
    assert len(response.recommendations) == 2
    assert response.recommendations[0].restaurant_name == "Spice Hub"


def test_rank_with_llm_hallucination_fallback(monkeypatch) -> None:
    monkeypatch.setattr(ranker, "get_shortlist", lambda request: _sample_candidates())
    monkeypatch.setattr(
        ranker,
        "invoke_groq_ranking",
        lambda prompt: {
            "content_json": {
                "recommendations": [
                    {"rank": 1, "restaurant_name": "Imaginary Place", "explanation": "Not in shortlist."}
                ]
            }
        },
    )

    response = ranker.rank_with_llm(_request())
    assert response.fallback_used is True
    assert response.recommendations[0].restaurant_name == "Spice Hub"


def test_rank_with_llm_exception_fallback(monkeypatch) -> None:
    monkeypatch.setattr(ranker, "get_shortlist", lambda request: _sample_candidates())

    def _raise(_: str) -> dict:
        raise RuntimeError("provider down")

    monkeypatch.setattr(ranker, "invoke_groq_ranking", _raise)
    response = ranker.rank_with_llm(_request())
    assert response.fallback_used is True
    assert len(response.recommendations) == 2

