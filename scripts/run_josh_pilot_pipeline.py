#!/usr/bin/env python3
"""Run the Josh Drs Group → HeyReach pilot pipeline end-to-end.

Stages:
  ingest → filter → merge → score → enrich → gate → export

Usage:
  python3 scripts/run_josh_pilot_pipeline.py
  python3 scripts/run_josh_pilot_pipeline.py --skip-enrich
  python3 scripts/run_josh_pilot_pipeline.py --enrich-max-rows 50 --skip-scrape
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.josh_pilot.enrich import run_enrich  # noqa: E402
from tam_builder.josh_pilot.export_campaigns import run_export  # noqa: E402
from tam_builder.josh_pilot.filter_candidates import run_filter  # noqa: E402
from tam_builder.josh_pilot.gate import run_gate  # noqa: E402
from tam_builder.josh_pilot.ingest import run_ingest  # noqa: E402
from tam_builder.josh_pilot.merge_fixtures import merge_candidates  # noqa: E402
from tam_builder.josh_pilot.score import run_score  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-enrich", action="store_true")
    p.add_argument("--skip-scrape", action="store_true")
    p.add_argument("--enrich-max-rows", type=int, default=None)
    p.add_argument("--min-per-subtier", type=int, default=10)
    p.add_argument("--max-per-subtier", type=int, default=25)
    args = p.parse_args()

    run_ingest()
    run_filter()
    merge_candidates()
    run_score(min_per_subtier=args.min_per_subtier, max_per_subtier=args.max_per_subtier)

    if not args.skip_enrich:
        log = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "enrichment_log.jsonl"
        if log.exists():
            log.unlink()
        run_enrich(
            max_rows=args.enrich_max_rows,
            skip_scrape=args.skip_scrape,
        )
    else:
        # Copy pre-linkedin to master for gate when skipping enrich
        src = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "pilot_finalists_pre_linkedin.csv"
        dst = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "pilot_linkedin_master.csv"
        if src.exists():
            dst.write_bytes(src.read_bytes())

    run_gate()
    run_export()
    sys.stdout.write("Josh pilot pipeline complete → fixtures/josh_drs_group_2026/\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
