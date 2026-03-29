"""News services for sentiment and headline enrichment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol
from xml.etree import ElementTree

import httpx


class NewsProvider(Protocol):
    """Provider interface for stock-related news headlines."""

    def fetch_headlines(self, symbol: str) -> List[str]:
        """Return recent news headlines for the requested symbol."""


@dataclass
class MockNewsProvider:
    """Deterministic news provider for local development and tests."""

    def fetch_headlines(self, symbol: str) -> List[str]:
        return [
            f"{symbol} gains attention after strong sector momentum",
            f"Analysts discuss earnings outlook for {symbol}",
        ]


@dataclass
class NewsApiProvider:
    """Best-effort news provider backed by NewsAPI."""

    api_key: str
    base_url: str = "https://newsapi.org/v2/everything"
    page_size: int = 5

    def fetch_headlines(self, symbol: str) -> List[str]:
        params = {
            "q": symbol,
            "language": "en",
            "pageSize": self.page_size,
            "sortBy": "publishedAt",
            "apiKey": self.api_key,
        }
        try:
            response = httpx.get(self.base_url, params=params, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"News provider request failed for symbol '{symbol}'.") from exc

        payload = response.json()
        articles = payload.get("articles", [])
        headlines = [article["title"] for article in articles if article.get("title")]
        return headlines


@dataclass
class YFinanceNewsProvider:
    """Live news provider backed by yfinance quote news."""

    max_items: int = 5

    def fetch_headlines(self, symbol: str) -> List[str]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError(
                "yfinance is not installed. Install dependencies or switch to a different news provider."
            ) from exc

        ticker = yf.Ticker(symbol)
        raw_news = getattr(ticker, "news", None) or []
        headlines = [item["title"] for item in raw_news if item.get("title")]
        return headlines[: self.max_items]


@dataclass
class YahooFinanceNewsProvider:
    """Live news provider backed by Yahoo Finance RSS feeds."""

    base_url: str = "https://feeds.finance.yahoo.com/rss/2.0/headline"
    google_news_url: str = "https://news.google.com/rss/search"
    max_items: int = 5

    def fetch_headlines(self, symbol: str) -> List[str]:
        try:
            response = httpx.get(
                self.base_url,
                params={"s": symbol, "region": "US", "lang": "en-US"},
                timeout=10.0,
            )
            response.raise_for_status()
            return self._parse_rss_titles(response.text)
        except httpx.HTTPError:
            response = httpx.get(
                self.google_news_url,
                params={"q": "{} stock".format(symbol), "hl": "en-US", "gl": "US", "ceid": "US:en"},
                timeout=10.0,
            )
            response.raise_for_status()
            return self._parse_rss_titles(response.text)

    def _parse_rss_titles(self, xml_payload: str) -> List[str]:
        root = ElementTree.fromstring(xml_payload)
        titles: List[str] = []
        for item in root.findall("./channel/item/title"):
            if item.text:
                titles.append(item.text.strip())
            if len(titles) >= self.max_items:
                break
        return titles


@dataclass
class NseYahooNewsProvider:
    """India-first live news provider backed by Yahoo Finance RSS feeds and Google News India."""

    base_url: str = "https://feeds.finance.yahoo.com/rss/2.0/headline"
    google_news_url: str = "https://news.google.com/rss/search"
    max_items: int = 5

    def fetch_headlines(self, symbol: str) -> List[str]:
        # Canonical NSE symbol formatting
        yahoo_symbol = symbol if "." in symbol else "{}.NS".format(symbol)
        try:
            response = httpx.get(
                self.base_url,
                params={"s": yahoo_symbol, "region": "IN", "lang": "en-IN"},
                timeout=10.0,
            )
            response.raise_for_status()
            return self._parse_rss_titles(response.text)
        except httpx.HTTPError:
            try:
                # Fallback to Google News India
                response = httpx.get(
                    self.google_news_url,
                    params={"q": "{} stock NSE".format(symbol), "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
                    timeout=10.0,
                )
                response.raise_for_status()
                return self._parse_rss_titles(response.text)
            except httpx.HTTPError:
                return []

    def _parse_rss_titles(self, xml_payload: str) -> List[str]:
        try:
            root = ElementTree.fromstring(xml_payload)
            titles: List[str] = []
            for item in root.findall("./channel/item/title"):
                if item.text:
                    titles.append(item.text.strip())
                if len(titles) >= self.max_items:
                    break
            return titles
        except Exception:
            return []


def get_news_provider(provider_name: str, api_key: Optional[str] = None) -> NewsProvider:
    """Build a news provider from configuration."""
    normalized = provider_name.strip().lower()
    if normalized == "mock":
        return MockNewsProvider()
    if normalized == "newsapi":
        if not api_key:
            raise ValueError("NEWSAPI provider requires STOCK_INTEL_NEWS_API_KEY to be set.")
        return NewsApiProvider(api_key=api_key)
    if normalized == "yfinance":
        return YFinanceNewsProvider()
    if normalized == "yahoo_finance":
        return YahooFinanceNewsProvider()
    if normalized == "nse_yahoo_finance":
        return NseYahooNewsProvider()
    raise ValueError(f"Unsupported news provider '{provider_name}'.")
