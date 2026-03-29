"""Explanation Agent for generating investor-friendly narratives."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import httpx

from config.settings import get_settings
from .base import AgentRequest, ExplanationResult, PatternResult, SignalResult


class ExplanationAgent:
    """Transforms structured analysis into plain-language investor guidance."""

    def run(self, request: AgentRequest, context: Dict[str, Any]) -> ExplanationResult:
        """Create a natural language explanation from agent outputs."""
        signals: SignalResult = context["signals"]
        patterns: PatternResult = context["patterns"]
        return self.generate_explanation(request, signals, patterns)

    def generate_explanation(
        self,
        request: AgentRequest,
        signals: SignalResult,
        patterns: PatternResult,
    ) -> ExplanationResult:
        """Generate an explanation using an LLM, otherwise fallback to deterministic mix."""
        settings = get_settings()
        if settings.openai_api_key:
            try:
                return self._generate_llm_explanation(request, signals, patterns, settings.openai_api_key)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"LLM explanation failed: {e}. Falling back to deterministic.")

        return self._generate_deterministic_explanation(request, signals, patterns)

    def _generate_llm_explanation(
        self,
        request: AgentRequest,
        signals: SignalResult,
        patterns: PatternResult,
        api_key: str,
    ) -> ExplanationResult:
        """Use OpenAI LLM to generate a concise, human-readable insight for a retail investor."""
        prompt = (
            f"Act as a professional and accessible financial assistant for a retail investor. "
            f"Your goal is to explain technical market setups without using heavy jargon.\n"
            f"Provide a highly concise, human-friendly 3-5 sentence analysis for {request.symbol} based purely on these technicals:\n"
            f"- Confidence Score: {signals.confidence}\n"
            f"- Signals: {json.dumps(signals.signals)}\n"
            f"- Patterns: {json.dumps(patterns.patterns)}\n"
            f"- Portfolio Symbols: {json.dumps(request.portfolio)}\n\n"
            f"Rules:\n"
            f"1. Explain what is happening in simple, conversational terms. Avoid words like 'stochastic', 'moving average convergence', or 'Bollinger'. Instead say 'price trend', 'momentum', or 'volatility'.\n"
            f"2. Be brief and actionable.\n"
            f"\nReturn ONLY a valid JSON object with EXACTLY these four keys:\n"
            f"1. 'explanation': human-readable summary of the current state.\n"
            f"2. 'reasoning': why the signals triggered and key risk factors.\n"
            f"3. 'insight': actionable takeaway.\n"
            f"4. 'portfolio_context': Insights regarding sector concentration or duplicate exposure, comparing {request.symbol} to the provided portfolio.\n"
        )

        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",
                "temperature": 0.0,
                "seed": 42,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "explanation_response",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "explanation": {
                                    "type": "string",
                                    "description": "Clear, jargon-free human-readable summary of the current state."
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Simple reasoning for why this setup matters and core risk factors."
                                },
                                "insight": {
                                    "type": "string",
                                    "description": "A very concise actionable takeaway for a retail investor."
                                },
                                "portfolio_context": {
                                    "type": "string",
                                    "description": "Simple insights on portfolio overlap or sector exposure, if any."
                                }
                            },
                            "required": ["explanation", "reasoning", "insight", "portfolio_context"],
                            "additionalProperties": False
                        }
                    }
                },
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
        content = json.loads(payload["choices"][0]["message"]["content"])

        # Add manual validation check before returning to ensure deterministic fallback if violated
        required_keys = {"explanation", "reasoning", "insight", "portfolio_context"}
        if not all(k in content for k in required_keys):
            raise ValueError("LLM response failed schema validation. Missing required keys.")

        return ExplanationResult(
            symbol=signals.symbol,
            alert=content["explanation"],
            recommendation=content["insight"],
            rationale=content["reasoning"],
            confidence=signals.confidence,
            portfolio_insights=content["portfolio_context"],
        )

    def _generate_deterministic_explanation(
        self,
        request: AgentRequest,
        signals: SignalResult,
        patterns: PatternResult,
    ) -> ExplanationResult:
        """Fallback method to generate an explanation aligned with the current signal and pattern mix."""
        signal_statuses = [signal["status"] for signal in signals.signals]
        bullish_count = signal_statuses.count("bullish")
        bearish_count = signal_statuses.count("bearish")
        watch_patterns = [pattern for pattern in patterns.patterns if pattern["status"] == "watch"]

        portfolio_note = (
            f"This symbol also appears in your tracked portfolio, so position exposure should be reviewed against {len(request.portfolio)} other holdings."
            if request.symbol.upper() in {item.upper() for item in request.portfolio}
            else f"Consider how adding {request.symbol} affects sector balance alongside your {len(request.portfolio)} current holdings." if request.portfolio else "No portfolio context provided."
        )

        stance = self._determine_stance(bullish_count, bearish_count)
        alert = self._build_alert(signals.symbol, signals.confidence, stance)
        recommendation = self._build_recommendation(stance, watch_patterns, patterns.rsi)
        rationale = self._build_rationale(
            signals=signals,
            patterns=patterns,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
        )

        return ExplanationResult(
            symbol=signals.symbol,
            alert=alert,
            recommendation=recommendation,
            rationale=rationale,
            confidence=signals.confidence,
            portfolio_insights=portfolio_note,
        )

    def _determine_stance(self, bullish_count: int, bearish_count: int) -> str:
        """Classify the overall setup direction from signal counts."""
        if bullish_count > bearish_count:
            return "bullish"
        if bearish_count > bullish_count:
            return "bearish"
        return "mixed"

    def _build_alert(self, symbol: str, confidence: float, stance: str) -> str:
        """Create a concise alert headline for the current setup."""
        if stance == "bullish":
            return f"{symbol} is showing a constructive setup with confidence {confidence:.2f}."
        if stance == "bearish":
            return f"{symbol} is showing cautionary weakness with confidence {confidence:.2f}."
        return f"{symbol} is showing mixed signals with confidence {confidence:.2f}."

    def _build_recommendation(
        self, stance: str, watch_patterns: List[Dict[str, Any]], rsi: Optional[float]
    ) -> str:
        """Create a short investor-facing recommendation."""
        has_breakout_watch = any(pattern["name"] == "breakout_setup" for pattern in watch_patterns)
        has_support_watch = any(pattern["name"] == "support_retest" for pattern in watch_patterns)

        if stance == "bullish":
            if has_breakout_watch:
                return "Watch for a clean breakout confirmation before acting, since momentum is improving."
            if rsi is not None and rsi >= 70:
                return "Momentum is strong, but the setup may be extended, so waiting for a pullback or confirmation is prudent."
            return "Momentum is favorable, but confirmation through follow-through price action is still important."

        if stance == "bearish":
            if has_support_watch:
                return "Use caution near support because a failed hold could strengthen the bearish setup."
            return "The setup is weakening, so waiting for stabilization or reversal evidence is safer than reacting early."

        return "Signals are mixed, so it is better to wait for clearer confirmation before making a directional decision."

    def _build_rationale(
        self,
        signals: SignalResult,
        patterns: PatternResult,
        bullish_count: int,
        bearish_count: int,
    ) -> str:
        """Combine structured outputs into a concise rationale."""
        pattern_highlights = self._summarize_patterns(patterns.patterns)
        directional_context = (
            f"Bullish signals: {bullish_count}; bearish signals: {bearish_count}. "
            f"Support is near {patterns.support_level}, resistance is near {patterns.resistance_level}, "
            f"and RSI is {patterns.rsi}. "
        )
        return f"{signals.summary} {directional_context}{pattern_highlights}"

    def _summarize_patterns(self, patterns: List[Dict[str, Any]]) -> str:
        """Summarize the most relevant pattern observations."""
        notable_patterns = [
            pattern["details"]
            for pattern in patterns
            if pattern["status"] in {"bullish", "bearish", "watch", "overbought", "oversold"}
        ]
        if not notable_patterns:
            return "No notable technical pattern stood out beyond the baseline support and resistance structure."
        return " Key pattern context: " + " ".join(notable_patterns[:2])
