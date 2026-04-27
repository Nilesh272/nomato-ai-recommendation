from fastapi.testclient import TestClient

from frontend.basic_ui.app import app
from phases.phase5_response_presentation.backend.schemas.presentation import (
    EmptyStateSuggestion,
    PresentedRecommendation,
    PresentationResponse,
)

client = TestClient(app)


def test_ui_home_page_loads() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Zomato AI Recommender" in response.text


def test_ui_backend_route_with_mock(monkeypatch) -> None:
    from phases.phase6_production_readiness.backend.api import routes

    def _fake_format(_payload, _rank_response):
        return PresentationResponse(
            message="ok",
            fallback_used=False,
            recommendations=[
                PresentedRecommendation(
                    rank=1,
                    restaurant_name="Spice Hub",
                    cuisine="North Indian",
                    rating="4.5/5.0",
                    estimated_cost="INR 900 for two",
                    ai_generated_explanation="Great fit.",
                    sort_key_ai_rank=1,
                    sort_key_cost=900.0,
                )
            ],
            empty_state_suggestions=[EmptyStateSuggestion(suggestion="none")],
        )

    monkeypatch.setattr(routes, "format_for_presentation", _fake_format)
    monkeypatch.setattr(
        routes,
        "rank_with_llm",
        lambda _payload: type("R", (), {"fallback_used": False, "recommendations": [1]})(),
    )

    payload = {
        "client_id": "ui-test",
        "location": "Bangalore",
        "budget_tier": "medium",
        "cuisines": ["North Indian"],
        "min_rating": 4.0,
        "additional_preferences": ["quick service"],
        "max_results": 5,
        "shortlist_size": 20,
        "top_k": 5,
        "sort_mode": "ai_ranked",
    }
    response = client.post("/api/v1/recommendations/production", json=payload)
    assert response.status_code == 200
    assert response.json()["recommendations"][0]["restaurant_name"] == "Spice Hub"

