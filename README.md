# World Cup 2026 — Prediction & Analysis

A probabilistic forecasting tool that predicts outcomes for every remaining match of
the FIFA World Cup 2026 (group stage through final), with **transparent, evidence-cited
reasoning** for each prediction. It also flags standout "players to watch" per match,
and after every matchweek runs a full **reconciliation** against the actual results —
logging what changed and why.

> ⚠️ **This is a probabilistic forecasting and analysis tool, not betting advice.**
> Predictions are model estimates with explicit uncertainty. Do not use them to gamble.

---

## How it works

```
   data sources (Elo, form, club stats, fixtures)
                 │
                 ▼
   pipeline/  ── Python ──►  data/*.json   (ratings, predictions, evidence)
                 │
                 ▼
   web/      ── Next.js ──►  dashboard, group tables, bracket, players, recon log
```

The **Python pipeline** computes everything offline (reproducible, fully cited) and
writes JSON. The **Next.js app** only renders that JSON — so every number on screen is
traceable back to a source file in `data/sources/`.

## Repository layout

| Path | Purpose |
|------|---------|
| `data/teams.json` | 48 teams: Elo, FIFA rank, recent form, xG/xGA, WC knockout history |
| `data/players.json` | Key players: club-season stats, international record, big-game history |
| `data/fixtures.json` | Full WC 2026 schedule |
| `data/results.json` | Actual results, filled in as the tournament progresses |
| `data/predictions.json` | Current predictions for all remaining matches |
| `data/sources/` | Raw scraped/downloaded data **+ source URLs** (traceability) |
| `reconciliations/` | One markdown log per matchweek ("what changed and why") |
| `pipeline/` | Python: fetch → build ratings → predict → reconcile |
| `web/` | Next.js + Tailwind UI |

## Prediction method (summary)

For each match the engine produces:

- **Win / draw / loss probabilities** and a **predicted scoreline**, via a Poisson model
  whose expected-goals inputs are calibrated from team **Elo**, **recent form**, and
  **home/host advantage**.
- A short **reasoning paragraph** citing specific evidence (e.g. *"Elo gap of 120,
  unbeaten in last 8, striker scored in 5 of last 6"*).
- **1–3 players to watch**, each tied to underlying stats and big-tournament history.
- A **confidence level**, not just a point prediction.

Full methodology is documented in `pipeline/README.md` (added in Phase 3).

## Setup

### Pipeline (Python)
```bash
cd pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Web (Next.js)
```bash
cd web
npm install
npm run dev
```

## Running a reconciliation (after a matchweek)

1. Add the matchweek's actual scores to `data/results.json`:
   ```json
   [{"id": "M001", "home_goals": 2, "away_goals": 1, "status": "final"}]
   ```
2. Run the reconciliation:
   ```bash
   cd pipeline
   source .venv/bin/activate
   python reconcile.py --matchweek 1            # grade + update + re-run + write log
   python reconcile.py --matchweek 1 --dry-run  # preview metrics only, writes nothing
   python reconcile.py --matchweek 1 --commit   # also git-commit the result
   ```

This grades the standing predictions against the results (outcome accuracy, Brier score,
exact scorelines), flags upsets and explains them, updates each team's Elo and form,
re-runs predictions and the Monte Carlo simulation for all remaining matches, and writes a
"what changed and why" summary to `reconciliations/matchweek-01.md`. The graded predictions
are snapshotted to `data/snapshots/` for traceability. Commit with a message like
`Matchweek 1 reconciliation`.

## Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Plan & scaffold | ✅ done |
| 2 | Data pipeline | ✅ teams (real Elo) + fixtures done; form/xG/players to enrich |
| 3 | Prediction engine | ✅ Poisson per-match + Monte Carlo bracket odds |
| 4 | Web app UI | ✅ fixtures, groups, title race, players, reconciliation pages |
| 5 | Reconciliation workflow | ✅ grade, Elo/form update, re-run, matchweek log |

## License & disclaimer

For educational and analytical purposes only. Data is sourced from public providers
(eloratings.net, FBref/Transfermarkt, FIFA.com, API-Football); see `data/sources/` for
attribution. Not affiliated with FIFA. **Not betting advice.**
