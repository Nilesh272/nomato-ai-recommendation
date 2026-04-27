from __future__ import annotations

from fastapi import FastAPI

from phases.phase3_candidate_retrieval.backend.api.routes import router

app = FastAPI(
    title="Zomato Recommendation API - Phase 3",
    version="0.1.0",
    description="Candidate retrieval and deterministic pre-ranking API.",
)
app.include_router(router)

