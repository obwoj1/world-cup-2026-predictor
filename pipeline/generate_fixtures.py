"""Phase 2 — generate data/fixtures.json (group-stage round-robin).

Builds the 72 group-stage fixtures (12 groups x 6 matches) from the draw in
teams.json using a standard 4-team round-robin. Date/venue are left null here and
enriched by a later fetch step; the prediction engine only needs the pairings.

Knockout fixtures (round of 32 onward) are produced later by the prediction engine
once group projections exist, since their participants are TBD.

Usage:
    python generate_fixtures.py
"""
from __future__ import annotations

from collections import defaultdict

from common import TEAMS_FILE, FIXTURES_FILE, load_json, save_json

# Round-robin schedule for 4 teams (indices into the group list), one pairing per
# matchday. Each team plays the other three exactly once.
ROUND_ROBIN = [
    [(0, 3), (1, 2)],  # matchday 1
    [(0, 2), (3, 1)],  # matchday 2
    [(0, 1), (2, 3)],  # matchday 3
]


def main() -> None:
    teams = load_json(TEAMS_FILE)
    if not teams:
        raise SystemExit("teams.json is empty — run build_ratings.py first.")

    by_group: dict[str, list] = defaultdict(list)
    for t in teams:
        by_group[t["group"]].append(t)

    fixtures = []
    counter = 1
    for group in sorted(by_group):
        members = by_group[group]
        if len(members) != 4:
            raise SystemExit(f"Group {group} has {len(members)} teams, expected 4.")
        # Stable order: by Elo descending so seedings are deterministic.
        members.sort(key=lambda t: -(t["elo"] or 0))
        for matchday, pairings in enumerate(ROUND_ROBIN, start=1):
            for home_idx, away_idx in pairings:
                fixtures.append({
                    "id": f"M{counter:03d}",
                    "matchweek": matchday,
                    "stage": "group",
                    "group": group,
                    "matchday": matchday,
                    "date": None,
                    "venue": None,
                    "home": members[home_idx]["id"],
                    "away": members[away_idx]["id"],
                })
                counter += 1

    save_json(FIXTURES_FILE, fixtures)
    print(f"[generate_fixtures] wrote {len(fixtures)} group-stage fixtures "
          f"to {FIXTURES_FILE.name}")


if __name__ == "__main__":
    main()
