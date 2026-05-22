from __future__ import annotations

import csv
import sys
from pathlib import Path

from tam_builder.josh_pilot.col4 import normalize_linkedin_url
from tam_builder.josh_pilot.constants import FIXTURE_DIR

BH_SIGNALS = ("cocm", "collaborative care", "behavioral health", "bhi", "population health")


def linkedin_quality_score(row: dict[str, str]) -> int:
    score = 0
    if normalize_linkedin_url(row.get("linkedin_profile_url") or ""):
        score += 40
    headline = (row.get("linkedin_headline") or "").strip()
    if headline:
        score += 20
    if (row.get("has_profile_photo") or "").lower() == "true":
        score += 25
    about = (row.get("linkedin_about") or "").lower()
    if len(about) > 80:
        score += 10
    if any(s in about or s in headline.lower() for s in BH_SIGNALS):
        score += 15
    return score


def passes_hard_gate(row: dict[str, str]) -> bool:
    if not normalize_linkedin_url(row.get("linkedin_profile_url") or ""):
        return False
    if not (row.get("linkedin_headline") or "").strip():
        return False
    if (row.get("has_profile_photo") or "").lower() != "true":
        return False
    return True


def run_gate(
    *,
    in_csv: Path = FIXTURE_DIR / "pilot_linkedin_master.csv",
    out_csv: Path = FIXTURE_DIR / "pilot_heyreach_ready.csv",
    min_quality: int = 60,
) -> dict[str, int]:
    if not in_csv.exists():
        raise FileNotFoundError(in_csv)

    ready: list[dict[str, str]] = []
    rejected = 0
    with in_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            row["linkedin_quality_score"] = str(linkedin_quality_score(row))
            if passes_hard_gate(row):
                ready.append(row)
            else:
                rejected += 1

    ready.sort(
        key=lambda r: (
            -int(r.get("linkedin_quality_score") or 0),
            -int(r.get("pilot_score") or 0),
        )
    )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if ready:
        fields: list[str] = []
        for r in ready:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(ready)

    return {"input": len(ready) + rejected, "ready": len(ready), "rejected": rejected}


def main() -> int:
    try:
        stats = run_gate()
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(f"Gate: {stats}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
