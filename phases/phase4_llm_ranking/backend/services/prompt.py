from __future__ import annotations

import json

from phases.phase2_user_input_api.backend.services.normalizer import normalize_preferences
from phases.phase3_candidate_retrieval.backend.schemas.retrieval import Candidate
from phases.phase4_llm_ranking.backend.schemas.ranking import RankRequest


def build_ranking_prompt(request: RankRequest, candidates: list[Candidate]) -> str:
    normalized = normalize_preferences(request)
    candidate_payload = [
        {
            "candidate_id": c.candidate_id,
            "name": c.name,
            "city": c.city,
            "cuisines": c.cuisines,
            "rating": c.rating,
            "avg_cost_for_two": c.avg_cost_for_two,
            "pre_rank_score": c.pre_rank_score,
            "matched_signals": c.matched_signals,
        }
        for c in candidates
    ]

    instruction = {
        "task": "Rank restaurants and explain fit.",
        "constraints": [
            "Do not invent data.",
            "Use only attributes in candidate list.",
            "Return top K recommendations.",
            "Each explanation must be at most 2-3 sentences.",
            "Return strict JSON only. No markdown fences.",
            "Budget constraints are numeric INR for two (budget_min/budget_max).",
        ],
        "output_schema": {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_name": "string",
                    "explanation": "string",
                    "confidence": 0.0,
                }
            ]
        },
    }

    payload = {
        "user_preferences": normalized.model_dump(),
        "top_k": request.top_k,
        "candidates": candidate_payload,
    }
    return f"{json.dumps(instruction)}\n{json.dumps(payload)}"

