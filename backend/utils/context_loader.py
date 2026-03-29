"""Helpers for loading context-engineering assets from disk."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


def load_context_files(context_dir: Path) -> Dict[str, str]:
    """Load text context files into a dictionary keyed by stem name."""
    context_map: Dict[str, str] = {}
    for file_path in sorted(context_dir.glob("*.txt")):
        context_map[file_path.stem] = file_path.read_text(encoding="utf-8").strip()
    return context_map
