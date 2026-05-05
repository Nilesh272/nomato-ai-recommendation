from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path

from phases.phase4_llm_ranking.backend.services.ranker import rank_with_llm
from phases.phase5_response_presentation.backend.services.formatter import format_for_presentation
from phases.phase6_production_readiness.backend.schemas.production import (
    ProductionRequest,
    ProductionResponse,
)
from phases.phase6_production_readiness.backend.services.cache import TTLCache
from phases.phase6_production_readiness.backend.services.evaluation import evaluate_recommendations
from phases.phase6_production_readiness.backend.services.observability import MetricsRegistry, log_event
from phases.phase6_production_readiness.backend.services.resilience import CircuitBreaker
from phases.phase6_production_readiness.backend.services.security import RateLimiter


class ProductionRateLimitError(Exception):
    """Raised when a client exceeds the configured request rate."""


class ProductionPipelineError(Exception):
    """Raised when the ranking or presentation pipeline fails."""


cache = TTLCache(ttl_seconds=180)
metrics = MetricsRegistry()
breaker = CircuitBreaker(failure_threshold=3, cooldown_seconds=60)
limiter = RateLimiter(max_requests=30, per_seconds=60)
DB_PATH = Path("phases/phase1_data_ingestion/data_pipeline/zomato.db")


def _cache_key(payload: ProductionRequest) -> str:
    signature = {
        "location": payload.location,
        "budget_min": payload.budget_min,
        "budget_max": payload.budget_max,
        "budget_tier": payload.budget_tier.value if payload.budget_tier else None,
        "cuisines": payload.cuisines,
        "min_rating": payload.min_rating,
        "additional_preferences": payload.additional_preferences,
        "sort_mode": payload.sort_mode,
        "top_k": payload.top_k,
    }
    return hashlib.sha256(json.dumps(signature, sort_keys=True).encode("utf-8")).hexdigest()


def run_production_recommendation(payload: ProductionRequest) -> ProductionResponse:
    """Execute the Phase 6 production path (cache, limits, LLM rank, format, metrics)."""
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    metrics.request_count += 1

    if not limiter.allow(payload.client_id):
        metrics.error_count += 1
        raise ProductionRateLimitError()

    key = _cache_key(payload)
    cached_payload = cache.get(key)
    if cached_payload is not None:
        metrics.cache_hit_count += 1
        latency_ms = (time.perf_counter() - start) * 1000
        metrics.observe_latency(latency_ms)
        log_event(
            {
                "event": "recommendation_request",
                "request_id": request_id,
                "cached": True,
                "filters": payload.model_dump(exclude={"client_id"}),
                "candidate_count": len(cached_payload.get("recommendations", [])),
                "llm_latency_ms": 0,
            }
        )
        return ProductionResponse(request_id=request_id, cached=True, **cached_payload)

    if not breaker.allow_request():
        metrics.fallback_count += 1
        return ProductionResponse(
            request_id=request_id,
            cached=False,
            message="Circuit breaker open due to LLM instability. Try again shortly.",
            fallback_used=True,
            recommendations=[],
            empty_state_suggestions=[],
        )

    try:
        rank_response = rank_with_llm(payload)
        presentation = format_for_presentation(payload, rank_response)
        if rank_response.fallback_used:
            metrics.fallback_count += 1
        if not presentation.recommendations:
            metrics.no_result_count += 1
        else:
            metrics.success_count += 1
        breaker.record_success()

        payload_dict = presentation.model_dump()
        cache.set(key, payload_dict)

        _eval = evaluate_recommendations(presentation.recommendations)
        latency_ms = (time.perf_counter() - start) * 1000
        metrics.observe_latency(latency_ms)
        log_event(
            {
                "event": "recommendation_request",
                "request_id": request_id,
                "cached": False,
                "filters": payload.model_dump(exclude={"client_id"}),
                "candidate_count": len(presentation.recommendations),
                "llm_latency_ms": round(latency_ms, 2),
                "eval": _eval,
            }
        )
        return ProductionResponse(request_id=request_id, cached=False, **payload_dict)
    except Exception as exc:  # noqa: BLE001
        metrics.error_count += 1
        breaker.record_failure()
        raise ProductionPipelineError(f"Production pipeline failed: {exc}") from exc
