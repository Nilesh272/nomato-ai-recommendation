from fastapi.testclient import TestClient

from phases.phase2_user_input_api.backend.main import app

client = TestClient(app)


def test_recommendations_intake_success() -> None:
    payload = {
        "location": "  bangalore ",
        "budget_tier": "medium",
        "cuisines": ["north indian", "Italian", "north indian"],
        "min_rating": 4.0,
        "additional_preferences": ["Quick Service", "family friendly"],
        "max_results": 5,
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    body = response.json()
    normalized = body["normalized_preferences"]
    assert normalized["location"] == "Bangalore"
    assert normalized["budget_min"] == 501
    assert normalized["budget_max"] == 1500
    assert normalized["cuisines"] == ["North Indian", "Italian"]
    assert normalized["additional_preferences"] == ["quick_service", "family_friendly"]


def test_recommendations_invalid_rating() -> None:
    payload = {"location": "Delhi", "budget_tier": "low", "min_rating": 7}
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 422

