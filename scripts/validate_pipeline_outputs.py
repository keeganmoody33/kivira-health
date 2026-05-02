#!/usr/bin/env python3
"""
Per-stage sanity metrics for GTM pipeline outputs (03→06 and QA).

Example:
  .venv/bin/python scripts/validate_pipeline_outputs.py --base-dir . --output-subdir pilot --states GA
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from tam_builder.pilot_filters import resolve_output_dir


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")


def pct(n: int, d: int) -> str:
    if d <= 0:
        return "n/a"
    return f"{100.0 * n / d:.1f}%"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate pipeline CSV outputs and print stage metrics.")
    p.add_argument("--base-dir", default=".", help="Repo root (contains output/).")
    p.add_argument("--output-subdir", default="", help="Inspect output/<subdir>/ (e.g. pilot).")
    p.add_argument("--states", default="GA", help="Comma-separated states (default GA).")
    p.add_argument(
        "--min-ready-accounts",
        type=int,
        default=0,
        help="Exit 2 if wave1_accounts_* ready count is below this (0 = no check).",
    )
    args = p.parse_args(argv)

    base = Path(args.base_dir).expanduser().resolve()
    out = resolve_output_dir(base, str(args.output_subdir or ""))
    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]

    print(f"output_dir={out}")

    for st in states:
        pp = out / f"public_pages_{st}.csv"
        df = _read(pp)
        if not df.empty:
            nu = (df["discovered_url"].astype(str).str.strip() != "").sum() if "discovered_url" in df.columns else 0
            ca = (
                (df["crawl_allowed"].astype(str).str.lower().isin(["true", "1", "yes", ""])).sum()
                if "crawl_allowed" in df.columns
                else 0
            )
            print(f"[03 {st}] rows={len(df)} non_empty_url={pct(int(nu), len(df))} crawl_allowed_or_empty={pct(int(ca), len(df))}")
        else:
            print(f"[03 {st}] (missing or empty) {pp}")

        cr = out / f"contacts_raw_{st}.csv"
        df = _read(cr)
        if not df.empty:
            em = df["email"].astype(str).str.strip() != "" if "email" in df.columns else pd.Series([False] * len(df))
            ph = (
                (df["phone_direct"].astype(str).str.strip() != "")
                | (df["phone_main"].astype(str).str.strip() != "")
                if "phone_direct" in df.columns
                else pd.Series([False] * len(df))
            )
            nm = df["person_name"].astype(str).str.strip() != "" if "person_name" in df.columns else pd.Series([False] * len(df))
            any_contact = (em | ph).sum()
            print(
                f"[04 {st}] rows={len(df)} any_email_or_phone={pct(int(any_contact), len(df))} "
                f"with_person_name={pct(int(nm.sum()), len(df))}"
            )
        else:
            print(f"[04 {st}] (missing or empty) {cr}")

        cm = out / f"contacts_mapped_{st}.csv"
        df = _read(cm)
        if not df.empty:
            pr = df["persona_role_primary"].astype(str).str.strip() != "" if "persona_role_primary" in df.columns else pd.Series([False])
            db = (
                df["demo_bookable_flag"].astype(str).str.lower().isin(["true", "1", "yes"])
                if "demo_bookable_flag" in df.columns
                else pd.Series([False] * len(df))
            )
            print(
                f"[05 {st}] rows={len(df)} has_persona={pct(int(pr.sum()), len(df))} demo_bookable={pct(int(db.sum()), len(df))}"
            )
        else:
            print(f"[05 {st}] (missing or empty) {cm}")

        wa = out / f"wave1_accounts_{st}.csv"
        df = _read(wa)
        if not df.empty and "wave_status" in df.columns:
            vc = df["wave_status"].astype(str).str.lower().value_counts()
            ready = int(vc.get("ready", 0))
            review = int(vc.get("review", 0))
            excl = int(vc.get("exclude", 0))
            print(f"[06 {st}] accounts rows={len(df)} ready={ready} review={review} exclude={excl}")
            if args.min_ready_accounts > 0 and ready < int(args.min_ready_accounts):
                print(
                    f"FAIL: ready accounts {ready} < --min-ready-accounts {args.min_ready_accounts}",
                    file=sys.stderr,
                )
                return 2
            top_reasons = []
            if "wave_reason" in df.columns:
                top_reasons = (
                    df[df["wave_status"].astype(str).str.lower() == "exclude"]["wave_reason"]
                    .astype(str)
                    .value_counts()
                    .head(5)
                )
            if len(top_reasons):
                print(f"[06 {st}] top exclude reasons: {dict(top_reasons)}")
        else:
            print(f"[06 {st}] (missing or empty) {wa}")

        rq = out / f"research_queue_contacts_{st}.csv"
        if rq.exists():
            rdf = _read(rq)
            print(f"[06 {st}] research_queue_contacts rows={len(rdf)}")

    ev = out / "contact_evidence.csv"
    if ev.exists():
        edf = _read(ev)
        print(f"[04 evidence] rows={len(edf)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
