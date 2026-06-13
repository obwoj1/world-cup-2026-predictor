"""Phase 2/3 — turn raw sources into data/teams.json and data/players.json.

Reads the raw payloads in data/sources/, computes/normalizes Elo, recent form (last
10-15 matches), xG/xGA, and WC knockout history into the schemas documented in
data/SCHEMA.md. Each output object carries a `sources` list pointing back to the raw
files used.

Usage:
    python build_ratings.py

NOTE: stub — implemented in Phase 2.
"""
from __future__ import annotations

from common import TEAMS_FILE, PLAYERS_FILE, load_json, save_json


def main() -> None:
    teams = load_json(TEAMS_FILE)
    players = load_json(PLAYERS_FILE)
    print(f"[build_ratings] loaded {len(teams)} teams, {len(players)} players")
    print("[build_ratings] stub — compute ratings from data/sources/ in Phase 2.")
    # Re-save unchanged for now so the file formatting stays canonical.
    save_json(TEAMS_FILE, teams)
    save_json(PLAYERS_FILE, players)


if __name__ == "__main__":
    main()
