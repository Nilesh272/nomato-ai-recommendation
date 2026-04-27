from fastapi.testclient import TestClient

from phases.phase3_candidate_retrieval.backend.main import app

client = TestClient(app)


def test_phase3_shortlist_endpoint_success() -> None:
    payload = {
        "location": "Bangalore",
        "budget_tier": "medium",
        "cuisines": ["North Indian"],
        "min_rating": 4.0,
        "additional_preferences": ["quick service"],
        "max_results": 5,
    }
    response = client.post("/api/v1/recommendations/shortlist", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "candidates" in body


def test_phase3_shortlist_size_validation() -> None:
    payload = {
        "location": "Bangalore",
        "budget_tier": "medium",
        "cuisines": [],
        "min_rating": 4.0,
        "additional_preferences": [],
        "max_results": 5,
    }
    response = client.post("/api/v1/recommendations/shortlist", json=payload)
    assert response.status_code == 200

