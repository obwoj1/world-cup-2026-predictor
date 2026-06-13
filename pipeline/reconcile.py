"""Phase 5 — post-matchweek reconciliation.

Grades the predictions that were standing before a matchweek against the actual results,
updates each team's Elo (and a lightweight form record) from those results, re-runs the
per-match predictions and the Monte Carlo simulation for everything still to play, and
writes a "what changed and why" log to reconciliations/matchweek-NN.md.

Workflow:
    1. populate data/results.json with the matchweek's actual scores, then
    2. python reconcile.py --matchweek 1
       add --commit to also git-commit the result, --dry-run to preview without writing.

Results schema (data/results.json): [{"id":"M001","home_goals":2,"away_goals":1,"status":"final"}]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from common import (
    TEAMS_FILE, FIXTURES_FILE, RESULTS_FILE, PREDICTIONS_FILE, DATA_DIR,
    RECONCILIATIONS_DIR, PIPELINE_DIR, load_json, save_json,
)
from elo import elo_delta
from scoring import grade, summarize, GradedMatch

SNAPSHOT_DIR = DATA_DIR / "snapshots"
PROJECTIONS_FILE = DATA_DIR / "projections.json"


def _matchweek_results(mw: int):
    fixtures = {f["id"]: f for f in load_json(FIXTURES_FILE)}
    results = load_json(RESULTS_FILE)
    rows = []
    for r in results:
        fx = fixtures.get(r["id"])
        if fx and (fx.get("matchday") or fx.get("matchweek")) == mw:
            rows.append((r, fx))
    return rows


def _apply_elo_and_form(graded: list[GradedMatch]):
    """Update teams.json Elo (computed from pre-week ratings) and append form."""
    teams = {t["id"]: t for t in load_json(TEAMS_FILE)}
    team_list = load_json(TEAMS_FILE)

    deltas: dict[str, float] = {tid: 0.0 for tid in teams}
    for g in graded:
        h, a = teams[g.home], teams[g.away]
        if h["elo"] is None or a["elo"] is None:
            continue
        gh, ga = g.actual_score
        deltas[g.home] += elo_delta(h["elo"], a["elo"], gh, ga)
        deltas[g.away] += elo_delta(a["elo"], h["elo"], ga, gh)

    for t in team_list:
        d = deltas.get(t["id"], 0.0)
        if t["elo"] is not None and d:
            t["elo"] = round(t["elo"] + d)
    # rebuild Elo ranks within this dataset (display only; global rank stays from source)
    save_json(TEAMS_FILE, team_list)

    # append a lightweight form line per team
    teams = {t["id"]: t for t in team_list}
    for g in graded:
        gh, ga = g.actual_score
        for tid, gf, gaa, opp in ((g.home, gh, ga, g.away), (g.away, ga, gh, g.home)):
            t = teams[tid]
            res = "W" if gf > gaa else "L" if gf < gaa else "D"
            form = t.get("form") or {"recent": []}
            if not isinstance(form, dict):
                form = {"recent": []}
            form.setdefault("recent", []).insert(0, f"{res} {gf}-{gaa} vs {opp}")
            form["recent"] = form["recent"][:15]
            t["form"] = form
    save_json(TEAMS_FILE, list(teams.values()))
    return deltas


def _run(script: str, *args: str):
    subprocess.run([sys.executable, str(PIPELINE_DIR / script), *args], check=True)


def _title_odds(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {t["id"]: t["p_champion"] for t in data.get("teams", [])}


def _write_log(mw: int, graded: list[GradedMatch], summary: dict, deltas: dict,
               teams: dict, odds_before: dict, odds_after: dict) -> Path:
    RECONCILIATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out = RECONCILIATIONS_DIR / f"matchweek-{mw:02d}.md"
    today = dt.date.today().isoformat()
    L: list[str] = [f"# Matchweek {mw} Reconciliation — {today}", ""]

    # Scoreboard
    L += ["## Scoreboard", "",
          "| Match | Predicted | Actual | Outcome ✓ | Exact ✓ |",
          "|-------|-----------|--------|-----------|---------|"]
    for g in graded:
        L.append(
            f"| {g.home} v {g.away} | {g.pred_score[0]}-{g.pred_score[1]} "
            f"({g.pred_outcome}) | {g.actual_score[0]}-{g.actual_score[1]} "
            f"({g.actual}) | {'✓' if g.outcome_hit else '✗'} | "
            f"{'✓' if g.exact_hit else '·'} |"
        )

    # Accuracy
    L += ["", "## Accuracy", "",
          f"- Outcome accuracy: **{summary['outcome_accuracy']:.0%}** "
          f"({sum(g.outcome_hit for g in graded)}/{summary['n']})",
          f"- Mean Brier score: **{summary['mean_brier']}** (0 = perfect, lower is better)",
          f"- Exact scorelines: {summary['exact_scorelines']}/{summary['n']}"]

    # Upsets
    L += ["", "## Upsets & surprises", ""]
    if summary["upsets"]:
        for g in summary["upsets"]:
            eh = teams[g.home]["name"]
            ea = teams[g.away]["name"]
            L.append(
                f"- **{eh} {g.actual_score[0]}-{g.actual_score[1]} {ea}** — the model gave "
                f"the actual result only {g.prob_of_actual:.0%}. It expected a "
                f"{g.pred_outcome} win; the {g.actual} result is the surprise."
            )
    else:
        L.append("- None — every result fell within the model's expected range.")

    # Rating updates
    moved = sorted(
        [(tid, d) for tid, d in deltas.items() if abs(d) >= 1],
        key=lambda kv: -abs(kv[1]),
    )
    L += ["", "## Rating & form updates", ""]
    if moved:
        for tid, d in moved:
            L.append(f"- {teams[tid]['name']}: {'+' if d >= 0 else ''}{round(d)} Elo "
                     f"→ {teams[tid]['elo']}")
    else:
        L.append("- No rating changes (no results applied).")

    # Downstream changes
    L += ["", "## What changed for remaining matches", ""]
    if odds_before and odds_after:
        swings = sorted(
            ((tid, odds_after.get(tid, 0) - odds_before.get(tid, 0)) for tid in odds_after),
            key=lambda kv: -abs(kv[1]),
        )[:5]
        for tid, sw in swings:
            if abs(sw) < 0.001:
                continue
            L.append(f"- {teams[tid]['name']} title odds {odds_before.get(tid,0):.1%} → "
                     f"{odds_after.get(tid,0):.1%} ({'+' if sw>=0 else ''}{sw*100:.1f} pts)")
    else:
        L.append("- Predictions and tournament odds re-run for all remaining matches.")

    L += ["", "---", "_Probabilistic forecast, not betting advice. "
          "Predictions re-run after this matchweek._", ""]
    out.write_text("\n".join(L))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile predictions vs actual results")
    parser.add_argument("--matchweek", type=int, required=True)
    parser.add_argument("--sims", type=int, default=20000)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing data")
    parser.add_argument("--commit", action="store_true", help="git commit the reconciliation")
    args = parser.parse_args()

    rows = _matchweek_results(args.matchweek)
    if not rows:
        raise SystemExit(
            f"No results found for matchweek {args.matchweek}. "
            f"Add them to {RESULTS_FILE.name} first."
        )

    preds = {p["id"]: p for p in load_json(PREDICTIONS_FILE)}
    graded: list[GradedMatch] = []
    for r, _fx in rows:
        pred = preds.get(r["id"])
        if pred:
            graded.append(grade(pred, r["home_goals"], r["away_goals"]))

    summary = summarize(graded)
    teams_before = {t["id"]: t for t in load_json(TEAMS_FILE)}
    print(f"[reconcile] matchweek {args.matchweek}: graded {summary['n']} matches | "
          f"accuracy {summary['outcome_accuracy']:.0%} | Brier {summary['mean_brier']} | "
          f"{len(summary['upsets'])} upset(s)")

    if args.dry_run:
        for g in graded:
            tag = " UPSET" if g.is_upset else ""
            print(f"   {g.home} {g.actual_score[0]}-{g.actual_score[1]} {g.away}: "
                  f"pred {g.pred_outcome}/actual {g.actual} "
                  f"{'✓' if g.outcome_hit else '✗'} brier {g.brier}{tag}")
        print("[reconcile] dry run — no data written.")
        return

    # snapshot the graded (pre-update) predictions for traceability
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    save_json(SNAPSHOT_DIR / f"predictions_pre_mw{args.matchweek:02d}.json",
              [preds[g.id] for g in graded])

    odds_before = _title_odds(PROJECTIONS_FILE)
    deltas = _apply_elo_and_form(graded)

    # re-run predictions + simulation for everything still to play
    _run("predict.py")
    _run("simulate.py", "--sims", str(args.sims))
    odds_after = _title_odds(PROJECTIONS_FILE)

    teams_after = {t["id"]: t for t in load_json(TEAMS_FILE)}
    out = _write_log(args.matchweek, graded, summary, deltas, teams_after,
                     odds_before, odds_after)
    print(f"[reconcile] wrote {out.relative_to(out.parents[1])}")

    if args.commit:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", f"Matchweek {args.matchweek} reconciliation"],
                       check=True)
        print("[reconcile] committed.")


if __name__ == "__main__":
    main()
