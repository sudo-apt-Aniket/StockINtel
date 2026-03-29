"""Pytest configuration for project import paths."""

from __future__ import annotations

import sys
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("STOCK_INTEL_MARKET_DATA_PROVIDER", "mock")
os.environ.setdefault("STOCK_INTEL_NEWS_PROVIDER", "mock")
os.environ.setdefault("STOCK_INTEL_DATABASE_PATH", str(PROJECT_ROOT / "data" / "test_stock_intelligence.db"))
