"""Data Fetch Agent for retrieving stock and news inputs."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import AgentRequest, MarketSnapshot
from backend.services.market_data_service import (
    MarketDataProvider,
    MockMarketDataProvider,
)
from backend.services.news_service import MockNewsProvider, NewsProvider


class DataFetchAgent:
    """Fetches market snapshots from external providers or mock sources.

    The implementation is intentionally lightweight so it can later be swapped
    with live data clients, scheduled jobs, or orchestration frameworks.
    """

    def __init__(
        self,
        provider: Optional[MarketDataProvider] = None,
        news_provider: Optional[NewsProvider] = None,
    ) -> None:
        self.provider = provider or MockMarketDataProvider()
        self.news_provider = news_provider or MockNewsProvider()

    def run(self, request: AgentRequest, context: Dict[str, Any]) -> MarketSnapshot:
        """Retrieve the latest stock snapshot for a symbol."""
        return self.fetch_stock_data(request)

    def fetch_stock_data(self, request: AgentRequest) -> MarketSnapshot:
        """Retrieve stock and news data concurrently to reduce latency and prevent timeouts."""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Step 1: Submit market and news tasks
            market_future = executor.submit(self.provider.fetch_snapshot, request)
            news_future = None
            if request.include_news:
                news_future = executor.submit(self.news_provider.fetch_headlines, request.symbol.upper())

            # Step 2: Resolve futures
            try:
                snapshot = market_future.result(timeout=15.0)
            except Exception as exc:
                raise RuntimeError(f"Market fetch timed out or failed for {request.symbol}: {exc}") from exc

            if news_future:
                try:
                    snapshot.news_headlines = news_future.result(timeout=10.0)
                    snapshot.metadata["news_source"] = (
                        self.news_provider.__class__.__name__.replace("Provider", "").lower()
                    )
                except Exception as exc:
                    snapshot.news_headlines = []
                    snapshot.metadata["news_source"] = "unavailable"
                    snapshot.metadata["news_error"] = str(exc)
        
        self._validate_market_data(snapshot)
        return snapshot

    def _validate_market_data(self, snapshot: MarketSnapshot) -> None:
        """Enforce strict guardrails on provider payloads before allowing downstream agents to consume them."""
        if not snapshot.historical_prices or not snapshot.historical_volumes:
            raise ValueError(f"Data validation failed: No historical market data returned for symbol {snapshot.symbol}.")
        
        if len(snapshot.historical_prices) != len(snapshot.historical_volumes):
            raise ValueError("Data validation failed: Structural mismatch. Price and volume array lengths differ.")

        if any(p <= 0 for p in snapshot.historical_prices) or snapshot.latest_price <= 0:
            raise ValueError("Data validation failed: Unrealistic price series containing zero or negative prices.")

        if any(v < 0 for v in snapshot.historical_volumes) or snapshot.latest_volume < 0:
            raise ValueError("Data validation failed: Malformed volume arrays containing negative volumes.")

        if len(snapshot.historical_prices) < 20:
             raise ValueError(
                f"Data validation failed: Insufficient history. Only {len(snapshot.historical_prices)} periods available, "
                "but at least 20 are required for stable indicator calculation."
            )
