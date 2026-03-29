"""Unit tests for the India-first data and news providers."""

from unittest.mock import MagicMock, patch

import pytest
import httpx

from backend.agents.base import AgentRequest
from backend.services.market_data_service import NseYahooMarketDataProvider
from backend.services.news_service import NseYahooNewsProvider


@pytest.fixture
def market_provider() -> NseYahooMarketDataProvider:
    return NseYahooMarketDataProvider()


@pytest.fixture
def news_provider() -> NseYahooNewsProvider:
    return NseYahooNewsProvider()


def test_nse_yahoo_market_data_provider_appends_ns_suffix(market_provider: NseYahooMarketDataProvider):
    """Ensure the provider automatically appends .NS to NSE symbols lacking a dot."""
    request = AgentRequest(symbol="RELIANCE", timeframe="1d")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "chart": {
            "result": [
                {
                    "indicators": {
                        "quote": [{"close": [100.0] * 19 + [2450.0], "volume": [100] * 19 + [200]}]
                    }
                }
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response) as mock_get:
        snapshot = market_provider.fetch_snapshot(request)

        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        assert url.endswith("/RELIANCE.NS")
        
        assert snapshot.symbol == "RELIANCE"
        assert snapshot.latest_price == 2450.0
        assert snapshot.latest_volume == 200


def test_nse_yahoo_market_data_provider_preserves_existing_suffix(market_provider: NseYahooMarketDataProvider):
    """Ensure the provider does not append .NS if a dot is already present."""
    request = AgentRequest(symbol="TCS.BO", timeframe="1d")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "chart": {
            "result": [
                {
                    "indicators": {
                        "quote": [{"close": [100.0] * 19 + [3500.0], "volume": [100] * 19 + [500]}]
                    }
                }
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response) as mock_get:
        snapshot = market_provider.fetch_snapshot(request)

        url = mock_get.call_args[0][0]
        assert url.endswith("/TCS.BO")
        assert snapshot.symbol == "TCS.BO"


def test_nse_yahoo_news_provider_fetches_yahoo_first(news_provider: NseYahooNewsProvider):
    """Ensure the provider hits Yahoo Finance RSS with NSE symbols first."""
    mock_response = MagicMock()
    mock_response.text = "<rss><channel><item><title>Reliance announces gains</title></item></channel></rss>"
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response) as mock_get:
        headlines = news_provider.fetch_headlines("RELIANCE")

        mock_get.assert_called_once()
        kwargs = mock_get.call_args[1]
        assert kwargs["params"]["s"] == "RELIANCE.NS"
        assert kwargs["params"]["region"] == "IN"
        
        assert len(headlines) == 1
        assert headlines[0] == "Reliance announces gains"


def test_nse_yahoo_news_provider_falls_back_to_google(news_provider: NseYahooNewsProvider):
    """Ensure the provider falls back to Google News if Yahoo RSS fails."""
    def mock_get(*args, **kwargs):
        url = args[0]
        if "finance.yahoo.com" in url:
            raise httpx.HTTPError("Yahoo is down")
        
        mock_google_response = MagicMock()
        mock_google_response.text = "<rss><channel><item><title>Google News: Reliance Stock jumps</title></item></channel></rss>"
        mock_google_response.raise_for_status = MagicMock()
        return mock_google_response

    with patch("httpx.get", side_effect=mock_get) as mock_get_call:
        headlines = news_provider.fetch_headlines("RELIANCE")

        assert mock_get_call.call_count == 2
        assert len(headlines) == 1
        assert "Google News" in headlines[0]
