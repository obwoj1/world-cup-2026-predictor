"""Phase 2 — build data/fixtures.json and data/results.json from the real schedule.

Parses the official match schedule (fixturedownload.com feed saved in data/sources/) into:
  * fixtures.json — all 104 matches with real dates, venues and pairings; knockout slots
    (e.g. "1A", "3ABCDF") are kept as placeholders until participants are known,
  * results.json — actual scores for matches already played.

Usage:
    python generate_fixtures.py
"""
from __future__ import annotations

import glob
import json
import datetime as dt
from pathlib import Path

from common import FIXTURES_FILE, RESULTS_FILE, SOURCES_DIR, save_json

# fixturedownload feed names -> our FIFA codes (used in teams.json / predictions).
FEED_NAME_TO_CODE = {
    "Mexico": "MEX", "South Africa": "RSA", "Korea Republic": "KOR", "Czechia": "CZE",
    "Canada": "CAN", "Bosnia and Herzegovina": "BIH", "Qatar": "QAT", "Switzerland": "SUI",
    "Brazil": "BRA", "Morocco": "MAR", "Haiti": "HAI", "Scotland": "SCO",
    "USA": "USA", "Paraguay": "PAR", "Australia": "AUS", "Türkiye": "TUR",
    "Germany": "GER", "Curaçao": "CUW", "Côte d'Ivoire": "CIV", "Ecuador": "ECU",
    "Netherlands": "NED", "Japan": "JPN", "Sweden": "SWE", "Tunisia": "TUN",
    "Belgium": "BEL", "Egypt": "EGY", "IR Iran": "IRN", "New Zealand": "NZL",
    "Spain": "ESP", "Cabo Verde": "CPV", "Saudi Arabia": "KSA", "Uruguay": "URU",
    "France": "FRA", "Senegal": "SEN", "Iraq": "IRQ", "Norway": "NOR",
    "Argentina": "ARG", "Algeria": "ALG", "Austria": "AUT", "Jordan": "JOR",
    "Portugal": "POR", "Congo DR": "COD", "Uzbekistan": "UZB", "Colombia": "COL",
    "England": "ENG", "Croatia": "CRO", "Ghana": "GHA", "Panama": "PAN",
}

# Round number in the feed -> our stage label.
ROUND_TO_STAGE = {1: "group", 2: "group", 3: "group", 4: "r32", 5: "r16", 6: "qf", 7: "sf"}


def _latest_feed() -> Path:
    matches = sorted(glob.glob(str(SOURCES_DIR / "fixtures_fixturedownload_*.json")))
    if not matches:
        raise FileNotFoundError(
            "No fixtures_fixturedownload_*.json in data/sources/. Download the schedule first."
        )
    return Path(matches[-1])


def _team_ref(name: str) -> tuple[str | None, str | None]:
    """Return (fifa_code, None) for a real team, or (None, slot) for a knockout slot."""
    if name in FEED_NAME_TO_CODE:
        return FEED_NAME_TO_CODE[name], None
    if name == "To be announced":
        return None, "TBD"
    return None, name  # e.g. "1A", "3ABCDF", "2K"


def main() -> None:
    feed = json.loads(_latest_feed().read_text())
    fixtures, results = [], []

    for m in sorted(feed, key=lambda x: x["MatchNumber"]):
        num = m["MatchNumber"]
        rnd = m["RoundNumber"]
        stage = ROUND_TO_STAGE.get(rnd)
        if stage is None:  # round 8: 103 = third place, 104 = final
            stage = "third_place" if num == 103 else "final"

        when = dt.datetime.fromisoformat(m["DateUtc"].replace("Z", "+00:00"))
        home_code, home_slot = _team_ref(m["HomeTeam"])
        away_code, away_slot = _team_ref(m["AwayTeam"])
        group = (m.get("Group") or "").replace("Group ", "") or None

        fixtures.append({
            "id": f"M{num:03d}",
            "matchweek": rnd if stage == "group" else None,
            "matchday": rnd if stage == "group" else None,
            "stage": stage,
            "group": group,
            "date": when.date().isoformat(),
            "datetime_utc": when.isoformat(),
            "venue": m.get("Location"),
            "home": home_code,
            "away": away_code,
            "home_slot": home_slot,
            "away_slot": away_slot,
        })

        if m["HomeTeamScore"] is not None and m["AwayTeamScore"] is not None:
            results.append({
                "id": f"M{num:03d}",
                "home_goals": int(m["HomeTeamScore"]),
                "away_goals": int(m["AwayTeamScore"]),
                "status": "final",
            })

    save_json(FIXTURES_FILE, fixtures)
    save_json(RESULTS_FILE, results)
    groups = sum(1 for f in fixtures if f["stage"] == "group")
    print(f"[generate_fixtures] wrote {len(fixtures)} fixtures ({groups} group) "
          f"and {len(results)} played results from the real schedule")


if __name__ == "__main__":
    main()
