"""Phase 2 — build data/players.json from the Wikipedia squads wikitext.

Parses the raw "2026 FIFA World Cup squads" wikitext (saved in data/sources/) into the
full 26-man roster for every team, capturing position, club, caps and international
goals per player. It then flags a handful of "key players" per team — difference-makers
across attack, midfield and defence — used by the per-match "players to watch" picks.

Usage:
    python build_players.py
"""
from __future__ import annotations

import glob
import re
from pathlib import Path

from common import PLAYERS_FILE, SOURCES_DIR, save_json

# Wikipedia heading -> our FIFA code.
WIKI_NAME_TO_CODE = {
    "Mexico": "MEX", "South Africa": "RSA", "South Korea": "KOR", "Czech Republic": "CZE",
    "Canada": "CAN", "Bosnia and Herzegovina": "BIH", "Qatar": "QAT", "Switzerland": "SUI",
    "Brazil": "BRA", "Morocco": "MAR", "Haiti": "HAI", "Scotland": "SCO",
    "United States": "USA", "Paraguay": "PAR", "Australia": "AUS", "Turkey": "TUR",
    "Germany": "GER", "Curaçao": "CUW", "Ivory Coast": "CIV", "Ecuador": "ECU",
    "Netherlands": "NED", "Japan": "JPN", "Sweden": "SWE", "Tunisia": "TUN",
    "Belgium": "BEL", "Egypt": "EGY", "Iran": "IRN", "New Zealand": "NZL",
    "Spain": "ESP", "Cape Verde": "CPV", "Saudi Arabia": "KSA", "Uruguay": "URU",
    "France": "FRA", "Senegal": "SEN", "Iraq": "IRQ", "Norway": "NOR",
    "Argentina": "ARG", "Algeria": "ALG", "Austria": "AUT", "Jordan": "JOR",
    "Portugal": "POR", "DR Congo": "COD", "Uzbekistan": "UZB", "Colombia": "COL",
    "England": "ENG", "Croatia": "CRO", "Ghana": "GHA", "Panama": "PAN",
}

POS_GROUP = {"GK": "defence", "DF": "defence", "MF": "midfield", "FW": "attack"}


def _latest_raw() -> Path:
    matches = sorted(glob.glob(str(SOURCES_DIR / "wiki_squads_raw_*.txt")))
    if not matches:
        raise FileNotFoundError("No wiki_squads_raw_*.txt in data/sources/.")
    return Path(matches[-1])


def _field(s: str, key: str) -> str | None:
    # Capture a full [[wiki|link]] (may contain a pipe) or a plain value up to the next |.
    m = re.search(rf"\|{key}=(\[\[[^\]]*\]\]|[^|}}]*)", s)
    return m.group(1).strip() if m else None


def _clean_link(s: str | None) -> str | None:
    if not s:
        return s
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)  # [[A|B]] -> B, [[A]] -> A
    return s.strip()


def _slug(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return base


def parse(raw: str) -> list[dict]:
    players: list[dict] = []
    current_team: str | None = None
    src = f"sources/{_latest_raw().name}"

    for line in raw.splitlines():
        h = re.match(r"^===\s*([^=]+?)\s*===", line)
        if h:
            current_team = WIKI_NAME_TO_CODE.get(h.group(1).strip())
            continue
        if current_team and "nat fs g player" in line:
            name = _clean_link(_field(line, "name"))
            if not name:
                continue
            pos = _field(line, "pos") or ""
            caps = _field(line, "caps")
            goals = _field(line, "goals")
            club = _clean_link(_field(line, "club"))
            players.append({
                "id": f"{current_team.lower()}-{_slug(name)}",
                "name": name,
                "team": current_team,
                "position": pos,
                "pos_group": POS_GROUP.get(pos, "midfield"),
                "club": club,
                "caps": int(caps) if caps and caps.isdigit() else None,
                "intl_goals": int(goals) if goals and goals.isdigit() else None,
                "key": False,
                "key_role": None,
                "evidence": None,
                "sources": [src],
            })
    return players


def _evidence(p: dict, role: str) -> str:
    caps = p["caps"]
    goals = p["intl_goals"]
    club = p["club"] or "his club"
    label = {"attack": "Attacking threat", "midfield": "Midfield engine",
             "defence": "Defensive anchor"}[role]

    if role == "defence":
        # lead with experience; mention goals only if notable
        rec = f"{caps} caps" if caps is not None else "an experienced international"
        if goals:
            rec += f" and {goals} goals"
    else:
        bits = []
        if goals is not None:
            bits.append(f"{goals} goals")
        if caps is not None:
            bits.append(f"in {caps} caps")
        rec = " ".join(bits) if bits else "an established international"
    return f"{label} — {rec} for the national team; plays his club football at {club}."


def flag_key_players(players: list[dict]) -> None:
    """Per team, flag difference-makers: top scorer (attack), a midfield leader,
    a defensive leader, plus the next-best scorer as an extra threat."""
    by_team: dict[str, list[dict]] = {}
    for p in players:
        by_team.setdefault(p["team"], []).append(p)

    for team, squad in by_team.items():
        def top(group: str, by: str):
            cands = [p for p in squad if p["pos_group"] == group and p.get(by) is not None]
            return max(cands, key=lambda p: p[by]) if cands else None

        chosen: dict[str, str] = {}  # player id -> role
        # attack: most international goals among forwards (fallback midfield scorer)
        atk = top("attack", "intl_goals") or top("midfield", "intl_goals")
        if atk:
            chosen[atk["id"]] = "attack"
        # midfield: most caps among midfielders
        mid = top("midfield", "caps")
        if mid and mid["id"] not in chosen:
            chosen[mid["id"]] = "midfield"
        # defence: most caps among defenders/keepers
        dfn = top("defence", "caps")
        if dfn and dfn["id"] not in chosen:
            chosen[dfn["id"]] = "defence"
        # extra difference-maker: next-highest scorer overall not already chosen
        scorers = sorted(
            [p for p in squad if p.get("intl_goals") is not None and p["id"] not in chosen],
            key=lambda p: p["intl_goals"], reverse=True,
        )
        if scorers:
            chosen[scorers[0]["id"]] = scorers[0]["pos_group"]

        for p in squad:
            if p["id"] in chosen:
                role = chosen[p["id"]]
                p["key"] = True
                p["key_role"] = role
                p["evidence"] = _evidence(p, role)


def main() -> None:
    raw = _latest_raw().read_text()
    players = parse(raw)
    flag_key_players(players)
    save_json(PLAYERS_FILE, players)
    teams = len({p["team"] for p in players})
    keys = sum(1 for p in players if p["key"])
    print(f"[build_players] wrote {len(players)} players across {teams} teams "
          f"({keys} flagged as key)")


if __name__ == "__main__":
    main()
