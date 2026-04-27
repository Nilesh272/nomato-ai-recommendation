from __future__ import annotations

from fastapi import FastAPI

from phases.phase4_llm_ranking.backend.api.routes import router

app = FastAPI(
    title="Zomato Recommendation API - Phase 4",
    version="0.1.0",
    description="LLM ranking and explanation service with deterministic fallback.",
)
app.include_router(router)

