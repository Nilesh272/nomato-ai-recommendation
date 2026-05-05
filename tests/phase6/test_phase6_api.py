from phases.phase4_llm_ranking.backend.schemas.ranking import RankResponse, RankedRecommendation
from phases.phase6_production_readiness.backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _payload(client_id: str = "u1") -> dict:
    return {
        "client_id": client_id,
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


def test_phase6_cache_hit(monkeypatch) -> None:
    # Ensure the cache does not contain a previous run entry
    from phases.phase6_production_readiness.backend.api import routes
    routes.cache._store.clear()
    calls = {"count": 0}

    def _fake_rank(_payload):
        calls["count"] += 1
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

    monkeypatch.setattr(
        "phases.phase6_production_readiness.backend.services.production_pipeline.rank_with_llm",
        _fake_rank,
    )
    r1 = client.post("/api/v1/recommendations/production", json=_payload("cache-user"))
    r2 = client.post("/api/v1/recommendations/production", json=_payload("cache-user"))
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["cached"] is False
    assert r2.json()["cached"] is True
    assert calls["count"] == 1


def test_phase6_rate_limit(monkeypatch) -> None:
    from phases.phase6_production_readiness.backend.api import routes

    original = routes.limiter.max_requests
    routes.limiter.max_requests = 1

    def _fake_rank(_payload):
        return RankResponse(message="ok", fallback_used=True, shortlist_count=0, recommendations=[])

    monkeypatch.setattr(
        "phases.phase6_production_readiness.backend.services.production_pipeline.rank_with_llm",
        _fake_rank,
    )
    first = client.post("/api/v1/recommendations/production", json=_payload("limited-user"))
    second = client.post("/api/v1/recommendations/production", json=_payload("limited-user"))
    routes.limiter.max_requests = original
    assert first.status_code == 200
    assert second.status_code == 429


def test_phase6_metrics_endpoint() -> None:
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "request_count" in body
    assert "p95_latency_ms" in body

