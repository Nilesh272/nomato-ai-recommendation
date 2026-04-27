from __future__ import annotations

from typing import List

from phases.phase5_response_presentation.backend.schemas.presentation import PresentedRecommendation


def evaluate_recommendations(recommendations: List[PresentedRecommendation]) -> dict:
    if not recommendations:
        return {"relevance": 0.0, "explanation_quality": 0.0, "diversity": 0.0}

    relevance = 1.0 if recommendations else 0.0
    explanation_quality = round(
        sum(1 for r in recommendations if len(r.ai_generated_explanation.strip()) > 15) / len(recommendations),
        2,
    )
    cuisine_set = set(r.cuisine for r in recommendations)
    diversity = round(len(cuisine_set) / len(recommendations), 2)
    return {"relevance": relevance, "explanation_quality": explanation_quality, "diversity": diversity}

