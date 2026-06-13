# Reconciliation logs

After each matchweek the pipeline compares predictions to actual results and writes a
log here (`matchweek-01.md`, `matchweek-02.md`, …). Each log is committed with a message
like `Matchweek 1 reconciliation`.

## What each log contains
1. **Scoreboard** — predicted vs actual for every match that week, with a hit/miss flag.
2. **Accuracy metrics** — outcome accuracy, Brier score, scoreline exactness.
3. **Upsets & surprises** — matches the model got wrong, and the likely *why*.
4. **Rating/form updates** — how team Elo and form were adjusted from the results.
5. **What changed downstream** — notable swings in predictions for remaining matches.

## Template
```markdown
# Matchweek N Reconciliation — <date range>

## Scoreboard
| Match | Predicted | Actual | Outcome hit? | Scoreline hit? |
|-------|-----------|--------|--------------|----------------|

## Accuracy
- Outcome accuracy: X / Y (Z%)
- Mean Brier score: 0.XX
- Exact scorelines: X / Y

## Upsets & surprises
- ...

## Rating & form updates
- ...

## What changed for remaining matches
- ...
```
