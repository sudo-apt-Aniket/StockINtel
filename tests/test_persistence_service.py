"""Tests for analysis and alert persistence."""

from pathlib import Path

from backend.services.database import Database
from backend.services.persistence_service import PersistenceService


def test_persistence_service_saves_analysis_and_alert(tmp_path: Path) -> None:
    """Saving an actionable analysis should persist both the analysis and an alert."""
    database = Database(tmp_path / "stock_intel.db")
    service = PersistenceService(database=database, alert_confidence_threshold=0.7)
    service.initialize()

    result = service.save_analysis(
        {
            "request": {"symbol": "RELIANCE", "timeframe": "1d", "portfolio": [], "include_news": True},
            "summary": {
                "symbol": "RELIANCE",
                "alert": "RELIANCE is showing a constructive setup with confidence 0.80.",
                "recommendation": "Watch for a clean breakout confirmation before acting.",
                "confidence": 0.8,
                "rationale": "Constructive signal mix.",
            },
            "market_snapshot": {"symbol": "RELIANCE"},
            "signals": {"signals": [{"status": "bullish"}]},
            "patterns": {"patterns": [{"status": "watch"}]},
            "pipeline": [{"stage": "data_fetch", "status": "completed"}],
        }
    )

    analyses = service.list_recent_analyses()
    alerts = service.list_open_alerts()

    assert result["analysis_id"] is not None
    assert analyses[0]["symbol"] == "RELIANCE"
    assert len(alerts) == 1
    assert alerts[0]["analysis_id"] == result["analysis_id"]
