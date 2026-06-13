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
import urllib.request

from common import SOURCES_DIR

USER_AGENT = "Mozilla/5.0 (compatible; wc2026-predictor/0.1; data pipeline)"

ELO_SOURCES = {
    "elo_world": "https://www.eloratings.net/World.tsv",
    "elo_teamcodes": "https://www.eloratings.net/en.teams.tsv",
}


def _download(url: str, dest_stem: str) -> str:
    today = dt.date.today().isoformat()
    dest = SOURCES_DIR / f"{dest_stem}_{today}.tsv"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (trusted host)
        data = resp.read()
    dest.write_bytes(data)
    print(f"[fetch_data] {url} -> {dest.name} ({len(data):,} bytes)")
    return dest.name


def fetch_elo() -> None:
    for stem, url in ELO_SOURCES.items():
        _download(url, stem)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch raw WC 2026 data into data/sources/")
    parser.add_argument("--all", action="store_true", help="Fetch every available source")
    parser.add_argument("--elo", action="store_true", help="Fetch team Elo ratings + codes")
    args = parser.parse_args()

    if not (args.all or args.elo):
        parser.print_help()
        return

    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    if args.all or args.elo:
        fetch_elo()


if __name__ == "__main__":
    main()
