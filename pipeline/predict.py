"""Phase 3 — generate data/predictions.json for all remaining matches.

For every unplayed fixture, runs the Elo→Poisson model (model.py), attaches an
evidence-cited reasoning paragraph (reasoning.py) and any players to watch, and writes
the result to data/predictions.json (schema in data/SCHEMA.md).

Usage:
    python predict.py                 # predict all remaining matches
    python predict.py --stage group   # limit to a stage
"""
from __future__ import annotations

import argparse
import datetime as dt

from common import (
    FIXTURES_FILE, RESULTS_FILE, PREDICTIONS_FILE, TEAMS_FILE, PLAYERS_FILE,
    MODEL_VERSION, load_json, save_json,
)
from model import predict_match
from reasoning import build_reasoning


_ROLE_ORDER = {"attack": 0, "midfield": 1, "defence": 2}


def _players_to_watch(players_by_team: dict, *team_ids: str) -> list[dict]:
    """Flagged difference-makers from each side, ordered attack → midfield → defence."""
    out = []
    for tid in team_ids:
        key = [p for p in players_by_team.get(tid, []) if p.get("key")]
        key.sort(key=lambda p: (_ROLE_ORDER.get(p.get("key_role"), 1),
                                -(p.get("intl_goals") or 0)))
        for p in key:
            out.append({
                "player_id": p["id"],
                "name": p["name"],
                "team": tid,
                "position": p.get("position"),
                "role": p.get("key_role"),
                "evidence": p.get("evidence") or "Key player.",
            })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict remaining WC 2026 matches")
    parser.add_argument("--stage", help="Limit to a stage (group, r32, r16, qf, sf, final)")
    args = parser.parse_args()

    teams = {t["id"]: t for t in load_json(TEAMS_FILE)}
    fixtures = load_json(FIXTURES_FILE)
    results = load_json(RESULTS_FILE)
    players = load_json(PLAYERS_FILE)

    players_by_team: dict[str, list] = {}
    for p in players:
        players_by_team.setdefault(p["team"], []).append(p)

    played = {r["id"] for r in results}
    remaining = [f for f in fixtures if f["id"] not in played]
    if args.stage:
        remaining = [f for f in remaining if f.get("stage") == args.stage]

    now = dt.datetime.now(dt.timezone.utc).isoformat()
    predictions = []
    for fx in remaining:
        home, away = teams.get(fx["home"]), teams.get(fx["away"])
        if not home or not away or home["elo"] is None or away["elo"] is None:
            continue  # knockout TBD slots or missing Elo
        pred = predict_match(home["elo"], away["elo"], home["id"], away["id"])
        predictions.append({
            "id": fx["id"],
            "generated_at": now,
            "model_version": MODEL_VERSION,
            "stage": fx["stage"],
            "group": fx.get("group"),
            "home": home["id"],
            "away": away["id"],
            "probabilities": {
                "home_win": pred.p_home, "draw": pred.p_draw, "away_win": pred.p_away,
            },
            "predicted_scoreline": {"home": pred.scoreline[0], "away": pred.scoreline[1]},
            "expected_goals": {"home": pred.lambda_home, "away": pred.lambda_away},
            "confidence": pred.confidence,
            "reasoning": build_reasoning(pred, home, away),
            "players_to_watch": _players_to_watch(players_by_team, home["id"], away["id"]),
            "evidence_refs": [f"teams.json:{home['id']}", f"teams.json:{away['id']}"],
        })

    save_json(PREDICTIONS_FILE, predictions)
    print(f"[predict] wrote {len(predictions)} predictions "
          f"({len(remaining)} remaining fixtures considered)")


if __name__ == "__main__":
    main()
