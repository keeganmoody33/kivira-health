#!/usr/bin/env python3
"""Build Tier 2A ACO attack lists from CMS MSSP Organizations (+ optional REACH CSV).

Outputs under fixtures/aco_attack/:
  mssp_2a_master.csv      — net 2A orgs after shell/hospital exclusions
  high_fit_2a.csv         — HIGH fit (ENHANCED + period>=3, or REACH)
  wave2_linkedin_2a.csv   — top N high-fit for LinkedIn Wave 2 (~135 default)
  blitz_focus_2a.csv      — sync blitz cohort (default 40; CMS exec contact required)
  excluded_2a.csv         — rows filtered out with exclude_reason

Usage:
  python3 scripts/build_aco_attack_lists.py
  python3 scripts/build_aco_attack_lists.py --reach-csv path/to/reach.csv
  python3 scripts/build_aco_attack_lists.py --mssp-csv artifacts/cms_mssp_orgs_py2026.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.aco_attack import (  # noqa: E402
    DEFAULT_MSSP_ORGS_URL,
    load_mssp_orgs,
    net_2a_orgs,
    parse_reach_rows,
    to_csv_dict,
    write_attack_csv,
)

DEFAULT_OUT_DIR = REPO_ROOT / "fixtures" / "aco_attack"
WAVE1_TOUCHED_ORGS = REPO_ROOT / "fixtures" / "heyreach_loads" / "heyreach_leads_2a.json"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _wave1_touched_company_names() -> set[str]:
    if not WAVE1_TOUCHED_ORGS.exists():
        return set()
    import json

    data = json.loads(WAVE1_TOUCHED_ORGS.read_text(encoding="utf-8"))
    return {
        (item.get("companyName") or "").strip().lower()
        for item in data
        if item.get("companyName")
    }


def _sort_blitz_key(row) -> tuple:
    """REACH and PC Flex first; then period desc; then name."""
    reach = 0 if row.value_based_track == "ACO REACH" else 1
    pc = 0 if row.pc_flex else 1
    return (reach, pc, -row.agreement_period_num, row.aco_name.lower())


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build 2A ACO attack CSVs from CMS.")
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument("--mssp-csv", type=Path, help="Cached MSSP Organizations CSV.")
    p.add_argument("--mssp-url", default=DEFAULT_MSSP_ORGS_URL)
    p.add_argument("--reach-csv", type=Path, help="Optional ACO REACH participants CSV.")
    p.add_argument("--wave2-size", type=int, default=135)
    p.add_argument("--blitz-size", type=int, default=40)
    p.add_argument("--blitz-fresh-only", action="store_true", default=True,
                   help="Exclude org names already in heyreach_leads_2a.json (default: on).")
    args = p.parse_args(argv)

    mssp = load_mssp_orgs(
        csv_path=args.mssp_csv,
        url=args.mssp_url if not args.mssp_csv else DEFAULT_MSSP_ORGS_URL,
    )
    reach: list = []
    if args.reach_csv and args.reach_csv.exists():
        reach = parse_reach_rows(_read_csv(args.reach_csv))

    all_rows = mssp + reach
    excluded = [r for r in all_rows if r.exclude_reason]
    net = net_2a_orgs(mssp, reach)
    high = [r for r in net if r.fit_tier == "HIGH" and r.has_cms_contact]
    high_sorted = sorted(high, key=_sort_blitz_key)

    touched = _wave1_touched_company_names() if args.blitz_fresh_only else set()
    blitz_pool = [
        r for r in high_sorted
        if r.aco_name.lower() not in touched
    ]
    blitz = blitz_pool[: args.blitz_size]
    wave2 = high_sorted[: args.wave2_size]

    out = args.out_dir
    write_attack_csv(out / "mssp_2a_master.csv", net)
    write_attack_csv(out / "high_fit_2a.csv", high_sorted)
    write_attack_csv(out / "wave2_linkedin_2a.csv", wave2)
    write_attack_csv(out / "blitz_focus_2a.csv", blitz)
    write_attack_csv(out / "excluded_2a.csv", excluded)

    if args.mssp_csv is None:
        cache = REPO_ROOT / "artifacts" / "cms_mssp_orgs_py2026.csv"
        cache.parent.mkdir(parents=True, exist_ok=True)
        if not cache.exists():
            from tam_builder.aco_attack import _http_get_text

            cache.write_text(_http_get_text(args.mssp_url), encoding="utf-8")
            print(f"Cached MSSP orgs → {cache}", file=sys.stderr)

    print(f"MSSP org rows loaded: {len(mssp)}")
    print(f"REACH rows loaded: {len(reach)}")
    print(f"Excluded: {len(excluded)}")
    print(f"Net 2A: {len(net)}")
    print(f"HIGH fit (CMS contact): {len(high_sorted)}")
    print(f"Wave 2 slice: {len(wave2)} → {out / 'wave2_linkedin_2a.csv'}")
    print(f"Blitz focus: {len(blitz)} → {out / 'blitz_focus_2a.csv'}")
    if touched:
        print(f"Blitz skipped {len(high_sorted) - len(blitz_pool)} Wave-1-touched orgs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
