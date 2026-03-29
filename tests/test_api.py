"""API tests for the stock intelligence backend."""

from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Create a lifespan-aware API client for each test."""
    with TestClient(app) as test_client:
        yield test_client


def test_analyze_endpoint_returns_structured_response(client: TestClient) -> None:
    """The analyze endpoint should return the full response contract."""
    response = client.post(
        "/analyze",
        json={
            "symbol": "RELIANCE",
            "timeframe": "1d",
            "portfolio": ["TCS", "RELIANCE"],
            "include_news": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["request"]["symbol"] == "RELIANCE"
    assert payload["summary"]["symbol"] == "RELIANCE"
    assert "market_snapshot" in payload
    assert "signals" in payload
    assert "patterns" in payload
    assert len(payload["pipeline"]) == 4
    assert payload["analysis_id"] >= 1


def test_analysis_detail_endpoint_returns_saved_analysis(client: TestClient) -> None:
    """A persisted analysis should be retrievable by id."""
    created = client.post(
        "/analyze",
        json={
            "symbol": "RELIANCE",
            "timeframe": "1d",
            "portfolio": ["RELIANCE"],
            "include_news": True,
        },
    )
    analysis_id = created.json()["analysis_id"]

    response = client.get(f"/analyses/{analysis_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_id"] == analysis_id
    assert payload["summary"]["symbol"] == "RELIANCE"


def test_alert_can_be_acknowledged(client: TestClient) -> None:
    """Open alerts should support lifecycle updates."""
    created = client.post(
        "/analyze",
        json={
            "symbol": "RELIANCE",
            "timeframe": "1d",
            "portfolio": [],
            "include_news": True,
        },
    )
    alert_id = created.json()["alert_id"]

    response = client.patch(f"/alerts/{alert_id}", json={"status": "acknowledged"})

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_analyze_endpoint_rejects_invalid_symbol(client: TestClient) -> None:
    """Invalid symbols should be blocked by request validation."""
    response = client.post(
        "/analyze",
        json={
            "symbol": "###",
            "timeframe": "1d",
            "portfolio": [],
            "include_news": True,
        },
    )

    assert response.status_code == 422


def test_analysis_endpoint_returns_502_when_pipeline_fails(monkeypatch, client: TestClient) -> None:
    """Pipeline failures should map to an upstream-style API error."""
    from backend.main import pipeline

    def broken_run(_request):
        raise RuntimeError("Pipeline stage 'data_fetch' failed")

    monkeypatch.setattr(pipeline, "run", broken_run)
    response = client.post(
        "/analyze",
        json={
            "symbol": "RELIANCE",
            "timeframe": "1d",
            "portfolio": [],
            "include_news": True,
        },
    )

    assert response.status_code == 502
