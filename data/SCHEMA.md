# Data schemas

All prediction inputs and outputs are plain JSON so they're human-readable and
git-diffable. Every numeric input should be traceable to a file in `sources/`.

## `teams.json` — array of team objects
```jsonc
{
  "id": "ARG",              // FIFA 3-letter code
  "name": "Argentina",
  "confederation": "CONMEBOL",
  "group": "A",
  "elo": 2105,              // eloratings.net
  "fifa_rank": 1,           // FIFA.com
  "form": {                 // recent results, most recent first
    "last_n": 10,
    "record": "W7 D2 L1",
    "goals_for": 21,
    "goals_against": 6,
    "matches": ["W 2-0 vs CHI", "D 1-1 vs URU", "..."]
  },
  "xg": { "xgf_per90": 1.9, "xga_per90": 0.8, "source": "fbref" },
  "wc_knockout_history": "Won 2022; finalist 2014; ...",
  "sources": ["sources/elo_2026-06-13.html", "sources/fifa_ranking.csv"]
}
```

## `players.json` — array of player objects
```jsonc
{
  "id": "messi-lionel",
  "name": "Lionel Messi",
  "team": "ARG",
  "position": "FW",
  "club_season": { "comp": "MLS 2025", "goals": 20, "assists": 12, "xg": 16.4, "xa": 9.1, "minutes": 2400 },
  "international": { "caps": 190, "goals": 112 },
  "big_tournament": "5 goals + 3 assists at WC 2022 (Golden Ball)",
  "sources": ["sources/transfermarkt_messi.html"]
}
```

## `fixtures.json` — array of match objects
```jsonc
{
  "id": "M01",
  "matchweek": 1,
  "stage": "group",         // group | r32 | r16 | qf | sf | final | third_place
  "group": "A",
  "date": "2026-06-11",
  "venue": "Estadio Azteca, Mexico City",
  "home": "MEX",            // for knockouts, "home" is just slot ordering
  "away": "TBD"
}
```

## `results.json` — array, filled in as matches finish
```jsonc
{ "id": "M01", "home_goals": 2, "away_goals": 1, "status": "final", "source": "sources/results_mw01.json" }
```

## `predictions.json` — array, one per remaining match
```jsonc
{
  "id": "M01",
  "generated_at": "2026-06-13T00:00:00Z",
  "model_version": "0.1.0",
  "probabilities": { "home_win": 0.58, "draw": 0.24, "away_win": 0.18 },
  "predicted_scoreline": { "home": 2, "away": 1 },
  "expected_goals": { "home": 1.8, "away": 0.9 },
  "confidence": "medium",   // low | medium | high
  "reasoning": "Elo gap of 120 favours the hosts; unbeaten in last 8 ...",
  "players_to_watch": [
    { "player_id": "messi-lionel", "evidence": "Scored in 5 of last 6 internationals; 5 goals at WC 2022." }
  ],
  "evidence_refs": ["teams.json:ARG", "players.json:messi-lionel"]
}
```
