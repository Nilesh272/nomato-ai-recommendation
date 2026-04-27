from __future__ import annotations

from pydantic import BaseModel

from phases.phase5_response_presentation.backend.schemas.presentation import (
    PresentationRequest,
    PresentationResponse,
)


class ProductionRequest(PresentationRequest):
    client_id: str = "anonymous"


class ProductionResponse(PresentationResponse):
    request_id: str
    cached: bool


class MetricsResponse(BaseModel):
    request_count: int
    success_count: int
    fallback_count: int
    no_result_count: int
    cache_hit_count: int
    error_count: int
    p95_latency_ms: float

