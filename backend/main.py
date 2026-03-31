"""FastAPI entrypoint for the stock intelligence backend."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from backend.agents.base import AgentRequest
from backend.agents.data_fetch_agent import DataFetchAgent
from backend.services.market_data_service import get_market_data_provider
from backend.services.news_service import get_news_provider
from backend.services.analysis_pipeline import StockAnalysisPipeline
from backend.services.database import Database
from backend.services.persistence_service import PersistenceService
from backend.utils.context_loader import load_context_files
from backend.utils.logging import configure_logging, log_event
from config.settings import get_settings


class AnalyzeStockPayload(BaseModel):
    """Input payload for stock analysis requests."""

    symbol: str = Field(..., examples=["RELIANCE.NS"], description="Ticker symbol to analyze.")
    timeframe: str = Field(default="1d", description="Requested analysis timeframe.")
    portfolio: List[str] = Field(default_factory=list, examples=[["TCS.NS", "INFY.NS"]], description="Optional list of portfolio symbols.")
    portfolio_name: Optional[str] = Field(default=None, description="Name of a stored portfolio to fetch symbols from.")
    include_news: bool = Field(default=True, description="Whether to include news placeholders.")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        """Normalize and validate the incoming ticker symbol."""
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Ticker symbol must not be empty.")
        if not normalized.replace(".", "").isalnum():
            raise ValueError("Ticker symbol must be alphanumeric.")
        return normalized

    @field_validator("portfolio")
    @classmethod
    def validate_portfolio(cls, value: List[str]) -> List[str]:
        """Normalize portfolio symbols and drop blank entries."""
        normalized = [item.strip().upper() for item in value if item.strip()]
        return normalized


class StrictStockResponse(BaseModel):
    symbol: str
    signal: str
    confidence: float
    action: str
    explanation: str
    reasoning: str
    risk: str
    insight: str
    portfolio_context: str
    rsi: float
    volatility: float
    timestamp: str

class RadarPayload(BaseModel):
    """Payload to scan multiple symbols."""
    symbols: List[str] = Field(..., description="List of stock symbols to scan.")
    timeframe: str = Field(default="1d", description="Requested analysis timeframe.")
    include_news: bool = Field(default=False, description="Whether to include news (slower).")

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, value: List[str]) -> List[str]:
        return [item.strip().upper() for item in value if item.strip()]

class RadarResponse(BaseModel):
    """Ranked radar results."""
    results: List[StrictStockResponse]


class StoredAnalysisResponse(BaseModel):
    """Persisted analysis summary record."""

    analysis_id: int
    symbol: str
    timeframe: str
    confidence: float
    created_at: str
    summary: Dict[str, Any]


class AnalysisDetailResponse(BaseModel):
    """Detailed persisted analysis record."""

    analysis_id: int
    symbol: str
    timeframe: str
    confidence: float
    created_at: str
    request: Dict[str, Any]
    summary: Dict[str, Any]
    market_snapshot: Dict[str, Any]
    signals: Dict[str, Any]
    patterns: Dict[str, Any]
    pipeline: List[Dict[str, Any]]


class StoredAlertResponse(BaseModel):
    """Persisted alert record."""

    alert_id: int
    analysis_id: int
    symbol: str
    alert: str
    recommendation: str
    confidence: float
    status: str
    created_at: str
    updated_at: str


class UpdateAlertStatusPayload(BaseModel):
    """Payload for changing alert lifecycle state."""

    status: str = Field(..., description="New alert status: open, acknowledged, or closed.")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"open", "acknowledged", "closed"}:
            raise ValueError("Status must be one of: open, acknowledged, closed.")
        return normalized


class PortfolioPayload(BaseModel):
    """Payload to create or update a portfolio."""
    name: str = Field(..., description="Unique portfolio name.")
    symbols: List[str] = Field(..., description="List of stock symbols.")

class PortfolioResponse(BaseModel):
    """Stored portfolio metadata."""
    id: int
    name: str
    symbols: List[str]
    created_at: str
    updated_at: str


class HealthResponse(BaseModel):
    """Operational health and readiness response."""

    status: str
    environment: str
    storage_ready: bool
    providers: Dict[str, Any]


BASE_DIR = Path(__file__).resolve().parent.parent
CONTEXT_DIR = BASE_DIR / "context"
configure_logging()
logger = logging.getLogger(__name__)
request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")
settings = get_settings()
database = Database(settings.database_path)
persistence_service = PersistenceService(
    database=database,
    alert_confidence_threshold=settings.alert_confidence_threshold,
)
pipeline = StockAnalysisPipeline(
    data_fetch_agent=DataFetchAgent(
        provider=get_market_data_provider(settings.market_data_provider),
        news_provider=get_news_provider(settings.news_provider, settings.news_api_key),
    ),
    context_dir=CONTEXT_DIR,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize app resources during startup."""
    persistence_service.initialize()
    log_event(logger, "storage_initialized", database_path=str(settings.database_path))
    yield


app = FastAPI(
    title="Stock Intelligence API",
    version="0.1.0",
    description="AI-powered stock intelligence backend prepared for future multi-agent orchestration.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Welcome page for the backend API."""
    return {
        "message": "Stock Intelligence API is Live",
        "docs": "/docs",
        "health": "/health",
        "status": "operational",
        "neural_engine": "v2 (Grounded)"
    }


@app.get("/ping")
def ping():
    return {"status": "pong"}


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """Attach a request id and emit request lifecycle logs."""
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request_id_context.set(request_id)
    log_event(logger, "request_started", request_id=request_id, path=request.url.path, method=request.method)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    log_event(
        logger,
        "request_completed",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
    )
    return response


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return operational health and provider readiness details."""
    storage_ready = settings.database_path.exists()
    market_provider_ready = settings.market_data_provider in {"mock", "yfinance", "yahoo_finance", "nse_yahoo_finance"}
    news_provider_ready = settings.news_provider in {"mock", "yfinance", "yahoo_finance", "nse_yahoo_finance"} or (
        settings.news_provider == "newsapi" and bool(settings.news_api_key)
    )

    overall_status = "ok" if storage_ready and market_provider_ready and news_provider_ready else "degraded"
    return HealthResponse(
        status=overall_status,
        environment=settings.environment,
        storage_ready=storage_ready,
        providers={
            "market_data": {
                "provider": settings.market_data_provider,
                "ready": market_provider_ready,
            },
            "news": {
                "provider": settings.news_provider,
                "ready": news_provider_ready,
                "requires_api_key": settings.news_provider == "newsapi",
            },
        },
    )


@app.get("/context")
def get_context() -> Dict[str, Any]:
    """Expose loaded context-engineering assets for debugging and prompt assembly."""
    return {"context": load_context_files(CONTEXT_DIR)}


@app.get("/analyses", response_model=List[StoredAnalysisResponse])
def list_recent_analyses(limit: int = 20) -> List[StoredAnalysisResponse]:
    """Return recently stored stock analyses."""
    records = persistence_service.list_recent_analyses(limit=limit)
    return [StoredAnalysisResponse(**record) for record in records]


@app.get("/analyses/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(analysis_id: int) -> AnalysisDetailResponse:
    """Return a persisted analysis by id."""
    record = persistence_service.get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return AnalysisDetailResponse(**record)


@app.get("/alerts", response_model=List[StoredAlertResponse])
def list_open_alerts(limit: int = 20) -> List[StoredAlertResponse]:
    """Return recently generated open alerts."""
    records = persistence_service.list_open_alerts(limit=limit)
    return [StoredAlertResponse(**record) for record in records]


@app.patch("/alerts/{alert_id}", response_model=StoredAlertResponse)
def update_alert_status(alert_id: int, payload: UpdateAlertStatusPayload) -> StoredAlertResponse:
    """Update an alert lifecycle status."""
    try:
        record = persistence_service.update_alert_status(alert_id=alert_id, status=payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if record is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    return StoredAlertResponse(**record)


@app.post("/portfolios", response_model=PortfolioResponse)
def create_portfolio(payload: PortfolioPayload) -> PortfolioResponse:
    """Create or update a list of portfolio symbols."""
    record = persistence_service.save_portfolio(payload.name, payload.symbols)
    return PortfolioResponse(**record)


@app.get("/portfolios/{name}", response_model=PortfolioResponse)
def get_portfolio(name: str) -> PortfolioResponse:
    """Retrieve a stored portfolio by its unique name."""
    record = persistence_service.get_portfolio(name)
    if not record:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    return PortfolioResponse(**record)

@app.get("/portfolio", response_model=List[PortfolioResponse])
def get_all_portfolios() -> List[PortfolioResponse]:
    """Retrieve all stored portfolios."""
    records = persistence_service.list_portfolios()
    return [PortfolioResponse(**record) for record in records]


@app.post("/radar", response_model=RadarResponse)
def opportunity_radar(payload: RadarPayload) -> RadarResponse:
    """Scan multiple stocks and return them sorted by confidence."""
    import datetime
    results = []
    request_id = request_id_context.get()
    symbols = payload.symbols or ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ITC"]
    
    logger.info(f"RADAR_START: request_id={request_id} symbols={symbols}")
    
    for symbol in symbols:
        inner_request = AgentRequest(
            symbol=symbol,
            timeframe=payload.timeframe,
            portfolio=[],
            include_news=payload.include_news,
        )
        try:
            logger.info(f"RADAR_PROCESSING: {symbol}")
            result = pipeline.run(inner_request)
            response = result.to_dict()
            
            # Map to strict format
            action_map = {"buy": "buy", "sell": "sell", "neutral": "hold", "bullish": "buy", "bearish": "sell", "watch": "watch"}
            rec = response["explanation"]["recommendation"].lower()
            action = next((v for k, v in action_map.items() if k in rec), "hold")
            if "watch" in rec: action = "watch"
            
            sig_text = response["explanation"]["alert"].lower()
            signal = "bullish" if "bullish" in sig_text or "constructive" in sig_text else "bearish" if "bearish" in sig_text or "weakness" in sig_text else "neutral"

            res = StrictStockResponse(
                symbol=symbol,
                signal=signal,
                confidence=result.signals.confidence,
                action=action.upper(),
                explanation=response["explanation"]["alert"],
                reasoning=response["explanation"]["rationale"],
                risk="Market conditions and specific sentiment risks apply.",
                insight=response["explanation"]["recommendation"],
                portfolio_context=response["explanation"].get("portfolio_insights", "No portfolio provided."),
                rsi=response["patterns"].get("rsi", 50.0),
                volatility=response["patterns"].get("volatility", 0.0),
                timestamp=datetime.datetime.utcnow().isoformat() + "Z"
            )
            results.append(res)
            logger.info(f"RADAR_SUCCESS: {symbol} score={res.confidence}")
        except Exception as exc:
            logger.error(f"RADAR_FAILURE: {symbol} error={str(exc)}")
            results.append(StrictStockResponse(
                symbol=symbol, signal="neutral", confidence=0.0, action="ERROR",
                explanation=f"Analysis failed: {str(exc)}",
                reasoning="Processing error.", risk="N/A", insight="N/A", portfolio_context="N/A",
                rsi=50.0, volatility=0.0, timestamp=datetime.datetime.utcnow().isoformat() + "Z"
            ))
            
    results.sort(key=lambda x: x.confidence, reverse=True)
    logger.info(f"RADAR_COMPLETE: count={len(results)}")
    return RadarResponse(results=results)


@app.post("/analyze", response_model=StrictStockResponse)
def analyze_stock(payload: AnalyzeStockPayload) -> StrictStockResponse:
    """Run the placeholder end-to-end stock intelligence pipeline."""
    import datetime
    request_id = request_id_context.get()
    
    portfolio_symbols = payload.portfolio.copy()
    if payload.portfolio_name:
        record = persistence_service.get_portfolio(payload.portfolio_name)
        if record:
            portfolio_symbols.extend(record["symbols"])

    request = AgentRequest(
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        portfolio=list(set(portfolio_symbols)),
        include_news=payload.include_news,
    )
    log_event(logger, "analysis_requested", request_id=request_id, symbol=request.symbol)
    try:
        result = pipeline.run(request)
    except ValueError as exc:
        log_event(logger, "analysis_rejected", request_id=request_id, symbol=request.symbol, error=str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        log_event(logger, "analysis_failed", request_id=request_id, symbol=request.symbol, error=str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    response = result.to_dict()
    persistence_result = persistence_service.save_analysis(
        {
            "request": response["request"],
            "summary": {
                "symbol": response["explanation"]["symbol"],
                "alert": response["explanation"]["alert"],
                "recommendation": response["explanation"]["recommendation"],
                "confidence": response["explanation"]["confidence"],
                "rationale": response["explanation"]["rationale"],
                "portfolio_insights": response["explanation"].get("portfolio_insights"),
            },
            "market_snapshot": response["market_snapshot"],
            "signals": response["signals"],
            "patterns": response["patterns"],
            "pipeline": response["stages"],
        }
    )
    log_event(
        logger,
        "analysis_completed",
        request_id=request_id,
        symbol=request.symbol,
        confidence=response["explanation"]["confidence"],
        analysis_id=persistence_result["analysis_id"],
        alert_id=persistence_result["alert_id"],
    )
    
    # Map to strict format
    action_map = {"buy": "buy", "sell": "sell", "neutral": "hold", "bullish": "buy", "bearish": "sell", "watch": "watch"}
    rec = response["explanation"]["recommendation"].lower()
    action = next((v for k, v in action_map.items() if k in rec), "hold")
    if "watch" in rec: action = "watch"
    
    sig_text = response["explanation"]["alert"].lower()
    signal = "bullish" if "bullish" in sig_text or "constructive" in sig_text else "bearish" if "bearish" in sig_text or "weakness" in sig_text else "neutral"

    return StrictStockResponse(
        symbol=response["explanation"]["symbol"],
        signal=signal,
        confidence=response["explanation"]["confidence"],
        action=action.upper(),
        explanation=response["explanation"]["alert"],
        reasoning=response["explanation"]["rationale"],
        risk="Market conditions and specific sentiment risks apply.",
        insight=response["explanation"]["recommendation"],
        portfolio_context=response["explanation"].get("portfolio_insights") or "No portfolio provided.",
        rsi=response["patterns"].get("rsi", 50.0),
        volatility=response["patterns"].get("volatility", 0.0),
        timestamp=datetime.datetime.utcnow().isoformat() + "Z"
    )
