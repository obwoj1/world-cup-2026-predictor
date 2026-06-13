"""Elo rating updates from match results (World Football Elo method).

After a result, each team's rating moves by

    delta = K * G * (W - We)

where
  * W  = actual result for the team (1 win, 0.5 draw, 0 loss),
  * We = expected result = 1 / (1 + 10**(-(elo - elo_opp)/400)),
  * K  = importance weight (60 for World Cup finals, per eloratings.net),
  * G  = goal-difference multiplier (1 for a one-goal margin, 1.5 for two,
         (11+GD)/8 for three or more).

Ratings are updated at neutral venue (no home-advantage term) — consistent with how
eloratings.net treats World Cup matches. The host bump lives only in the prediction
model, not in the rating itself.
"""
from __future__ import annotations

K_WORLD_CUP = 60.0


def expected_score(elo: float, elo_opp: float) -> float:
    return 1.0 / (1.0 + 10 ** (-(elo - elo_opp) / 400.0))


def _gd_multiplier(gd: int) -> float:
    gd = abs(gd)
    if gd <= 1:
        return 1.0
    if gd == 2:
        return 1.5
    return (11 + gd) / 8.0


def result_score(goals_for: int, goals_against: int) -> float:
    if goals_for > goals_against:
        return 1.0
    if goals_for < goals_against:
        return 0.0
    return 0.5


def elo_delta(elo: float, elo_opp: float, goals_for: int, goals_against: int,
              k: float = K_WORLD_CUP) -> float:
    """Rating change for the team with `elo` after this result."""
    we = expected_score(elo, elo_opp)
    w = result_score(goals_for, goals_against)
    g = _gd_multiplier(goals_for - goals_against)
    return k * g * (w - we)
