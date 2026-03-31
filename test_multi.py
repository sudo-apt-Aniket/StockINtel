
import sys
import os
from pathlib import Path

# Add the project root to sys.path
root = Path("c:/et genai")
sys.path.append(str(root))

from backend.agents.base import AgentRequest
from backend.services.analysis_pipeline import StockAnalysisPipeline
from backend.agents.data_fetch_agent import DataFetchAgent
from backend.services.market_data_service import get_market_data_provider
from backend.services.news_service import get_news_provider
from backend.utils.logging import configure_logging
from config.settings import get_settings

def test_multi_integration():
    configure_logging()
    settings = get_settings()
    out_lines = []
    
    pipeline = StockAnalysisPipeline(
        data_fetch_agent=DataFetchAgent(
            provider=get_market_data_provider(settings.market_data_provider),
            news_provider=get_news_provider(settings.news_provider, settings.news_api_key),
        )
    )
    
    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    
    for symbol in symbols:
        out_lines.append(f"\n=== Testing {symbol} ===")
        request = AgentRequest(symbol=symbol, timeframe="1d", portfolio=[], include_news=True)
        try:
            result = pipeline.run(request)
            out_lines.append(f"Price: {result.market_snapshot.latest_price}")
            out_lines.append(f"Confidence: {result.signals.confidence}")
            out_lines.append(f"Alert: {result.explanation.alert}")
        except Exception as e:
            out_lines.append(f"ERROR: {str(e)}")

    with open("c:/et genai/test_multi_result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

if __name__ == "__main__":
    test_multi_integration()
