from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException

from phases.phase6_production_readiness.backend.schemas.production import (
    MetricsResponse,
    ProductionRequest,
    ProductionResponse,
)
from phases.phase6_production_readiness.backend.services.production_pipeline import (
    DB_PATH,
    ProductionPipelineError,
    ProductionRateLimitError,
    cache,
    limiter,
    metrics,
    run_production_recommendation,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "phase6_production_readiness"}


@router.get("/api/v1/metrics", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    return MetricsResponse(**metrics.snapshot())


@router.get("/api/v1/locations")
def get_locations() -> dict:
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT city, COUNT(*) as cnt FROM restaurants GROUP BY city ORDER BY cnt DESC LIMIT 200"
        ).fetchall()
    finally:
        conn.close()
    return {"locations": [r[0] for r in rows if r[0]]}


@router.post("/api/v1/recommendations/production", response_model=ProductionResponse)
def production_recommendations(payload: ProductionRequest) -> ProductionResponse:
    try:
        return run_production_recommendation(payload)
    except ProductionRateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.") from None
    except ProductionPipelineError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
