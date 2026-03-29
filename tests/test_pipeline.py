"""Tests for the stock analysis pipeline."""

from backend.agents.base import AgentRequest
from backend.services.analysis_pipeline import StockAnalysisPipeline


def test_pipeline_returns_complete_result() -> None:
    """The pipeline should return all major analysis sections."""
    pipeline = StockAnalysisPipeline()

    result = pipeline.run(
        AgentRequest(symbol="RELIANCE", timeframe="1d", portfolio=["RELIANCE"])
    )
    payload = result.to_dict()

    assert payload["request"]["symbol"] == "RELIANCE"
    assert payload["market_snapshot"]["symbol"] == "RELIANCE"
    assert payload["signals"]["symbol"] == "RELIANCE"
    assert payload["patterns"]["symbol"] == "RELIANCE"
    assert payload["explanation"]["symbol"] == "RELIANCE"
    assert len(payload["stages"]) == 4
    assert all(stage["status"] == "completed" for stage in payload["stages"])


def test_pipeline_rejects_unsupported_timeframe() -> None:
    """Unsupported timeframes should fail before agent execution begins."""
    pipeline = StockAnalysisPipeline()

    try:
        pipeline.run(AgentRequest(symbol="RELIANCE", timeframe="1y"))
    except ValueError as exc:
        assert "Unsupported timeframe" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported timeframe.")
