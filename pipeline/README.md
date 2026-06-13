# Prediction pipeline

Python scripts that turn raw data into the JSON the web app reads. Run them in order:

```bash
python fetch_data.py --all      # download raw sources -> data/sources/
python build_ratings.py         # data/sources -> data/teams.json (Elo, group, etc.)
python generate_fixtures.py     # real schedule -> data/fixtures.json + data/results.json
python build_players.py         # Wikipedia squads -> data/players.json (1248 players)
python predict.py               # per-match predictions -> data/predictions.json
python simulate.py --sims 20000 # Monte Carlo bracket -> data/projections.json
```

## Files
| File | Role |
|------|------|
| `common.py` | Canonical paths + JSON load/save helpers |
| `seed_draw_2026.py` | Authoritative 48-team / 12-group draw (cross-checked vs ESPN + FIFA) |
| `fetch_data.py` | Download raw sources (eloratings.net today) into `data/sources/` |
| `build_ratings.py` | Map the draw to real Elo ratings -> `teams.json` |
| `generate_fixtures.py` | Round-robin group fixtures -> `fixtures.json` |
| `model.py` | Elo -> expected goals -> Poisson scoreline model |
| `reasoning.py` | Evidence-cited reasoning text per match |
| `predict.py` | Per-match predictions -> `predictions.json` |
| `simulate.py` | Monte Carlo full tournament -> `projections.json` |
| `reconcile.py` | Post-matchweek reconciliation (Phase 5) |

## Model (v0.1.0)

**Per match.** Effective rating difference `dr = elo_home - elo_away + host_adj`, where a
host nation (USA/MEX/CAN) gets a `+65` Elo home-advantage bump. Expected goal supremacy
`sup = dr / 250` (≈250 Elo points per goal). Expected goals sit around a World-Cup
baseline total of 2.6: `λ_home = 2.6/2 + sup/2`, `λ_away = 2.6/2 - sup/2` (clamped). An
independent Poisson over both gives the full scoreline grid → win/draw/loss probabilities,
most-likely scoreline, and a confidence band (high ≥ 60%, medium ≥ 45%, else low).

**Tournament.** `simulate.py` plays every group match by sampling Poisson scorelines,
ranks groups (points, GD, GF), takes 12 winners + 12 runners-up + 8 best thirds, slots the
thirds into the official Round-of-32 bracket by satisfying Annex C eligibility constraints,
then plays R32→Final (knockout draws resolved by relative attacking strength). Over N runs
this yields each team's advance / reach-round / title probabilities.

**Current inputs:** Elo + host advantage only. Recent form, xG and player availability are
layered on next and the constants above are recalibrated against actual results during
reconciliation. This is a probabilistic baseline, **not betting advice.**
