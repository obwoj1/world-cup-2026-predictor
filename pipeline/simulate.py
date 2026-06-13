"""Phase 3 — Monte Carlo full-tournament simulation.

Simulates the whole World Cup many times to produce, for every team, the probability of
advancing from the group, reaching each knockout round, and winning the title.

Each simulation:
  1. plays all 72 group matches by sampling scorelines from the Elo->Poisson model,
  2. ranks each group (points, goal difference, goals for; ties broken randomly),
  3. takes the 12 winners, 12 runners-up and the 8 best third-placed teams,
  4. allocates the eight thirds to their bracket slots respecting the official
     eligibility constraints (Annex C of the regulations) via constraint matching,
  5. plays the Round of 32 -> Final; knockout draws are resolved by the two sides'
     relative win probabilities (extra time / penalties),
  6. records how far every team got.

Aggregated over N runs these counts become probabilities.

Usage:
    python simulate.py --sims 20000
"""
from __future__ import annotations

import argparse
import datetime as dt
from collections import defaultdict

import numpy as np

from common import (
    TEAMS_FILE, FIXTURES_FILE, RESULTS_FILE, MODEL_VERSION, DATA_DIR, load_json, save_json,
)
from model import expected_goals

PROJECTIONS_FILE = DATA_DIR / "projections.json"

# Round-of-32 skeleton (Wikipedia / FIFA regulations). Each entry is a tie of two slots.
# Slot forms: ("W", "A")=winner grp A, ("R", "B")=runner-up grp B,
#             ("T", "ACEFH...") = best third from one of those groups.
R32 = [
    (("R", "A"), ("R", "B")),
    (("W", "C"), ("R", "F")),
    (("W", "E"), ("T", "ABCDF")),
    (("W", "F"), ("R", "C")),
    (("R", "E"), ("R", "I")),
    (("W", "I"), ("T", "CDFGH")),
    (("W", "A"), ("T", "CEFHI")),
    (("W", "L"), ("T", "EHIJK")),
    (("W", "G"), ("T", "AEHIJ")),
    (("W", "D"), ("T", "BEFIJ")),
    (("W", "H"), ("R", "J")),
    (("R", "K"), ("R", "L")),
    (("W", "B"), ("T", "EFGIJ")),
    (("R", "D"), ("R", "G")),
    (("W", "J"), ("R", "H")),
    (("W", "K"), ("T", "DEIJL")),
]
THIRD_SLOTS = [grp for tie in R32 for slot, grp in tie if slot == "T"]


def assign_thirds(qualified_groups: list[str], rng: np.random.Generator) -> dict[str, str]:
    """Match the 8 qualifying third-place groups to the 8 third slots respecting
    each slot's eligible-group set. Returns {slot_eligibility_string: group}."""
    slots = list(THIRD_SLOTS)
    rng.shuffle(slots)  # randomize to avoid a fixed bias when several matchings exist
    groups = list(qualified_groups)
    assignment: dict[str, str] = {}

    def backtrack(i: int, used: set[str]) -> bool:
        if i == len(slots):
            return True
        elig = slots[i]
        for g in groups:
            if g not in used and g in elig:
                assignment[elig] = g
                used.add(g)
                if backtrack(i + 1, used):
                    return True
                used.remove(g)
                del assignment[elig]
        return False

    if not backtrack(0, set()):
        # Extremely rare: no valid matching for this combination — fall back to any order.
        for elig, g in zip(slots, groups):
            assignment[elig] = g
    return assignment


def simulate_match_goals(elo_h, elo_a, id_h, id_a, rng) -> tuple[int, int]:
    lam_h, lam_a = expected_goals(elo_h, elo_a, id_h, id_a)
    return int(rng.poisson(lam_h)), int(rng.poisson(lam_a))


def knockout_winner(team_a, team_b, teams, rng) -> str:
    """Return the id of the side that advances (draws resolved by win-prob share)."""
    ea, eb = teams[team_a]["elo"], teams[team_b]["elo"]
    lam_a, lam_b = expected_goals(ea, eb, team_a, team_b)
    ga, gb = rng.poisson(lam_a), rng.poisson(lam_b)
    if ga > gb:
        return team_a
    if gb > ga:
        return team_b
    # extra time / penalties: split by relative attacking strength
    p_a = lam_a / (lam_a + lam_b)
    return team_a if rng.random() < p_a else team_b


def run(sims: int, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    teams = {t["id"]: t for t in load_json(TEAMS_FILE)}
    fixtures = [f for f in load_json(FIXTURES_FILE) if f["stage"] == "group"]
    # Actual results for matches already played are fixed, not re-simulated.
    played = {r["id"]: (r["home_goals"], r["away_goals"]) for r in load_json(RESULTS_FILE)}

    group_fixtures: dict[str, list] = defaultdict(list)
    for f in fixtures:
        group_fixtures[f["group"]].append(f)
    group_members: dict[str, list[str]] = {
        g: sorted({f["home"] for f in fs} | {f["away"] for f in fs}) for g, fs in group_fixtures.items()
    }

    rounds = ["group_advance", "r16", "qf", "sf", "final", "champion"]
    tally = {tid: {r: 0 for r in rounds} for tid in teams}

    for _ in range(sims):
        # ---- group stage ----
        standings = {g: {tid: {"pts": 0, "gd": 0, "gf": 0} for tid in members}
                     for g, members in group_members.items()}
        for g, fs in group_fixtures.items():
            for fx in fs:
                h, a = fx["home"], fx["away"]
                if fx["id"] in played:
                    gh, ga = played[fx["id"]]  # actual result, fixed
                else:
                    gh, ga = simulate_match_goals(teams[h]["elo"], teams[a]["elo"], h, a, rng)
                standings[g][h]["gf"] += gh
                standings[g][a]["gf"] += ga
                standings[g][h]["gd"] += gh - ga
                standings[g][a]["gd"] += ga - gh
                if gh > ga:
                    standings[g][h]["pts"] += 3
                elif ga > gh:
                    standings[g][a]["pts"] += 3
                else:
                    standings[g][h]["pts"] += 1
                    standings[g][a]["pts"] += 1

        winners, runners, thirds = {}, {}, []
        for g, table in standings.items():
            ranked = sorted(
                table.items(),
                key=lambda kv: (kv[1]["pts"], kv[1]["gd"], kv[1]["gf"], rng.random()),
                reverse=True,
            )
            winners[g] = ranked[0][0]
            runners[g] = ranked[1][0]
            third_tid = ranked[2][0]
            thirds.append((g, third_tid, ranked[2][1]))
            for tid, _slot in ((ranked[0][0], 1), (ranked[1][0], 2)):
                tally[tid]["group_advance"] += 1

        # best 8 third-placed teams
        thirds.sort(key=lambda x: (x[2]["pts"], x[2]["gd"], x[2]["gf"], rng.random()), reverse=True)
        best_thirds = thirds[:8]
        for _g, tid, _s in best_thirds:
            tally[tid]["group_advance"] += 1
        third_by_group = {g: tid for g, tid, _ in best_thirds}
        slot_to_group = assign_thirds([g for g, _, _ in best_thirds], rng)

        # ---- build Round of 32 ----
        def resolve(slot) -> str:
            kind, key = slot
            if kind == "W":
                return winners[key]
            if kind == "R":
                return runners[key]
            return third_by_group[slot_to_group[key]]  # "T"

        bracket = [(resolve(a), resolve(b)) for a, b in R32]

        # ---- knockout rounds ----
        # Each round plays the current ties and the winners advance. Naming reflects the
        # round the winners REACH: R32 winners reach R16, ..., final winners are champion.
        for round_name in ["r16", "qf", "sf", "final", "champion"]:
            next_round = []
            for a, b in bracket:
                w = knockout_winner(a, b, teams, rng)
                tally[w][round_name] += 1
                next_round.append(w)
            # pair winners for the next round; empty once a single champion remains
            bracket = [(next_round[i], next_round[i + 1]) for i in range(0, len(next_round) - 1, 2)]

    # ---- aggregate ----
    projections = []
    for tid, t in teams.items():
        c = tally[tid]
        projections.append({
            "id": tid, "name": t["name"], "group": t["group"], "elo": t["elo"],
            "p_advance_group": round(c["group_advance"] / sims, 4),
            "p_reach_r16": round(c["r16"] / sims, 4),
            "p_reach_qf": round(c["qf"] / sims, 4),
            "p_reach_sf": round(c["sf"] / sims, 4),
            "p_reach_final": round(c["final"] / sims, 4),
            "p_champion": round(c["champion"] / sims, 4),
        })
    projections.sort(key=lambda x: -x["p_champion"])
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model_version": MODEL_VERSION,
        "sims": sims,
        "method": "Monte Carlo over Elo->Poisson group + knockout simulation",
        "teams": projections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Monte Carlo WC 2026 tournament simulation")
    parser.add_argument("--sims", type=int, default=20000, help="Number of simulations")
    args = parser.parse_args()
    out = run(args.sims)
    save_json(PROJECTIONS_FILE, out)
    print(f"[simulate] {args.sims} sims -> {PROJECTIONS_FILE.name}")
    print("[simulate] Top 8 title odds:")
    for t in out["teams"][:8]:
        print(f"   {t['name']:<22} champion {t['p_champion']:.1%}  "
              f"final {t['p_reach_final']:.1%}  advance {t['p_advance_group']:.1%}")


if __name__ == "__main__":
    main()
