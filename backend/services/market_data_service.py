"""Market data services for live or mock stock intelligence inputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol

import httpx

from backend.agents.base import AgentRequest, MarketSnapshot


class MarketDataProvider(Protocol):
    """Provider interface for market and news data sources."""

    def fetch_snapshot(self, request: AgentRequest) -> MarketSnapshot:
        """Return a market snapshot for the requested symbol."""


@dataclass
class MockMarketDataProvider:
    """Deterministic provider for local development and tests."""

    def fetch_snapshot(self, request: AgentRequest) -> MarketSnapshot:
        symbol = request.symbol.upper()
        historical_prices = [100.0] * 15 + [218.4, 220.1, 221.8, 224.0, 228.6]
        historical_volumes = [1000000] * 15 + [1050000, 1125000, 1190000, 1410000, 1750000]

        return MarketSnapshot(
            symbol=symbol,
            latest_price=historical_prices[-1],
            latest_volume=historical_volumes[-1],
            historical_prices=historical_prices,
            historical_volumes=historical_volumes,
            news_headlines=[],
            metadata={
                "timeframe": request.timeframe,
                "data_source": "mock",
                "news_source": "unconfigured",
            },
        )


@dataclass
class YFinanceMarketDataProvider:
    """Best-effort live provider backed by yfinance when available."""

    history_period: str = "1y"

    def fetch_snapshot(self, request: AgentRequest) -> MarketSnapshot:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError(
                "yfinance is not installed. Install dependencies or switch to the mock data provider."
            ) from exc

        ticker = yf.Ticker(request.symbol)
        history = ticker.history(period=self.history_period, interval="1d")
        if history.empty:
            raise ValueError(f"No market data returned for symbol '{request.symbol}'.")

        closes = [round(float(value), 2) for value in history["Close"].tolist()]
        volumes = [int(value) for value in history["Volume"].fillna(0).tolist()]
        symbol = request.symbol.upper()

        return MarketSnapshot(
            symbol=symbol,
            latest_price=closes[-1],
            latest_volume=volumes[-1],
            historical_prices=closes,
            historical_volumes=volumes,
            news_headlines=[],
            metadata={
                "timeframe": request.timeframe,
                "data_source": "yfinance",
                "news_source": "unconfigured",
            },
        )


@dataclass
class YahooFinanceMarketDataProvider:
    """Live provider backed by Yahoo Finance chart endpoints."""

    base_url: str = "https://query1.finance.yahoo.com/v8/finance/chart"
    stooq_url: str = "https://stooq.com/q/d/l/"
    history_range: str = "1mo"
    interval: str = "1d"

    def fetch_snapshot(self, request: AgentRequest) -> MarketSnapshot:
        try:
            return self._fetch_from_yahoo(request)
        except (httpx.HTTPError, ValueError):
            return self._fetch_from_stooq(request)

    def _fetch_from_yahoo(self, request: AgentRequest) -> MarketSnapshot:
        response = httpx.get(
            "{}/{}".format(self.base_url, request.symbol),
            params={"range": self.history_range, "interval": self.interval},
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        chart_result = payload.get("chart", {}).get("result", [])
        if not chart_result:
            raise ValueError("No market data returned for symbol '{}'.".format(request.symbol))

        result = chart_result[0]
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        closes = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose") or quote.get("close") or []
        volumes = quote.get("volume") or []

        filtered_closes = [round(float(value), 2) for value in closes if value is not None]
        filtered_volumes = [int(value) for value in volumes if value is not None]
        if not filtered_closes or not filtered_volumes:
            raise ValueError("Incomplete market data returned for symbol '{}'.".format(request.symbol))

        return self._build_snapshot(
            request=request,
            closes=filtered_closes,
            volumes=filtered_volumes,
            source_name="yahoo_finance",
        )

    def _fetch_from_stooq(self, request: AgentRequest) -> MarketSnapshot:
        symbol = request.symbol.lower()
        if "." not in symbol:
            symbol = "{}.us".format(symbol)

        response = httpx.get(
            self.stooq_url,
            params={"s": symbol, "i": "d"},
            timeout=10.0,
        )
        response.raise_for_status()
        lines = [line.strip() for line in response.text.splitlines() if line.strip()]
        if len(lines) <= 1:
            raise ValueError("No fallback market data returned for symbol '{}'.".format(request.symbol))

        closes: List[float] = []
        volumes: List[int] = []
        for row in lines[1:]:
            columns = row.split(",")
            if len(columns) < 6:
                continue
            close_value = columns[4]
            volume_value = columns[5]
            if close_value == "N/D" or volume_value == "N/D":
                continue
            closes.append(round(float(close_value), 2))
            volumes.append(int(float(volume_value)))

        if not closes or not volumes:
            raise ValueError("Incomplete fallback market data returned for symbol '{}'.".format(request.symbol))

        return self._build_snapshot(
            request=request,
            closes=closes,
            volumes=volumes,
            source_name="stooq",
        )

    def _build_snapshot(
        self, request: AgentRequest, closes: List[float], volumes: List[int], source_name: str
    ) -> MarketSnapshot:
        symbol = request.symbol.upper()
        return MarketSnapshot(
            symbol=symbol,
            latest_price=closes[-1],
            latest_volume=volumes[-1],
            historical_prices=closes,
            historical_volumes=volumes,
            news_headlines=[],
            metadata={
                "timeframe": request.timeframe,
                "data_source": source_name,
                "news_source": "unconfigured",
            },
        )


@dataclass
class NseYahooMarketDataProvider:
    """India-first live provider backed by Yahoo Finance chart endpoints without Stooq fallback."""

    base_url: str = "https://query1.finance.yahoo.com/v8/finance/chart"
    history_range: str = "3mo"
    interval: str = "1d"

    def fetch_snapshot(self, request: AgentRequest) -> MarketSnapshot:
        symbol = request.symbol.upper()
        # Canonical rule: append .NS if no dot
        yahoo_symbol = symbol if "." in symbol else "{}.NS".format(symbol)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        response = httpx.get(
            "{}/{}".format(self.base_url, yahoo_symbol),
            params={"range": self.history_range, "interval": self.interval},
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
        chart_result = payload.get("chart", {}).get("result", [])
        if not chart_result:
            raise ValueError("No market data returned for NSE symbol '{}'.".format(symbol))

        result = chart_result[0]
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        closes = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose") or quote.get("close") or []
        volumes = quote.get("volume") or []

        filtered_closes = [round(float(value), 2) for value in closes if value is not None]
        filtered_volumes = [int(value) for value in volumes if value is not None]
        if not filtered_closes or not filtered_volumes:
            raise ValueError("Incomplete market data returned for NSE symbol '{}'.".format(symbol))

        return MarketSnapshot(
            symbol=symbol,
            latest_price=filtered_closes[-1],
            latest_volume=filtered_volumes[-1],
            historical_prices=filtered_closes,
            historical_volumes=filtered_volumes,
            news_headlines=[],
            metadata={
                "timeframe": request.timeframe,
                "data_source": "nse_yahoo_finance",
                "news_source": "unconfigured",
            },
        )


def get_market_data_provider(provider_name: str) -> MarketDataProvider:
    """Build a market data provider from configuration."""
    normalized = provider_name.strip().lower()
    if normalized == "mock":
        return MockMarketDataProvider()
    if normalized == "yfinance":
        return YFinanceMarketDataProvider()
    if normalized == "yahoo_finance":
        return YahooFinanceMarketDataProvider()
    if normalized == "nse_yahoo_finance":
        return NseYahooMarketDataProvider()
    raise ValueError(f"Unsupported market data provider '{provider_name}'.")
