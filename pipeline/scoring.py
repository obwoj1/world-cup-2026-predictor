"""Grade predictions against actual results.

Metrics per match:
  * outcome hit  — did argmax(home/draw/away) match the actual outcome?
  * Brier score  — sum of squared error across the 3-way one-hot outcome (0 best, 2 worst)
  * exact score  — did the most-likely scoreline match exactly?
An upset is a result whose actual outcome the model gave < UPSET_THRESHOLD probability.
"""
from __future__ import annotations

from dataclasses import dataclass

UPSET_THRESHOLD = 0.27  # actual outcome rated below this = flagged upset


def actual_outcome(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home"
    if away_goals > home_goals:
        return "away"
    return "draw"


@dataclass
class GradedMatch:
    id: str
    home: str
    away: str
    pred_outcome: str
    actual: str
    actual_score: tuple[int, int]
    pred_score: tuple[int, int]
    prob_of_actual: float
    brier: float
    outcome_hit: bool
    exact_hit: bool
    is_upset: bool


def grade(pred: dict, home_goals: int, away_goals: int) -> GradedMatch:
    probs = pred["probabilities"]
    p = {"home": probs["home_win"], "draw": probs["draw"], "away": probs["away_win"]}
    actual = actual_outcome(home_goals, away_goals)
    pred_outcome = max(p, key=p.__getitem__)

    brier = sum((p[o] - (1.0 if o == actual else 0.0)) ** 2 for o in ("home", "draw", "away"))
    ps = pred["predicted_scoreline"]
    pred_score = (ps["home"], ps["away"])
    exact = pred_score == (home_goals, away_goals)

    return GradedMatch(
        id=pred["id"], home=pred["home"], away=pred["away"],
        pred_outcome=pred_outcome, actual=actual,
        actual_score=(home_goals, away_goals), pred_score=pred_score,
        prob_of_actual=round(p[actual], 4), brier=round(brier, 4),
        outcome_hit=(pred_outcome == actual), exact_hit=exact,
        is_upset=(p[actual] < UPSET_THRESHOLD),
    )


def summarize(graded: list[GradedMatch]) -> dict:
    n = len(graded)
    if n == 0:
        return {"n": 0}
    return {
        "n": n,
        "outcome_accuracy": round(sum(g.outcome_hit for g in graded) / n, 4),
        "exact_scorelines": sum(g.exact_hit for g in graded),
        "mean_brier": round(sum(g.brier for g in graded) / n, 4),
        "upsets": [g for g in graded if g.is_upset],
    }
