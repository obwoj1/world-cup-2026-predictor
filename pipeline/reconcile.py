"""Phase 5 — post-matchweek reconciliation.

After a matchweek finishes:
  1. pull actual results into data/results.json,
  2. compare them to what was predicted (outcome accuracy, Brier score, scoreline hits),
  3. flag upsets/surprises and reason about why they happened,
  4. update team ratings/form from the results (re-run build_ratings),
  5. re-run predictions for all remaining matches (re-run predict),
  6. write a "what changed and why" summary to reconciliations/matchweek-NN.md.

Usage:
    python reconcile.py --matchweek 1

NOTE: stub — implemented in Phase 5.
"""
from __future__ import annotations

import argparse

from common import RECONCILIATIONS_DIR, RESULTS_FILE, PREDICTIONS_FILE, load_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile predictions vs actual results")
    parser.add_argument("--matchweek", type=int, required=True, help="Matchweek number")
    args = parser.parse_args()

    results = load_json(RESULTS_FILE)
    predictions = load_json(PREDICTIONS_FILE)
    out = RECONCILIATIONS_DIR / f"matchweek-{args.matchweek:02d}.md"

    print(f"[reconcile] matchweek {args.matchweek}: {len(results)} results, "
          f"{len(predictions)} predictions on file")
    print(f"[reconcile] would write summary to {out}")
    print("[reconcile] stub — implemented in Phase 5.")


if __name__ == "__main__":
    main()
