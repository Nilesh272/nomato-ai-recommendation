from __future__ import annotations

from fastapi import FastAPI

from phases.phase2_user_input_api.backend.api.routes import router

app = FastAPI(
    title="Zomato Recommendation API - Phase 2",
    version="0.1.0",
    description="User input intake, validation, and normalization API.",
)

app.include_router(router)

