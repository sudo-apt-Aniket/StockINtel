
import sys
import os
from pathlib import Path

# Add the project root to sys.path
root = Path("c:/et genai")
sys.path.append(str(root))

from backend.agents.base import AgentRequest
from backend.services.analysis_pipeline import StockAnalysisPipeline
from backend.agents.data_fetch_agent import DataFetchAgent
from backend.services.market_data_service import get_market_data_provider, NseYahooMarketDataProvider
from backend.services.news_service import get_news_provider
from backend.utils.logging import configure_logging
from config.settings import get_settings

def test_integration():
    configure_logging()
    settings = get_settings()
    out_lines = []
    out_lines.append(f"Current Market Provider: {settings.market_data_provider}")
    
    pipeline = StockAnalysisPipeline(
        data_fetch_agent=DataFetchAgent(
            provider=get_market_data_provider(settings.market_data_provider),
            news_provider=get_news_provider(settings.news_provider, settings.news_api_key),
        )
    )
    
    # Analyze RELIANCE.NS
    request = AgentRequest(
        symbol="RELIANCE.NS",
        timeframe="1d",
        portfolio=[],
        include_news=True
    )
    
    try:
        result = pipeline.run(request)
        out_lines.append("\n--- Market Snapshot ---")
        out_lines.append(f"Symbol: {result.market_snapshot.symbol}")
        out_lines.append(f"Latest Price: {result.market_snapshot.latest_price}")
        
        out_lines.append("\n--- Signals ---")
        out_lines.append(f"Confidence: {result.signals.confidence}")
        for signal in result.signals.signals:
            out_lines.append(f"- {signal['type']}: {signal['status']} (score: {signal['score']})")
            out_lines.append(f"  Details: {signal['details']}")
        
        out_lines.append("\n--- AI Explanation ---")
        out_lines.append(f"Alert: {result.explanation.alert}")
        out_lines.append(f"Recommendation: {result.explanation.recommendation}")
        out_lines.append(f"Rationale: {result.explanation.rationale}")
    except Exception as e:
        out_lines.append(f"\n--- ERROR ---\n{str(e)}")
        import traceback
        out_lines.append(traceback.format_exc())

    with open("c:/et genai/test_final_result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

if __name__ == "__main__":
    test_integration()
