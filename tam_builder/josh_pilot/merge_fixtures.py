from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from tam_builder.josh_pilot.col4 import normalize_linkedin_url
from tam_builder.josh_pilot.constants import (
    ACO_WAVE2_CSV,
    FIXTURE_DIR,
    WAVE1_RUNS_DIR,
)
from tam_builder.josh_pilot.message_lane import classify_message_lane
from tam_builder.josh_pilot.read_buckets import match_read_bucket
from tam_builder.persona_rules import tag_persona_keyword

QUERY_SUBTIER_RE = re.compile(r"Q(\d[A-C])", re.IGNORECASE)


def guess_josh_subtier(row: dict[str, str]) -> str:
    org_type = (row.get("org_type") or "").lower()
    title = (row.get("title_raw") or "").lower()
    try:
        metric = int((row.get("size_metric") or "0").strip())
    except ValueError:
        metric = 0

    if "independent practice association" in org_type:
        return "1C"
    if any(
        k in title
        for k in ("primary care", "family medicine", "internal medicine", "pcp", "physician owner")
    ):
        return "1B"
    if metric and metric < 15:
        return "1B"
    return "1A"


def _subtier_from_query_id(query_id: str, expected: list[str]) -> str:
    if expected:
        return str(expected[0]).upper().strip()
    m = QUERY_SUBTIER_RE.search(query_id or "")
    return m.group(1).upper() if m else "UNK"


def _parse_name_from_url_title(title: str) -> tuple[str, str]:
    """Best-effort name from LinkedIn search title snippet."""
    s = (title or "").split("|")[0].strip()
    parts = [p.strip() for p in s.split(" - ") if p.strip()]
    if not parts:
        return "", ""
    name = parts[0].split(",")[0].strip()
    tokens = name.split()
    if len(tokens) < 2:
        return tokens[0] if tokens else "", ""
    return tokens[0], " ".join(tokens[1:])


def load_wave1_fixture_rows(runs_dir: Path = WAVE1_RUNS_DIR) -> list[dict[str, str]]:
    if not runs_dir.exists():
        return []

    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir() or run_dir.name.startswith(("TEST_", "_")):
            continue
        for json_path in sorted(run_dir.glob("Q*_raw_urls.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            subtier = _subtier_from_query_id(
                payload.get("query_id", ""),
                payload.get("expected_subtiers") or [],
            )
            qid = payload.get("query_id", json_path.stem)
            for hit in payload.get("results") or []:
                url = normalize_linkedin_url(hit.get("linkedin_profile_url") or "")
                if not url or url in seen:
                    continue
                seen.add(url)
                title_snip = hit.get("title") or ""
                snippet = hit.get("snippet") or ""
                fn, ln = _parse_name_from_url_title(title_snip)
                tag = tag_persona_keyword(title_snip, "")
                lane, lane_r = classify_message_lane(
                    title_snip, persona=tag["persona"], headline=title_snip, about=snippet
                )
                rows.append(
                    {
                        "contact_id": f"fixture:{qid}:{url}",
                        "contact_name": f"{fn} {ln}".strip(),
                        "title_raw": title_snip,
                        "title_bucket": "",
                        "org_name": "",
                        "org_type": "fixture_linkedin",
                        "city": "",
                        "state": "",
                        "size_metric": "",
                        "source": f"wave1_fixture:{qid}",
                        "subtier_code": subtier,
                        "persona": tag["persona"],
                        "persona_confidence": tag["confidence"],
                        "persona_rationale": tag["rationale"],
                        "message_lane": lane,
                        "lane_rationale": lane_r,
                        "read_bucket": match_read_bucket(title_snip),
                        "linkedin_profile_url": url,
                        "linkedin_headline": title_snip,
                        "linkedin_position": title_snip,
                        "linkedin_about": snippet[:500],
                        "snippet_or_quote": snippet[:280],
                        "enrichment_source": "wave1_fixture",
                        "has_profile_photo": "true" if title_snip else "false",
                        "enrichment_confidence": "medium",
                    }
                )
    return rows


def load_aco_wave2_rows(path: Path = ACO_WAVE2_CSV) -> list[dict[str, str]]:
    if not path.exists():
        return []
    out: list[dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("exec_name") or "").strip()
            org = (row.get("aco_name") or "").strip()
            if not name:
                continue
            tag = tag_persona_keyword("ACO Executive", org)
            lane, lane_r = classify_message_lane("ACO population health", persona=tag["persona"])
            out.append(
                {
                    "contact_id": f"aco:{row.get('aco_id', '')}",
                    "contact_name": name,
                    "title_raw": "ACO Executive (CMS filing)",
                    "org_name": org,
                    "org_type": "aco",
                    "state": (row.get("state") or "").strip(),
                    "source": "aco_wave2_account",
                    "subtier_code": "2A",
                    "persona": tag["persona"],
                    "persona_confidence": "low",
                    "persona_rationale": "cms placeholder — needs linkedin fixture match",
                    "message_lane": lane,
                    "lane_rationale": lane_r,
                    "read_bucket": "regulatory_revenue",
                    "validation_flags": "needs_linkedin_url",
                }
            )
    return out


def merge_candidates(
    *,
    candidates_csv: Path = FIXTURE_DIR / "candidates_filtered.csv",
    out_csv: Path = FIXTURE_DIR / "candidates_with_subtier.csv",
) -> dict[str, int]:
    if not candidates_csv.exists():
        raise FileNotFoundError(candidates_csv)

    merged: list[dict[str, str]] = []
    with candidates_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)
            row["subtier_code"] = guess_josh_subtier(row)
            row["read_bucket"] = match_read_bucket(row.get("title_raw", ""))
            lane, lane_r = classify_message_lane(
                row.get("title_raw", ""),
                persona=row.get("persona", ""),
            )
            row["message_lane"] = lane
            row["lane_rationale"] = lane_r
            row["contact_id"] = f"josh:{row.get('org_name', '')}:{row.get('contact_name', '')}"
            merged.append(row)

    fixture_rows = load_wave1_fixture_rows()
    merged.extend(fixture_rows)

    counts: dict[str, int] = {}
    for r in merged:
        code = r.get("subtier_code", "UNK")
        counts[code] = counts.get(code, 0) + 1

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if merged:
        fields: list[str] = []
        for r in merged:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(merged)

    return {"josh_rows": len(merged) - len(fixture_rows), "fixture_rows": len(fixture_rows), **counts}


def main() -> int:
    try:
        stats = merge_candidates()
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(f"Merged candidates: {stats}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
