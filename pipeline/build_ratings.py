"""Phase 2 — build data/teams.json from raw sources.

Combines the authoritative 2026 draw (seed_draw_2026.py) with the raw Elo table
downloaded into data/sources/ (eloratings.net World.tsv). Each team object carries:
  * Elo rating + global Elo rank (from eloratings.net),
  * group, confederation, FIFA/Elo codes,
  * placeholders for fifa_rank / form / xg / wc_knockout_history (filled by later
    fetch steps), and
  * a `sources` list pointing back to the raw file(s) used.

Usage:
    python build_ratings.py
"""
from __future__ import annotations

import glob
from pathlib import Path

from common import TEAMS_FILE, SOURCES_DIR, save_json
from seed_draw_2026 import TEAMS_2026
from seed_fifa_rankings import FIFA_RANK


def _latest_source(pattern: str) -> Path:
    matches = sorted(glob.glob(str(SOURCES_DIR / pattern)))
    if not matches:
        raise FileNotFoundError(
            f"No source file matching {pattern} in {SOURCES_DIR}. "
            "Run fetch_data.py / download the Elo table first."
        )
    return Path(matches[-1])  # dated filenames sort chronologically


def load_elo() -> tuple[dict[str, dict], str]:
    """Return {elo_code: {'elo': int, 'rank': int}} plus the source filename."""
    src = _latest_source("elo_world_*.tsv")
    elo: dict[str, dict] = {}
    with src.open("r", encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 4:
                continue
            global_rank, _, code, rating = cols[0], cols[1], cols[2], cols[3]
            try:
                elo[code] = {"elo": int(rating), "rank": int(global_rank)}
            except ValueError:
                continue
    return elo, src.name


def main() -> None:
    elo, elo_src = load_elo()

    teams = []
    missing = []
    for group, name, fifa_code, elo_code, confederation in TEAMS_2026:
        entry = elo.get(elo_code)
        if entry is None:
            missing.append(f"{name} ({elo_code})")
        teams.append({
            "id": fifa_code,
            "name": name,
            "elo_code": elo_code,
            "confederation": confederation,
            "group": group,
            "elo": entry["elo"] if entry else None,
            "elo_rank": entry["rank"] if entry else None,
            "fifa_rank": FIFA_RANK.get(fifa_code),  # FIFA June 2026 (seed_fifa_rankings)
            "form": None,                 # filled by a later form fetch
            "xg": None,                   # filled where available (FBref)
            "wc_knockout_history": None,  # filled from historical dataset
            "sources": [f"sources/{elo_src}"],
        })

    # Sort by group then descending Elo for readable diffs.
    teams.sort(key=lambda t: (t["group"], -(t["elo"] or 0)))
    save_json(TEAMS_FILE, teams)

    print(f"[build_ratings] wrote {len(teams)} teams to {TEAMS_FILE.name} "
          f"(Elo source: {elo_src})")
    if missing:
        print(f"[build_ratings] WARNING: no Elo match for: {', '.join(missing)}")
    else:
        print("[build_ratings] all 48 teams matched to an Elo rating ✓")


if __name__ == "__main__":
    main()
