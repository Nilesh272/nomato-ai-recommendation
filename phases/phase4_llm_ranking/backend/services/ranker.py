from __future__ import annotations

import json
from typing import Any

from phases.phase3_candidate_retrieval.backend.schemas.retrieval import Candidate
from phases.phase3_candidate_retrieval.backend.services.retrieval import get_shortlist
from phases.phase4_llm_ranking.backend.schemas.ranking import RankRequest, RankedRecommendation, RankResponse
from phases.phase4_llm_ranking.backend.services.groq_adapter import invoke_groq_ranking
from phases.phase4_llm_ranking.backend.services.prompt import build_ranking_prompt


def _extract_recommendations(content_json: dict[str, Any]) -> list[dict[str, Any]]:
    recs = content_json.get("recommendations", [])
    if isinstance(recs, list):
        return recs
    return []


def _candidate_map(candidates: list[Candidate]) -> dict[str, Candidate]:
    return {c.name.strip().lower(): c for c in candidates}


def _is_valid_output(raw_recs: list[dict[str, Any]], candidates: list[Candidate]) -> bool:
    if not raw_recs:
        return False
    c_map = _candidate_map(candidates)
    for item in raw_recs:
        if not isinstance(item.get("rank"), int):
            return False
        name = str(item.get("restaurant_name", "")).strip().lower()
        explanation = str(item.get("explanation", "")).strip()
        if not name or not explanation:
            return False
        if name not in c_map:
            return False
    return True


def _hydrate_recommendations(raw_recs: list[dict[str, Any]], candidates: list[Candidate], top_k: int) -> list[RankedRecommendation]:
    c_map = _candidate_map(candidates)
    hydrated: list[RankedRecommendation] = []
    for item in sorted(raw_recs, key=lambda x: x.get("rank", 10_000)):
        candidate = c_map[str(item["restaurant_name"]).strip().lower()]
        hydrated.append(
            RankedRecommendation(
                rank=int(item["rank"]),
                restaurant_name=candidate.name,
                explanation=str(item["explanation"]).strip(),
                confidence=float(item["confidence"]) if item.get("confidence") is not None else None,
                candidate_id=candidate.candidate_id,
                city=candidate.city,
                locality=candidate.locality,
                cuisines=candidate.cuisines,
                rating=candidate.rating,
                avg_cost_for_two=candidate.avg_cost_for_two,
                votes=candidate.votes,
                tags=candidate.tags,
                pre_rank_score=candidate.pre_rank_score,
            )
        )
    return hydrated[:top_k]


def _fallback(candidates: list[Candidate], top_k: int, reason: str) -> RankResponse:
    top = candidates[:top_k]
    recs = [
        RankedRecommendation(
            rank=i + 1,
            restaurant_name=item.name,
            explanation=(
                f"Selected by deterministic ranking because LLM output was unavailable or invalid ({reason}). "
                "This recommendation matches your filters and has strong pre-ranking signals."
            ),
            confidence=None,
            candidate_id=item.candidate_id,
            city=item.city,
            locality=item.locality,
            cuisines=item.cuisines,
            rating=item.rating,
            avg_cost_for_two=item.avg_cost_for_two,
            votes=item.votes,
            tags=item.tags,
            pre_rank_score=item.pre_rank_score,
        )
        for i, item in enumerate(top)
    ]
    return RankResponse(
        message="LLM ranking unavailable. Returned deterministic fallback.",
        fallback_used=True,
        shortlist_count=len(candidates),
        recommendations=recs,
    )


def rank_with_llm(request: RankRequest) -> RankResponse:
    candidates = get_shortlist(request)
    if not candidates:
        return RankResponse(
            message="No candidates found for the given preferences.",
            fallback_used=True,
            shortlist_count=0,
            recommendations=[],
        )

    prompt = build_ranking_prompt(request, candidates)
    try:
        llm_result = invoke_groq_ranking(prompt)
        raw_json = llm_result.get("content_json", {})
        if isinstance(raw_json, str):
            raw_json = json.loads(raw_json)
        raw_recs = _extract_recommendations(raw_json)
        if not _is_valid_output(raw_recs, candidates):
            return _fallback(candidates, request.top_k, "hallucination_or_schema_mismatch")
        hydrated = _hydrate_recommendations(raw_recs, candidates, request.top_k)
        return RankResponse(
            message="Recommendations ranked successfully using Groq LLM.",
            fallback_used=False,
            shortlist_count=len(candidates),
            recommendations=hydrated,
        )
    except Exception as exc:  # noqa: BLE001
        return _fallback(candidates, request.top_k, str(exc))

