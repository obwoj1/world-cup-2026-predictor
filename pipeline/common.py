"""Shared paths and JSON helpers for the World Cup 2026 prediction pipeline.

Keeping all path logic in one place means every script reads and writes the same
canonical files under ../data, and the web app reads those exact files.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Repo-relative paths (this file lives in pipeline/)
PIPELINE_DIR = Path(__file__).resolve().parent
ROOT_DIR = PIPELINE_DIR.parent
DATA_DIR = ROOT_DIR / "data"
SOURCES_DIR = DATA_DIR / "sources"
RECONCILIATIONS_DIR = ROOT_DIR / "reconciliations"

TEAMS_FILE = DATA_DIR / "teams.json"
PLAYERS_FILE = DATA_DIR / "players.json"
FIXTURES_FILE = DATA_DIR / "fixtures.json"
RESULTS_FILE = DATA_DIR / "results.json"
PREDICTIONS_FILE = DATA_DIR / "predictions.json"

MODEL_VERSION = "0.1.0"


def load_json(path: Path) -> Any:
    """Load a JSON file, returning [] if it doesn't exist yet."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    """Write JSON with stable, diff-friendly formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")
