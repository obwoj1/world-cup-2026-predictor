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
| `elo_world_2026-06-13.tsv` | eloratings.net | https://www.eloratings.net/World.tsv | 2026-06-13 | Full world Elo table; cols: rank, rank, ISO2 code, Elo rating, … |
| `elo_teamcodes_2026-06-13.tsv` | eloratings.net | https://www.eloratings.net/en.teams.tsv | 2026-06-13 | ISO2 code → country name map |
| _group draw_ | ESPN / FIFA | https://www.espn.com/soccer/story/_/id/48939282 | 2026-06-13 | 12-group composition, cross-checked vs FIFA group previews; encoded in `pipeline/seed_draw_2026.py` |
| `fixtures_fixturedownload_2026-06-13.json` | fixturedownload.com | https://fixturedownload.com/feed/json/fifa-world-cup-2026 | 2026-06-13 | Official 104-match schedule: real dates, venues, pairings, knockout bracket slots, and live results. Parsed by `generate_fixtures.py` into fixtures.json + results.json |
| `wiki_squads_raw_2026-06-13.txt` | Wikipedia | https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads?action=raw | 2026-06-13 | Raw wikitext of all 48 final 26-man squads (position, caps, intl goals, club per player). Parsed by `build_players.py` into players.json |
| _FIFA ranking_ | FIFA via ESPN + whereig.com | https://www.espn.com/soccer/story/_/id/46664763 | 2026-06-13 | June 2026 FIFA world ranking for all 48 finalists; encoded in `pipeline/seed_fifa_rankings.py` (shown alongside Elo for context; model uses Elo) |

## Providers used
- **eloratings.net** — team Elo ratings
- **FBref / Transfermarkt** — club & international player stats, xG/xGA
- **FIFA.com** — official FIFA rankings, fixtures
- **Kaggle** — historical World Cup datasets
- **API-Football** — live fixtures & results (key added in Phase 2)
