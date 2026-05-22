from __future__ import annotations

import csv
import sys
from pathlib import Path

from tam_builder.josh_pilot.col4 import normalize_linkedin_url
from tam_builder.josh_pilot.constants import FIXTURE_DIR, HEYREACH_FIELDS
from tam_builder.briefing import build_value_prop_angle

LANE_NOTES = {
    "clinical": "CDS-aligned workflow for BH integration and screening follow-through.",
    "roi": "Directional reimbursement/workflow support — no guaranteed revenue claims.",
    "ops": "Day-to-day workflow relief for care management and follow-up consistency.",
}


def split_name(raw: str) -> tuple[str, str]:
    s = (raw or "").strip().strip('"')
    if not s:
        return "", ""
    before_comma = s.split(",")[0].strip()
    parts = before_comma.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def build_notes(row: dict[str, str]) -> str:
    lane = row.get("message_lane", "ops")
    headline = (row.get("linkedin_headline") or "")[:120]
    about = (row.get("linkedin_about") or row.get("snippet_or_quote") or "")[:160]
    angle = build_value_prop_angle(
        {
            "cfo": "roi",
            "cmio": "ops",
            "pop_health": "clinical",
            "bh_ops": "clinical",
            "pcp": "clinical",
        }.get(lane, "pcp"),
        row,
    )
    parts = [
        f"lane={lane}",
        LANE_NOTES.get(lane, ""),
        f"headline: {headline}" if headline else "",
        f"about: {about}" if about else "",
        angle,
        (row.get("lane_rationale") or "")[:80],
    ]
    return " | ".join(p for p in parts if p)


def run_export(
    *,
    in_csv: Path = FIXTURE_DIR / "pilot_heyreach_ready.csv",
    heyreach_csv: Path = FIXTURE_DIR / "heyreach_import.csv",
    detail_csv: Path = FIXTURE_DIR / "heyreach_import_profile_detail.csv",
) -> dict[str, int]:
    if not in_csv.exists():
        raise FileNotFoundError(in_csv)

    hey_rows: list[dict[str, str]] = []
    detail_rows: list[dict[str, str]] = []

    with in_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            fn, ln = split_name(row.get("contact_name", ""))
            position = (
                row.get("linkedin_position")
                or row.get("linkedin_headline")
                or row.get("title_raw")
                or ""
            ).strip()
            hey_rows.append(
                {
                    "profileUrl": normalize_linkedin_url(row.get("linkedin_profile_url") or ""),
                    "firstName": fn,
                    "lastName": ln,
                    "companyName": (row.get("org_name") or "").strip(),
                    "position": position,
                    "persona": row.get("persona", ""),
                    "subtier": row.get("subtier_code", ""),
                    "subtier_confidence": row.get("persona_confidence", ""),
                    "signal": row.get("pilot_score", ""),
                    "source_query": row.get("source", ""),
                    "notes": build_notes(row),
                    "subtier_code": row.get("subtier_code", ""),
                    "message_lane": row.get("message_lane", ""),
                }
            )
            detail_rows.append(
                {
                    "profileUrl": hey_rows[-1]["profileUrl"],
                    "contact_name": row.get("contact_name", ""),
                    "linkedin_headline": row.get("linkedin_headline", ""),
                    "linkedin_position": row.get("linkedin_position", ""),
                    "linkedin_about": row.get("linkedin_about", ""),
                    "has_profile_photo": row.get("has_profile_photo", ""),
                    "message_lane": row.get("message_lane", ""),
                    "persona": row.get("persona", ""),
                    "pilot_score": row.get("pilot_score", ""),
                    "validation_flags": row.get("validation_flags", ""),
                }
            )

    heyreach_csv.parent.mkdir(parents=True, exist_ok=True)
    with heyreach_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(HEYREACH_FIELDS))
        w.writeheader()
        w.writerows(hey_rows)

    with detail_csv.open("w", encoding="utf-8", newline="") as f:
        fields = list(detail_rows[0].keys()) if detail_rows else ["profileUrl"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(detail_rows)

    return {"heyreach_rows": len(hey_rows)}


def main() -> int:
    try:
        stats = run_export()
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(f"Export: {stats}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
