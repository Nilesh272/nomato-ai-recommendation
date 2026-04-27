from phases.phase4_llm_ranking.backend.schemas.ranking import RankResponse, RankedRecommendation
from phases.phase5_response_presentation.backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_phase5_presentation_endpoint(monkeypatch) -> None:
    def _fake_rank(_payload):
        return RankResponse(
            message="ok",
            fallback_used=False,
            shortlist_count=1,
            recommendations=[
                RankedRecommendation(
                    rank=1,
                    restaurant_name="Spice Hub",
                    explanation="Great fit.",
                    cuisines="North Indian",
                    rating=4.5,
                    avg_cost_for_two=900,
                )
            ],
        )

    monkeypatch.setattr("phases.phase5_response_presentation.backend.api.routes.rank_with_llm", _fake_rank)
    payload = {
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
    response = client.post("/api/v1/recommendations/present", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommendations"][0]["restaurant_name"] == "Spice Hub"
    assert data["recommendations"][0]["estimated_cost"] == "INR 900 for two"

