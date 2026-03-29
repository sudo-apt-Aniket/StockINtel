# Stock Intelligence Backend

Production-ready FastAPI scaffold for an AI-powered stock intelligence system built with a context engineering approach.

## Project Structure

```text
project_root/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── data_fetch_agent.py
│   │   ├── explanation_agent.py
│   │   ├── pattern_agent.py
│   │   └── signal_agent.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── analysis_pipeline.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── context_loader.py
│   ├── __init__.py
│   └── main.py
├── config/
│   └── settings.py
├── context/
│   ├── constraints.txt
│   ├── output_format.txt
│   ├── project_context.txt
│   └── system_role.txt
├── prompts/
│   ├── base_prompt.txt
│   └── task_prompt_template.txt
├── requirements.txt
└── README.md
```

## Why This Structure

- Keeps context-engineering assets outside the code so prompts and rules are easy to revise.
- Separates agent responsibilities to support future orchestration frameworks such as OpenViking.
- Uses clear dataclass-based interfaces so agent inputs and outputs remain explicit and testable.
- Starts with placeholder logic that can be replaced by real market data, sentiment, and LLM integrations.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Run tests:

```bash
pytest
```

## Available Endpoints

- `GET /health` for health checks
- `GET /context` to inspect loaded context files
- `POST /analyze` to run the placeholder stock intelligence pipeline

## Data Providers

- Default market data provider: `nse_yahoo_finance`
- Default news provider: `nse_yahoo_finance`
- Optional alternate provider: `yfinance`
- Optional alternate live news provider: `newsapi`

Set the provider with:

```bash
export STOCK_INTEL_MARKET_DATA_PROVIDER=nse_yahoo_finance
export STOCK_INTEL_NEWS_PROVIDER=nse_yahoo_finance
```

Optional NewsAPI setup:

```bash
export STOCK_INTEL_NEWS_PROVIDER=newsapi
export STOCK_INTEL_NEWS_API_KEY=your_newsapi_key
```

Tests force `mock` providers so they stay deterministic.

## Observability

- API requests now emit structured JSON logs.
- Each request gets an `X-Request-ID` header for tracing.
- Pipeline stages log start, completion, and failure events.

## Persistence

- Completed analyses are stored in SQLite at `data/stock_intelligence.db` by default.
- Actionable analyses automatically generate open alert records.
- `GET /analyses` returns recent stored analyses.
- `GET /analyses/{analysis_id}` returns a full persisted analysis record.
- `GET /alerts` returns recent open alerts.
- `PATCH /alerts/{alert_id}` updates alert status to `open`, `acknowledged`, or `closed`.

## Deployment

Run locally with environment variables from `.env.example`.

Container build:

```bash
docker build -t stock-intelligence-api .
docker run --rm -p 8000:8000 --env-file .env.example stock-intelligence-api
```

Example request:

```json
{
  "symbol": "RELIANCE.NS",
  "timeframe": "1d",
  "portfolio": ["RELIANCE.NS", "TCS.NS"],
  "include_news": true
}
```

## OpenViking Readiness

This scaffold does not install or configure OpenViking.

It does prepare for future orchestration by:
- keeping each agent modular and independently instantiable
- using a lightweight pipeline instead of tightly coupled cross-calls
- defining consistent request and result models in a shared base module
- storing prompt and context artifacts in dedicated folders for reuse

## Next Steps

- Replace placeholder market data with real providers such as `yfinance` or broker APIs.
- Add persistent storage for alerts, watchlists, and user portfolios.
- Add test coverage for each agent and the pipeline.
- Introduce LLM-backed explanation generation once prompt assembly is finalized.
