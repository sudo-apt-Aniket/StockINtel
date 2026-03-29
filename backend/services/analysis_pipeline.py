"""Lightweight orchestration layer for coordinating backend agents."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.agents.base import AgentRequest, PipelineResult, PipelineStageStatus
from backend.agents.data_fetch_agent import DataFetchAgent
from backend.agents.explanation_agent import ExplanationAgent
from backend.agents.pattern_agent import PatternAnalysisAgent
from backend.agents.signal_agent import SignalDetectionAgent
from backend.utils.context_loader import load_context_files
from backend.utils.logging import log_event


logger = logging.getLogger(__name__)


class StockAnalysisPipeline:
    """Coordinates agent execution while keeping agent boundaries explicit."""

    def __init__(
        self,
        data_fetch_agent: Optional[DataFetchAgent] = None,
        signal_agent: Optional[SignalDetectionAgent] = None,
        pattern_agent: Optional[PatternAnalysisAgent] = None,
        explanation_agent: Optional[ExplanationAgent] = None,
        context_dir: Optional[Path] = None,
    ) -> None:
        self.data_fetch_agent = data_fetch_agent or DataFetchAgent()
        self.signal_agent = signal_agent or SignalDetectionAgent()
        self.pattern_agent = pattern_agent or PatternAnalysisAgent()
        self.explanation_agent = explanation_agent or ExplanationAgent()
        self.context_dir = context_dir or Path(__file__).resolve().parents[2] / "context"

    def run(self, request: AgentRequest) -> PipelineResult:
        """Execute the full placeholder stock intelligence workflow."""
        self._validate_request(request)
        log_event(logger, "pipeline_started", symbol=request.symbol, timeframe=request.timeframe)
        context: Dict[str, Any] = {
            "context_files": load_context_files(self.context_dir),
        }
        stages: List[PipelineStageStatus] = []

        market_snapshot = self._run_stage(
            stage_name="data_fetch",
            agent=self.data_fetch_agent,
            request=request,
            context=context,
            output_key="market_snapshot",
            stages=stages,
        )
        patterns = self._run_stage(
            stage_name="pattern_analysis",
            agent=self.pattern_agent,
            request=request,
            context=context,
            output_key="patterns",
            stages=stages,
        )
        signals = self._run_stage(
            stage_name="signal_detection",
            agent=self.signal_agent,
            request=request,
            context=context,
            output_key="signals",
            stages=stages,
        )
        explanation = self._run_stage(
            stage_name="explanation",
            agent=self.explanation_agent,
            request=request,
            context=context,
            output_key="explanation",
            stages=stages,
        )

        result = PipelineResult(
            request=request,
            market_snapshot=market_snapshot,
            signals=signals,
            patterns=patterns,
            explanation=explanation,
            context_files=context["context_files"],
            stages=stages,
        )
        log_event(
            logger,
            "pipeline_completed",
            symbol=request.symbol,
            stage_count=len(stages),
            confidence=explanation.confidence,
        )
        return result

    def _run_stage(
        self,
        stage_name: str,
        agent: Any,
        request: AgentRequest,
        context: Dict[str, Any],
        output_key: str,
        stages: List[PipelineStageStatus],
    ) -> Any:
        """Run an agent, store its output in context, and record stage completion."""
        try:
            log_event(logger, "stage_started", stage=stage_name, symbol=request.symbol)
            result = agent.run(request, context)
        except Exception as exc:
            stages.append(
                PipelineStageStatus(stage=stage_name, status="failed", error=str(exc))
            )
            log_event(logger, "stage_failed", stage=stage_name, symbol=request.symbol, error=str(exc))
            raise RuntimeError(f"Pipeline stage '{stage_name}' failed") from exc

        context[output_key] = result
        stages.append(PipelineStageStatus(stage=stage_name, status="completed"))
        log_event(logger, "stage_completed", stage=stage_name, symbol=request.symbol)
        return result

    def _validate_request(self, request: AgentRequest) -> None:
        """Validate request values before any agent work begins."""
        if not request.symbol or not request.symbol.strip():
            raise ValueError("Symbol is required.")

        supported_timeframes = {"1d", "5d", "1mo", "3mo"}
        if request.timeframe not in supported_timeframes:
            raise ValueError(
                f"Unsupported timeframe '{request.timeframe}'. Supported values: {sorted(supported_timeframes)}."
            )
