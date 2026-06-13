"""Phase 2 — fetch raw data into data/sources/.

Pulls team Elo, FIFA rankings, recent form, player club/international stats, and the
WC 2026 fixture list from public sources. Each raw payload is saved verbatim under
data/sources/ with a dated filename, and logged in data/sources/SOURCES.md so every
downstream number is traceable.

Usage:
    python fetch_data.py --all
    python fetch_data.py --elo --fixtures

NOTE: stub — implemented in Phase 2.
"""
from __future__ import annotations

import argparse

from common import SOURCES_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch raw WC 2026 data into data/sources/")
    parser.add_argument("--all", action="store_true", help="Fetch every source")
    parser.add_argument("--elo", action="store_true", help="Fetch team Elo ratings")
    parser.add_argument("--rankings", action="store_true", help="Fetch FIFA rankings")
    parser.add_argument("--players", action="store_true", help="Fetch player stats")
    parser.add_argument("--fixtures", action="store_true", help="Fetch the fixture list")
    args = parser.parse_args()

    print(f"[fetch_data] target dir: {SOURCES_DIR}")
    print("[fetch_data] stub — wire up sources in Phase 2.")
    _ = args


if __name__ == "__main__":
    main()
