#!/usr/bin/env bash
# Tier 1A pilot (GA only): discovery → campaign under output/pilot/.
# Prerequisites: output/accounts_classified_GA.csv from 01→02 (re-run 02 after upgrading so `website`/`phone_main` columns exist).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="${PY:-.venv/bin/python}"
SUBDIR="${SUBDIR:-pilot}"
ST="${ST:-GA}"
MAX="${MAX_ACCOUNTS:-400}"

"$PY" 03_discover_public_pages.py --base-dir . --states "$ST" \
  --pilot-subtier 1A --pilot-max-accounts "$MAX" --pilot-require-website

"$PY" 04_extract_contacts.py --base-dir . --states "$ST" --output-subdir "$SUBDIR" \
  --pilot-scale-page-cap

"$PY" 05_map_personas.py --base-dir . --states "$ST" --output-subdir "$SUBDIR" \
  --demo-bookable-min-fit 0.55

"$PY" 06_export_wave_lists.py --base-dir . --states "$ST" --output-subdir "$SUBDIR" \
  --readiness-ready-threshold 0.55 --skip-1a-size-floor --export-research-queue-contacts

"$PY" 07_quality_gate_and_dedupe.py --base-dir . --states "$ST" --output-subdir "$SUBDIR"
"$PY" 08_campaign_export_and_handoff.py --base-dir . --states "$ST" --output-subdir "$SUBDIR"

"$PY" scripts/validate_pipeline_outputs.py --base-dir . --output-subdir "$SUBDIR" --states "$ST"
