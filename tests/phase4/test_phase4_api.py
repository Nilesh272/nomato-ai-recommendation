from fastapi.testclient import TestClient

from phases.phase4_llm_ranking.backend.main import app
from phases.phase4_llm_ranking.backend.schemas.ranking import RankResponse, RankedRecommendation

client = TestClient(app)


def test_phase4_final_endpoint_contract(monkeypatch) -> None:
    def _fake_ranker(_payload):
        return RankResponse(
            message="ok",
            fallback_used=False,
            shortlist_count=2,
            recommendations=[
                RankedRecommendation(rank=1, restaurant_name="Spice Hub", explanation="Good fit.", confidence=0.9)
            ],
        )

    monkeypatch.setattr("phases.phase4_llm_ranking.backend.api.routes.rank_with_llm", _fake_ranker)

    payload = {
        "location": "Bangalore",
        "budget_tier": "medium",
        "cuisines": ["North Indian"],
        "min_rating": 4.0,
        "additional_preferences": ["quick service"],
        "max_results": 5,
        "shortlist_size": 20,
        "top_k": 3,
    }
    response = client.post("/api/v1/recommendations/final", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "fallback_used" in data
    assert "recommendations" in data

