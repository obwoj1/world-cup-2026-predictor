#!/usr/bin/env bash
# Refresh ALL data from live sources and regenerate every prediction output.
# Free sources, no API key needed. Run from anywhere:
#     bash pipeline/refresh.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Fetching live sources (Elo, schedule+results, squads)…"
python3 fetch_data.py --all

echo "==> Rebuilding teams (Elo + FIFA rank)…"
python3 build_ratings.py

echo "==> Rebuilding fixtures + results from the live schedule…"
python3 generate_fixtures.py

echo "==> Rebuilding squads…"
python3 build_players.py

echo "==> Re-running predictions…"
python3 predict.py

echo "==> Re-running tournament simulation…"
python3 simulate.py --sims 20000

echo "==> Done. Sync the web app with:  (cd ../web && npm run sync-data)"
