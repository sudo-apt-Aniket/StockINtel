"""Shared models and interfaces for modular backend agents."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class AgentRequest:
    """Normalized input passed into agents during analysis."""

    symbol: str
    timeframe: str = "1d"
    portfolio: List[str] = field(default_factory=list)
    include_news: bool = True


@dataclass
class MarketSnapshot:
    """Market and news data fetched for a single stock symbol."""

    symbol: str
    latest_price: float
    latest_volume: int
    historical_prices: List[float]
    historical_volumes: List[int]
    news_headlines: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalResult:
    """Structured signal detection output."""

    symbol: str
    signals: List[Dict[str, Any]]
    confidence: float
    summary: str
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class PatternResult:
    """Structured technical pattern analysis output."""

    symbol: str
    patterns: List[Dict[str, Any]]
    support_level: Optional[float]
    resistance_level: Optional[float]
    rsi: Optional[float]
    volatility: Optional[float] = None


@dataclass
class ExplanationResult:
    """Natural language explanation generated from system outputs."""

    symbol: str
    alert: str
    recommendation: str
    rationale: str
    confidence: float
    portfolio_insights: Optional[str] = None


@dataclass
class PipelineStageStatus:
    """Execution metadata for a single pipeline stage."""

    stage: str
    status: str
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Structured output returned by the analysis pipeline."""

    request: AgentRequest
    market_snapshot: MarketSnapshot
    signals: SignalResult
    patterns: PatternResult
    explanation: ExplanationResult
    context_files: Dict[str, str]
    stages: List[PipelineStageStatus]

    def to_dict(self) -> Dict[str, Any]:
        """Convert nested dataclasses into plain dictionaries for API responses."""
        return asdict(self)


class StockAgent(Protocol):
    """Protocol for future orchestration frameworks to target."""

    def run(self, request: AgentRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent and return a serializable result."""
