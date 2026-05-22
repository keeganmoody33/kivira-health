from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

from tam_builder.josh_pilot.constants import FIXTURE_DIR, SUBTIER_ORDER
from tam_builder.josh_pilot.read_buckets import match_read_bucket

FIRST_TOUCH_PERSONA_BOOST = {
    "bh_quality_influencer": 25,
    "operational_owner": 20,
    "clinical_champion": 15,
    "economic_buyer": 5,
    "tech_gatekeeper": 0,
}

READ_BUCKET_BOOST = {
    "integrated_care": 15,
    "regulatory_revenue": 10,
    "service_line": 8,
    "none": 0,
}


def _size_metric_score(raw: str) -> int:
    try:
        v = int((raw or "").strip())
    except ValueError:
        return 0
    if 5 <= v <= 30:
        return 15
    if 3 <= v <= 50:
        return 8
    return 0


def score_row(row: dict[str, str]) -> tuple[int, str, str]:
    parts: list[str] = []
    score = 0

    persona = row.get("persona", "unknown")
    p_boost = FIRST_TOUCH_PERSONA_BOOST.get(persona, 0)
    score += p_boost
    parts.append(f"persona:{persona}+{p_boost}")

    bucket = row.get("read_bucket") or match_read_bucket(row.get("title_raw", ""))
    b_boost = READ_BUCKET_BOOST.get(bucket, 0)
    score += b_boost
    parts.append(f"read:{bucket}+{b_boost}")

    sm = _size_metric_score(row.get("size_metric", ""))
    score += sm
    parts.append(f"size_metric+{sm}")

    if row.get("source", "").startswith("josh_pcp"):
        score += 12
        parts.append("pcp_seed+12")

    if row.get("linkedin_profile_url") or row.get("linkedin_profile_url_hint"):
        score += 10
        parts.append("has_url_hint+10")

    about = (row.get("linkedin_about") or row.get("snippet_or_quote") or "").lower()
    if any(k in about for k in ("cocm", "collaborative care", "behavioral health", "bhi")):
        score += 8
        parts.append("bh_signal+8")

    if row.get("source", "").startswith("wave1_fixture"):
        score += 5
        parts.append("fixture+5")

    grade = "A" if score >= 55 else "B" if score >= 40 else "C" if score >= 25 else "D"
    return score, "; ".join(parts), grade


def select_per_subtier(
    rows: list[dict[str, str]],
    *,
    min_per: int = 10,
    max_per: int = 25,
) -> list[dict[str, str]]:
    by_sub: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        code = (row.get("subtier_code") or "UNK").upper()
        by_sub[code].append(row)

    picked: list[dict[str, str]] = []
    for code in SUBTIER_ORDER:
        bucket = by_sub.get(code, [])
        if not bucket:
            continue
        bucket.sort(key=lambda r: (-int(r.get("pilot_score") or 0), r.get("contact_name", "")))
        cap = max_per
        if len(bucket) >= min_per:
            cap = max(min_per, min(max_per, len(bucket)))
        picked.extend(bucket[:cap])

    for code, bucket in by_sub.items():
        if code in SUBTIER_ORDER:
            continue
        bucket.sort(key=lambda r: (-int(r.get("pilot_score") or 0), r.get("contact_name", "")))
        picked.extend(bucket[:max_per])

    return picked


def run_score(
    *,
    in_csv: Path = FIXTURE_DIR / "candidates_with_subtier.csv",
    out_csv: Path = FIXTURE_DIR / "pilot_finalists_pre_linkedin.csv",
    min_per_subtier: int = 10,
    max_per_subtier: int = 25,
) -> dict[str, object]:
    if not in_csv.exists():
        raise FileNotFoundError(in_csv)

    rows: list[dict[str, str]] = []
    with in_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            ps, breakdown, grade = score_row(row)
            row["pilot_score"] = str(ps)
            row["pilot_score_breakdown"] = breakdown
            row["confidence_grade"] = grade
            rows.append(row)

    finalists = select_per_subtier(rows, min_per=min_per_subtier, max_per=max_per_subtier)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if finalists:
        fields: list[str] = []
        for r in finalists:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(finalists)

    warnings = [
        code
        for code in SUBTIER_ORDER
        if sum(1 for r in finalists if r.get("subtier_code") == code) < min_per_subtier
    ]

    return {"input": len(rows), "finalists": len(finalists), "thin_subtiers": warnings}


def main() -> int:
    try:
        stats = run_score()
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(f"Score: {stats}\n")
    if stats.get("thin_subtiers"):
        sys.stderr.write(f"Warning: thin subtiers: {stats['thin_subtiers']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
