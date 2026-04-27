from __future__ import annotations

from phases.phase4_llm_ranking.backend.schemas.ranking import RankResponse, RankedRecommendation
from phases.phase5_response_presentation.backend.schemas.presentation import PresentationRequest
from phases.phase5_response_presentation.backend.services.formatter import format_for_presentation


def _request(sort_mode: str = "ai_ranked") -> PresentationRequest:
    return PresentationRequest(
        location="Bangalore",
        budget_tier="medium",
        cuisines=["North Indian"],
        min_rating=4.0,
        additional_preferences=["quick service"],
        max_results=5,
        shortlist_size=20,
        top_k=5,
        sort_mode=sort_mode,
    )


def test_formatter_ai_rank_mode() -> None:
    rank_response = RankResponse(
        message="ok",
        fallback_used=False,
        shortlist_count=2,
        recommendations=[
            RankedRecommendation(rank=2, restaurant_name="B", explanation="e2", cuisines="Indian", rating=4.2, avg_cost_for_two=600),
            RankedRecommendation(rank=1, restaurant_name="A", explanation="e1", cuisines="Italian", rating=4.7, avg_cost_for_two=1200),
        ],
    )
    result = format_for_presentation(_request("ai_ranked"), rank_response)
    assert result.recommendations[0].restaurant_name == "A"
    assert result.recommendations[0].rating == "4.7/5.0"


def test_formatter_cost_sort_mode() -> None:
    rank_response = RankResponse(
        message="ok",
        fallback_used=False,
        shortlist_count=2,
        recommendations=[
            RankedRecommendation(rank=1, restaurant_name="High", explanation="e", cuisines="Indian", rating=4.3, avg_cost_for_two=1500),
            RankedRecommendation(rank=2, restaurant_name="Low", explanation="e", cuisines="Indian", rating=4.1, avg_cost_for_two=500),
        ],
    )
    result = format_for_presentation(_request("cost_low_to_high"), rank_response)
    assert result.recommendations[0].restaurant_name == "Low"
    assert result.recommendations[0].estimated_cost == "INR 500 for two"


def test_formatter_empty_state_suggestions() -> None:
    rank_response = RankResponse(message="none", fallback_used=True, shortlist_count=0, recommendations=[])
    result = format_for_presentation(_request(), rank_response)
    assert len(result.recommendations) == 0
    assert len(result.empty_state_suggestions) == 3

