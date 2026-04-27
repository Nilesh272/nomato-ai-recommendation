from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from phases.phase6_production_readiness.backend.api.routes import router

app = FastAPI(
    title="Zomato Recommendation API - Phase 6",
    version="0.1.0",
    description="Production readiness layer with metrics, cache, resilience, and rate limiting.",
)

# Allow the Basic UI (running on a different port) to call the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8001",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

