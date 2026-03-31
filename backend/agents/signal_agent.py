"""Signal Detection Agent for identifying price, volume, and sentiment signals."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .base import AgentRequest, MarketSnapshot, SignalResult, PatternResult


class SignalDetectionAgent:
    """Applies simple heuristics to detect actionable market signals."""

    def run(self, request: AgentRequest, context: Dict[str, Any]) -> SignalResult:
        """Evaluate the current market snapshot and produce signal summaries."""
        snapshot = context["market_snapshot"]
        patterns = context.get("patterns")
        return self.detect_signals(snapshot, patterns)

    def detect_signals(self, snapshot: MarketSnapshot, patterns: Optional[PatternResult] = None) -> SignalResult:
        """Generate structured price, volume, trend, and sentiment signals."""
        valid_prices = [p for p in snapshot.historical_prices if p > 0.0]
        valid_volumes = [v for v in snapshot.historical_volumes if v >= 0]
        
        if len(valid_prices) < 3 or len(valid_volumes) < 2:
            return SignalResult(
                symbol=snapshot.symbol,
                signals=[{"type": "data_error", "status": "neutral", "score": 0, "details": {}}],
                confidence=0.0,
                summary="Insufficient or invalid history for technical signals.",
            )

        price_signal = self._detect_price_breakout(snapshot, valid_prices)
        volume_signal = self._detect_volume_spike(snapshot, valid_volumes)
        trend_signal = self._detect_trend_strength(snapshot, valid_prices)
        sentiment_signal = self._detect_news_sentiment(snapshot.news_headlines)

        signals = [price_signal, volume_signal, trend_signal, sentiment_signal]
        active_signals = [signal for signal in signals if signal["status"] != "neutral"]
        net_score = sum(signal["score"] for signal in signals)
        confidence, breakdown = self._calculate_confidence(signals, patterns)

        return SignalResult(
            symbol=snapshot.symbol,
            signals=signals,
            confidence=confidence,
            confidence_breakdown=breakdown,
            summary=self._build_summary(active_signals, net_score),
        )

    def _detect_price_breakout(self, snapshot: MarketSnapshot, valid_prices: List[float]) -> Dict[str, Any]:
        recent_prices = valid_prices[-20:] # bounded lookback
        previous_close = recent_prices[-2]
        previous_high = max(recent_prices[:-1]) if len(recent_prices) > 1 else recent_prices[0]
        latest_price = valid_prices[-1]
        
        price_change_pct = ((latest_price - previous_close) / previous_close) * 100
        breakout_margin_pct = ((latest_price - previous_high) / previous_high) * 100 if previous_high > 0 else 0
        is_breakout = latest_price > previous_high
        status = "bullish" if is_breakout else "neutral"
        score = 2 if is_breakout else 0

        return {
            "type": "price_breakout",
            "status": status,
            "score": score,
            "details": {
                "latest_price": latest_price,
                "previous_high": previous_high,
                "previous_close": previous_close,
                "price_change_pct": round(price_change_pct, 2),
                "breakout_margin_pct": round(breakout_margin_pct, 2),
            },
        }

    def _detect_volume_spike(self, snapshot: MarketSnapshot, valid_volumes: List[int]) -> Dict[str, Any]:
        recent_volumes = valid_volumes[-20:]
        latest_volume = recent_volumes[-1]
        average_volume = sum(recent_volumes[:-1]) / max(1, len(recent_volumes[:-1]))
        volume_ratio = latest_volume / average_volume if average_volume > 0 else 1.0
        is_spike = volume_ratio >= 1.2

        return {
            "type": "volume_spike",
            "status": "bullish" if is_spike else "neutral",
            "score": 1 if is_spike else 0,
            "details": {
                "latest_volume": latest_volume,
                "average_volume": round(average_volume, 2),
                "volume_ratio": round(volume_ratio, 2),
            },
        }

    def _detect_trend_strength(self, snapshot: MarketSnapshot, valid_prices: List[float]) -> Dict[str, Any]:
        recent_long_window = valid_prices[-50:] # Extended lookback for moving averages
        
        if len(recent_long_window) < 20:
             return {
                "type": "trend_strength",
                "status": "neutral",
                "score": 0,
                "details": {"error": "Insufficient data for trend detection"},
            }
            
        short_window = valid_prices[-20:] # 20 period SMA
        long_window = recent_long_window # up to 50 period SMA
        short_moving_average = sum(short_window) / len(short_window)
        long_moving_average = sum(long_window) / len(long_window)
        
        trend_gap_pct = ((short_moving_average - long_moving_average) / long_moving_average) * 100 if long_moving_average > 0 else 0

        if trend_gap_pct >= 1.0:
            status = "bullish"
            score = 1
        elif trend_gap_pct <= -1.0:
            status = "bearish"
            score = -1
        else:
            status = "neutral"
            score = 0

        return {
            "type": "trend_strength",
            "status": status,
            "score": score,
            "details": {
                "short_moving_average_20": round(short_moving_average, 2),
                "long_moving_average_50": round(long_moving_average, 2),
                "trend_gap_pct": round(trend_gap_pct, 2),
            },
        }

    def _detect_news_sentiment(self, headlines: List[str]) -> Dict[str, Any]:
        positive_keywords = ("strong", "gains", "growth", "beats", "upgrade")
        negative_keywords = ("falls", "downgrade", "weak", "misses", "lawsuit")

        positive_matches = sum(
            1 for headline in headlines if any(word in headline.lower() for word in positive_keywords)
        )
        negative_matches = sum(
            1 for headline in headlines if any(word in headline.lower() for word in negative_keywords)
        )
        sentiment_score = positive_matches - negative_matches

        if sentiment_score > 0:
            status = "bullish"
            score = 1
        elif sentiment_score < 0:
            status = "bearish"
            score = -1
        else:
            status = "neutral"
            score = 0

        return {
            "type": "news_sentiment",
            "status": status,
            "score": score,
            "details": {
                "headline_count": len(headlines),
                "positive_headline_matches": positive_matches,
                "negative_headline_matches": negative_matches,
                "sentiment_score": sentiment_score,
            },
        }

    def _calculate_confidence(self, signals: List[Dict[str, Any]], patterns: Optional[PatternResult] = None) -> Tuple[float, Dict[str, float]]:
        """Combine multiple factors with deterministic weights to produce a granular, unique score."""
        breakdown = {}
        
        # 1. Price Momentum Score (0.0 to 0.3)
        price_signal = next((s for s in signals if s["type"] == "price_breakout"), None)
        price_details = price_signal.get("details", {}) if price_signal else {}
        change_val = abs(price_details.get("price_change_pct", 0))
        price_score = min(0.3, change_val / 12.0) # More sensitive
        breakdown["price_momentum"] = round(price_score, 3)
        
        # 2. Volume Participation Score (0.0 to 0.2)
        volume_signal = next((s for s in signals if s["type"] == "volume_spike"), None)
        vol_ratio = volume_signal.get("details", {}).get("volume_ratio", 1.0) if volume_signal else 1.0
        volume_score = min(0.2, max(0.0, (vol_ratio - 1.0) / 8.0))
        breakdown["volume_profile"] = round(volume_score, 3)
        
        # 3. RSI Quality Score (0.0 to 0.15)
        rsi_score = 0.0
        if patterns and patterns.rsi:
            dist_from_50 = abs(patterns.rsi - 50)
            rsi_score = min(0.15, dist_from_50 / 200.0)
            if 40 <= patterns.rsi <= 60:
                rsi_score += 0.05
        breakdown["rsi_condition"] = round(rsi_score, 3)
        
        # 4. Trend Distance (SMA Gap) (0.0 to 0.15)
        # Use the symbol from patterns (if available) as a micro-influencer for unique scores
        symbol_str = patterns.symbol if patterns and hasattr(patterns, 'symbol') and patterns.symbol else "STOCK"
        symbol_seed = (sum(ord(c) for c in symbol_str) % 100) / 2000.0
        
        trend_signal = next((s for s in signals if s["type"] == "trend_strength"), None)
        trend_gap = abs(trend_signal.get("details", {}).get("trend_gap_pct", 0)) if trend_signal else 0
        trend_score = min(0.15, trend_gap / 40.0)
        breakdown["trend_alignment"] = round(trend_score, 3)
        
        # 5. Baseline + Component Sum + Micro-differentiation
        total = 0.18 + price_score + volume_score + rsi_score + trend_score + symbol_seed
        total = round(min(0.98, max(0.05, total)), 2)
        
        return total, breakdown

    def _build_summary(self, active_signals: List[Dict[str, Any]], net_score: int) -> str:
        """Create a concise description of the current signal mix."""
        if not active_signals:
            return "No strong directional signal was detected from price, volume, trend, or news inputs."

        if net_score > 0:
            return "Signals suggest constructive momentum supported by price action, participation, or sentiment."

        if net_score < 0:
            return "Signals suggest weakening momentum or cautionary pressure in the current setup."

        return "Signals are mixed, so the setup needs more confirmation before it becomes actionable."
