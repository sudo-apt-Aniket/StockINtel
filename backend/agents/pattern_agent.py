"""Pattern Analysis Agent for technical pattern and indicator assessment."""

from __future__ import annotations

import math
from statistics import mean
from typing import Any, Dict, List

from .base import AgentRequest, MarketSnapshot, PatternResult


class PatternAnalysisAgent:
    """Analyzes technical structure such as RSI and support/resistance zones."""

    def run(self, request: AgentRequest, context: Dict[str, Any]) -> PatternResult:
        """Inspect the fetched market snapshot for technical patterns."""
        snapshot = context["market_snapshot"]
        return self.analyze_patterns(snapshot)

    def analyze_patterns(self, snapshot: MarketSnapshot) -> PatternResult:
        """Return support, resistance, breakout proximity, and RSI analysis with guardrails."""
        valid_history = [p for p in snapshot.historical_prices if p > 0.0]
        if len(valid_history) < 3:
            return PatternResult(
                symbol=snapshot.symbol,
                patterns=[{"name": "insufficient_data", "status": "neutral", "details": "Not enough valid price history."}],
                support_level=0.0,
                resistance_level=0.0,
                rsi=50.0,
            )
            
        recent_history = valid_history[-30:] # Bounded recent lookback

        support_level, resistance_level = self._calculate_support_resistance(recent_history)
        rsi = self._calculate_rsi(recent_history)
        volatility, upper_band, lower_band = self._calculate_bollinger_bands(recent_history)
        patterns = self._identify_patterns(snapshot, support_level, resistance_level, rsi, volatility, upper_band, lower_band)

        return PatternResult(
            symbol=snapshot.symbol,
            patterns=patterns,
            support_level=support_level,
            resistance_level=resistance_level,
            rsi=rsi,
            volatility=volatility,
        )

    def _calculate_support_resistance(self, prices: List[float]) -> tuple[float, float]:
        """Estimate support and resistance using recent lower and upper price clusters."""
        sorted_prices = sorted(prices)
        cluster_size = max(1, min(3, len(sorted_prices)))
        support_level = round(mean(sorted_prices[:cluster_size]), 2)
        resistance_level = round(mean(sorted_prices[-cluster_size:]), 2)
        return (support_level, resistance_level)

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI from available closes, adapting when history is short."""
        if len(prices) < 2:
            return 50.0

        lookback = min(period, len(prices) - 1)
        relevant_prices = prices[-(lookback + 1) :]
        changes = [
            relevant_prices[index] - relevant_prices[index - 1]
            for index in range(1, len(relevant_prices))
        ]
        gains = [change for change in changes if change > 0]
        losses = [abs(change) for change in changes if change < 0]

        average_gain = sum(gains) / lookback if gains else 0.0
        average_loss = sum(losses) / lookback if losses else 0.0

        if average_loss == 0:
            return 100.0 if average_gain > 0 else 50.0

        relative_strength = average_gain / average_loss
        return round(100 - (100 / (1 + relative_strength)), 2)

    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> tuple[float, float, float]:
        """Calculate historical volatility standard deviation and resulting Bollinger Bands."""
        if len(prices) < 2:
            return 0.0, 0.0, 0.0
        lookback = min(period, len(prices))
        relevant = prices[-lookback:]
        mean_val = sum(relevant) / lookback
        variance = sum((x - mean_val) ** 2 for x in relevant) / lookback
        std_dev = math.sqrt(variance)
        return (round(std_dev, 2), round(mean_val + (2 * std_dev), 2), round(mean_val - (2 * std_dev), 2))

    def _identify_patterns(
        self,
        snapshot: MarketSnapshot,
        support_level: float,
        resistance_level: float,
        rsi: float,
        volatility: float,
        upper_band: float,
        lower_band: float,
    ) -> List[Dict[str, Any]]:
        """Produce simple but interpretable chart pattern insights."""
        patterns: List[Dict[str, Any]] = []
        latest_price = snapshot.latest_price
        price_range = max(resistance_level - support_level, 0.01)
        distance_to_resistance_pct = ((resistance_level - latest_price) / resistance_level) * 100
        distance_to_support_pct = ((latest_price - support_level) / support_level) * 100

        if latest_price > resistance_level:
            patterns.append(
                {
                    "name": "breakout_confirmation",
                    "status": "bullish",
                    "details": (
                        f"Price has moved above the recent resistance cluster near {resistance_level}."
                    ),
                }
            )
        elif distance_to_resistance_pct <= 1.0:
            patterns.append(
                {
                    "name": "breakout_setup",
                    "status": "watch",
                    "details": (
                        f"Price is within {round(distance_to_resistance_pct, 2)}% of resistance near "
                        f"{resistance_level}."
                    ),
                }
            )

        if distance_to_support_pct <= 1.0:
            patterns.append(
                {
                    "name": "support_retest",
                    "status": "watch",
                    "details": (
                        f"Price is trading close to support near {support_level}, which may define risk."
                    ),
                }
            )

        patterns.append(
            {
                "name": "rsi_momentum",
                "status": self._classify_rsi(rsi),
                "details": self._describe_rsi(rsi),
            }
        )

        patterns.append(
            {
                "name": "support_resistance",
                "status": "informational",
                "details": (
                    f"Support is clustered near {support_level}, resistance near {resistance_level}, "
                    f"and the observed range is {round(price_range, 2)}."
                ),
            }
        )

        if upper_band > 0:
            if latest_price > upper_band:
                patterns.append({
                    "name": "bollinger_breakout_up", 
                    "status": "overbought", 
                    "details": f"Price {latest_price} is piercing the upper Bollinger Band ({upper_band}), warning of extreme upside volatility."
                })
            elif latest_price < lower_band:
                patterns.append({
                    "name": "bollinger_breakout_down", 
                    "status": "oversold", 
                    "details": f"Price {latest_price} is below the lower Bollinger Band ({lower_band}), indicating downside volatility extension."
                })

        return patterns

    def _classify_rsi(self, rsi: float) -> str:
        """Map RSI value into an interpretable pattern status."""
        if rsi >= 70:
            return "overbought"
        if rsi >= 60:
            return "bullish"
        if rsi <= 30:
            return "oversold"
        if rsi <= 40:
            return "bearish"
        return "neutral"

    def _describe_rsi(self, rsi: float) -> str:
        """Generate a short explanation for the RSI reading."""
        if rsi >= 70:
            return f"RSI is {rsi}, which indicates strong momentum but also an overbought condition."
        if rsi >= 60:
            return f"RSI is {rsi}, which suggests constructive bullish momentum."
        if rsi <= 30:
            return f"RSI is {rsi}, which indicates weak momentum and a potentially oversold condition."
        if rsi <= 40:
            return f"RSI is {rsi}, which suggests bearish momentum."
        return f"RSI is {rsi}, which suggests balanced momentum without a strong directional edge."
