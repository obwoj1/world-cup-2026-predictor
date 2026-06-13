"""Phase 3 — the prediction engine.

For every remaining fixture, computes:
  * expected goals for each side from an Elo + recent-form + host-advantage model,
  * win/draw/loss probabilities and a predicted scoreline via a Poisson model,
  * a confidence level,
  * a short evidence-cited reasoning paragraph,
  * 1-3 players to watch tied to underlying stats.

Writes everything to data/predictions.json (schema in data/SCHEMA.md).

Usage:
    python predict.py                 # predict all remaining matches
    python predict.py --stage group   # limit to a stage

NOTE: stub — Poisson/Elo math implemented in Phase 3.
"""
from __future__ import annotations

import argparse

from common import (
    FIXTURES_FILE,
    RESULTS_FILE,
    PREDICTIONS_FILE,
    TEAMS_FILE,
    load_json,
    save_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict remaining WC 2026 matches")
    parser.add_argument("--stage", help="Limit to a stage (group, r32, r16, qf, sf, final)")
    args = parser.parse_args()

    teams = load_json(TEAMS_FILE)
    fixtures = load_json(FIXTURES_FILE)
    results = load_json(RESULTS_FILE)
    played = {r["id"] for r in results}
    remaining = [f for f in fixtures if f["id"] not in played]
    if args.stage:
        remaining = [f for f in remaining if f.get("stage") == args.stage]

    print(f"[predict] {len(teams)} teams, {len(remaining)} remaining fixtures to predict")
    print("[predict] stub — Poisson + Elo engine implemented in Phase 3.")
    save_json(PREDICTIONS_FILE, load_json(PREDICTIONS_FILE))


if __name__ == "__main__":
    main()
