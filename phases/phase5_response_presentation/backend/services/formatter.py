from __future__ import annotations

import re

from phases.phase4_llm_ranking.backend.schemas.ranking import RankResponse
from phases.phase5_response_presentation.backend.schemas.presentation import (
    EmptyStateSuggestion,
    PresentedRecommendation,
    PresentationRequest,
    PresentationResponse,
)

_FALLBACK_ERROR_RE = re.compile(
    r"\s*\((?:HTTPSConnectionPool|HTTPConnectionPool).*?\)\s*",
    flags=re.DOTALL,
)


def _sanitize_explanation(text: str, *, fallback_used: bool) -> str:
    if not text:
        return text
    if not fallback_used:
        return text

    # When the system falls back (e.g., LLM provider unreachable), keep the UX clean.
    cleaned = _FALLBACK_ERROR_RE.sub(" ", text).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    too_technical_markers = ("HTTPSConnectionPool", "NameResolutionError", "api.groq.com", "Max retries exceeded")
    if (not cleaned) or any(m in cleaned for m in too_technical_markers):
        return (
            "AI ranking is temporarily unavailable, so these results are selected using deterministic ranking. "
            "They match your filters and have strong pre-ranking signals."
        )

    return cleaned


def _format_rating(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}/5.0"


def _format_cost(value: float | None) -> str:
    if value is None:
        return "Not available"
    return f"INR {int(round(value))} for two"


def _empty_state() -> list[EmptyStateSuggestion]:
    return [
        EmptyStateSuggestion(suggestion="Try lowering minimum rating by 0.5."),
        EmptyStateSuggestion(suggestion="Try widening budget tier to include medium or high."),
        EmptyStateSuggestion(suggestion="Try removing one cuisine filter."),
    ]


def format_for_presentation(request: PresentationRequest, rank_response: RankResponse) -> PresentationResponse:
    if not rank_response.recommendations:
        return PresentationResponse(
            message="No recommendations found for current filters.",
            fallback_used=rank_response.fallback_used,
            recommendations=[],
            empty_state_suggestions=_empty_state(),
        )

    cards = [
        PresentedRecommendation(
            rank=item.rank,
            restaurant_id=item.candidate_id,
            restaurant_name=item.restaurant_name,
            city=item.city,
            locality=item.locality,
            cuisine=item.cuisines or "Not specified",
            rating=_format_rating(item.rating),
            estimated_cost=_format_cost(item.avg_cost_for_two),
            votes=item.votes,
            tags=item.tags,
            ai_generated_explanation=_sanitize_explanation(
                item.explanation, fallback_used=rank_response.fallback_used
            ),
            sort_key_ai_rank=item.rank,
            sort_key_cost=float(item.avg_cost_for_two or 999999.0),
        )
        for item in rank_response.recommendations
    ]

    if request.sort_mode == "cost_low_to_high":
        cards.sort(key=lambda x: x.sort_key_cost)
    else:
        cards.sort(key=lambda x: x.sort_key_ai_rank)

    return PresentationResponse(
        message="Recommendations prepared for UI presentation.",
        fallback_used=rank_response.fallback_used,
        recommendations=cards,
        empty_state_suggestions=[],
    )

