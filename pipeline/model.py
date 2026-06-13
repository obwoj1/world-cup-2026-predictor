"""Phase 3 — the prediction model (Elo → expected goals → Poisson scoreline).

Method (documented for traceability):

1. Effective rating difference
       dr = elo_home - elo_away + host_adj
   `host_adj` applies a home-advantage bump worth HOST_ADV Elo points to one of the
   three host nations (USA, Mexico, Canada) whenever it features in a match. All other
   group matches are treated as neutral (the World Cup is played at neutral venues for
   non-hosts).

2. Expected goal supremacy
       sup = dr / ELO_PER_GOAL
   Empirically ~250 Elo points ≈ one goal of supremacy at international level.

3. Expected goals per side, around a baseline total typical of World Cups (~2.6):
       lambda_home = clamp(BASE_TOTAL/2 + sup/2)
       lambda_away = clamp(BASE_TOTAL/2 - sup/2)

4. Independent Poisson over a score grid gives the full scoreline distribution, from
   which we read win/draw/loss probabilities and the single most likely scoreline.

This is a transparent baseline. Recent form, xG and player availability are layered on
in later passes and recalibrated against actual results during reconciliation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

HOSTS = {"USA", "MEX", "CAN"}

HOST_ADV = 65.0       # Elo-point home-advantage bump for a host nation
ELO_PER_GOAL = 250.0  # Elo points equivalent to one goal of supremacy
BASE_TOTAL = 2.6      # baseline combined expected goals
MIN_LAMBDA = 0.20     # floor so no side has ~zero expected goals
MAX_LAMBDA = 4.0      # ceiling to keep blowouts sane
MAX_GOALS = 10        # score-grid size for the Poisson convolution


@dataclass
class MatchPrediction:
    home: str
    away: str
    lambda_home: float
    lambda_away: float
    p_home: float
    p_draw: float
    p_away: float
    scoreline: tuple[int, int]
    confidence: str


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def host_adjustment(home: str, away: str) -> float:
    """Elo bump added to dr (home - away). Positive favours the home slot."""
    adj = 0.0
    if home in HOSTS:
        adj += HOST_ADV
    if away in HOSTS:
        adj -= HOST_ADV
    return adj


def expected_goals(elo_home: float, elo_away: float, home: str, away: str) -> tuple[float, float]:
    dr = (elo_home - elo_away) + host_adjustment(home, away)
    sup = dr / ELO_PER_GOAL
    lam_h = _clamp(BASE_TOTAL / 2 + sup / 2, MIN_LAMBDA, MAX_LAMBDA)
    lam_a = _clamp(BASE_TOTAL / 2 - sup / 2, MIN_LAMBDA, MAX_LAMBDA)
    return lam_h, lam_a


def _poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def score_matrix(lam_h: float, lam_a: float, max_goals: int = MAX_GOALS) -> list[list[float]]:
    home_p = [_poisson_pmf(i, lam_h) for i in range(max_goals + 1)]
    away_p = [_poisson_pmf(j, lam_a) for j in range(max_goals + 1)]
    return [[home_p[i] * away_p[j] for j in range(max_goals + 1)] for i in range(max_goals + 1)]


def outcome_probs(matrix: list[list[float]]) -> tuple[float, float, float]:
    p_home = p_draw = p_away = 0.0
    for i, row in enumerate(matrix):
        for j, p in enumerate(row):
            if i > j:
                p_home += p
            elif i == j:
                p_draw += p
            else:
                p_away += p
    total = p_home + p_draw + p_away
    return p_home / total, p_draw / total, p_away / total


def most_likely_scoreline(matrix: list[list[float]]) -> tuple[int, int]:
    best, best_p = (0, 0), -1.0
    for i, row in enumerate(matrix):
        for j, p in enumerate(row):
            if p > best_p:
                best_p, best = p, (i, j)
    return best


def _confidence(p_home: float, p_draw: float, p_away: float) -> str:
    top = max(p_home, p_draw, p_away)
    if top >= 0.60:
        return "high"
    if top >= 0.45:
        return "medium"
    return "low"


def predict_match(elo_home: float, elo_away: float, home: str, away: str) -> MatchPrediction:
    lam_h, lam_a = expected_goals(elo_home, elo_away, home, away)
    matrix = score_matrix(lam_h, lam_a)
    p_home, p_draw, p_away = outcome_probs(matrix)
    scoreline = most_likely_scoreline(matrix)
    return MatchPrediction(
        home=home, away=away,
        lambda_home=round(lam_h, 3), lambda_away=round(lam_a, 3),
        p_home=round(p_home, 4), p_draw=round(p_draw, 4), p_away=round(p_away, 4),
        scoreline=scoreline,
        confidence=_confidence(p_home, p_draw, p_away),
    )
