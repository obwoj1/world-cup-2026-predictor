"""Phase 3 — build evidence-cited reasoning text for a match prediction.

Every clause references a concrete number that exists in teams.json (Elo, rank) or the
model output (probabilities, host advantage), so the prose is always traceable. As form
and player data are added, more clauses are appended here.
"""
from __future__ import annotations

from model import MatchPrediction, HOSTS, HOST_ADV


def _fav_label(p: float) -> str:
    if p >= 0.60:
        return "clear favourites"
    if p >= 0.45:
        return "favourites"
    return "narrow favourites"


def build_reasoning(pred: MatchPrediction, home_team: dict, away_team: dict) -> str:
    elo_h, elo_a = home_team["elo"], away_team["elo"]
    gap = abs(elo_h - elo_a)
    home_favoured = pred.p_home >= pred.p_away
    fav, und = (home_team, away_team) if home_favoured else (away_team, home_team)
    fav_p = pred.p_home if home_favoured else pred.p_away

    sentences: list[str] = []

    # 1. Elo framing
    sentences.append(
        f"{fav['name']} (Elo {fav['elo']}, world #{fav['elo_rank']}) are {_fav_label(fav_p)} "
        f"over {und['name']} (Elo {und['elo']}, #{und['elo_rank']}), an Elo gap of {gap}."
    )

    # 2. Host advantage, if relevant
    if home_team["id"] in HOSTS or away_team["id"] in HOSTS:
        host = home_team if home_team["id"] in HOSTS else away_team
        sentences.append(
            f"As a tournament host, {host['name']} get a home-advantage bump worth "
            f"~{int(HOST_ADV)} Elo points in this projection."
        )

    # 3. Probability split + scoreline
    sentences.append(
        f"The model gives {home_team['name']} {pred.p_home:.0%} / draw {pred.p_draw:.0%} / "
        f"{away_team['name']} {pred.p_away:.0%}, with a most-likely scoreline of "
        f"{pred.scoreline[0]}-{pred.scoreline[1]}."
    )

    # 4. Confidence framing
    if pred.confidence == "low":
        sentences.append("Ratings are close, so this is flagged low confidence — a genuine toss-up.")
    elif pred.confidence == "high":
        sentences.append("The rating gap is large enough to call this high confidence.")
    else:
        sentences.append("A clear but not overwhelming edge — medium confidence.")

    return " ".join(sentences)
