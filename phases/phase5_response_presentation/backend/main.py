from __future__ import annotations

from fastapi import FastAPI

from phases.phase5_response_presentation.backend.api.routes import router

app = FastAPI(
    title="Zomato Recommendation API - Phase 5",
    version="0.1.0",
    description="Presentation formatter for UI-ready recommendation responses.",
)
app.include_router(router)

