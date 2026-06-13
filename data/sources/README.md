# Data sources (traceability)

Every number used by the prediction engine must be traceable to a file in this folder.
When you fetch or download data, save the **raw payload here** and record where it came
from in `SOURCES.md` (date + URL). Team/player JSON objects then reference these files in
their `sources` field.

## Naming convention
```
<source>_<subject>_<YYYY-MM-DD>.<ext>
e.g.  elo_ratings_2026-06-13.html
      fbref_argentina_2026-06-13.csv
      transfermarkt_messi_2026-06-13.html
      apifootball_results_mw01_2026-06-14.json
```

## Source log
| File | Provider | URL | Fetched | Notes |
|------|----------|-----|---------|-------|
| _(none yet — populated in Phase 2)_ | | | | |

## Providers used
- **eloratings.net** — team Elo ratings
- **FBref / Transfermarkt** — club & international player stats, xG/xGA
- **FIFA.com** — official FIFA rankings, fixtures
- **Kaggle** — historical World Cup datasets
- **API-Football** — live fixtures & results (key added in Phase 2)
