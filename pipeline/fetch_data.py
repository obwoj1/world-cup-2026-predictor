"""Phase 2 — fetch raw data into data/sources/.

Downloads raw payloads verbatim into data/sources/ with a dated filename so every
downstream number is traceable. Currently wired up for eloratings.net (team Elo table
+ country-code map). FIFA rankings, FBref/Transfermarkt player stats, and API-Football
live results are added as follow-on fetchers.

Usage:
    python fetch_data.py --all
    python fetch_data.py --elo
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess

from common import SOURCES_DIR

USER_AGENT = "Mozilla/5.0 (compatible; wc2026-predictor/0.1; data pipeline)"

# stem -> (url, extension). All are free, no API key required.
SOURCES = {
    "elo_world": ("https://www.eloratings.net/World.tsv", "tsv"),
    "elo_teamcodes": ("https://www.eloratings.net/en.teams.tsv", "tsv"),
    "fixtures_fixturedownload": ("https://fixturedownload.com/feed/json/fifa-world-cup-2026", "json"),
    "wiki_squads_raw": ("https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads?action=raw", "txt"),
}
ELO_ONLY = {"elo_world", "elo_teamcodes"}


def _download(url: str, dest_stem: str, ext: str) -> str:
    # Use curl: reliable TLS on macOS where Python's urllib often lacks CA roots.
    today = dt.date.today().isoformat()
    dest = SOURCES_DIR / f"{dest_stem}_{today}.{ext}"
    subprocess.run(
        ["curl", "-sSf", "-m", "40", "-A", USER_AGENT, "-o", str(dest), url],
        check=True,
    )
    size = dest.stat().st_size if dest.exists() else 0
    print(f"[fetch_data] {url} -> {dest.name} ({size:,} bytes)")
    return dest.name


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch raw WC 2026 data into data/sources/")
    parser.add_argument("--all", action="store_true", help="Fetch every available source")
    parser.add_argument("--elo", action="store_true", help="Fetch only Elo ratings + codes")
    args = parser.parse_args()

    if not (args.all or args.elo):
        parser.print_help()
        return

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    for stem, (url, ext) in SOURCES.items():
        if args.elo and stem not in ELO_ONLY:
            continue
        _download(url, stem, ext)


if __name__ == "__main__":
    main()
