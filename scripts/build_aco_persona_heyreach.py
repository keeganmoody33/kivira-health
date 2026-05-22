#!/usr/bin/env python3
"""Merge 2A ACO persona Spider results into a HeyReach-loadable lead list
plus a tiered metadata CSV for outbound triage.

Reads the raw_urls.json output of spider_account_search.py (one or both of
the 2a-aco-persona and 2a-bh-persona modes), classifies each matched person
into a buyer-persona bucket from their LinkedIn title text, tiers each ACO
by the density of qualified hits, and emits two artifacts:

  fixtures/heyreach_loads/heyreach_leads_2a_persona.json
      Strict HeyReach API shape: [{profileUrl, firstName, lastName,
      companyName, position}]. Ordered Tier A → C → unranked. Safe to
      load directly via `heyreach lists add-leads`.

  fixtures/aco_persona_ranked.csv
      Full metadata for review: rank, tier, persona_bucket, hits_per_aco,
      title, snippet, match_score, source_query. Use this to spot-check
      before pulling the trigger on HeyReach load.

Persona bucket mapping uses the PERSONA_TITLE_DICTIONARY_BY_SUBTIER Tier 2A
patterns. Tiering rule:
  Tier A : >= 3 qualified hits at the same ACO (major health-system parent,
           multiple named decision-makers findable)
  Tier B : 1-2 qualified hits at the same ACO with non-state-only brand token
           (genuine ACO with a named buyer; needs manual verification)
  Tier C : state-name-only brand match (likely cross-org collision) — keep
           in metadata CSV but DO NOT include in HeyReach JSON output

Usage:
  python3 scripts/build_aco_persona_heyreach.py \\
    --aco fixtures/wave1_runs/20260521T191019Z/Q2A_ACO_raw_urls.json \\
    --bh  fixtures/wave1_runs/20260521T163822Z/Q2A_BH_raw_urls.json \\
    --out-heyreach fixtures/heyreach_loads/heyreach_leads_2a_persona.json \\
    --out-meta     fixtures/aco_persona_ranked.csv
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.aco_persona_rules import (  # noqa: E402
    brand_is_state_only,
    brand_token,
    classify_persona,
    filter_persona_rows,
)


def extract_position(title_str: str) -> str:
    """Pull the human-readable position out of a Spider page title.

    Spider titles look like "Joe Smith - VP Population Health at FooHealth |
    LinkedIn" or "Joe Smith, MD - CMO at Bar Health". Returns the middle
    chunk between the first " - " or ", " and " | LinkedIn"/end.
    """
    if not title_str:
        return ""
    t = title_str
    # Strip "| LinkedIn" trailer.
    t = re.sub(r"\s*\|\s*LinkedIn\s*$", "", t)
    # Take everything after the first " - " (LinkedIn's name/title separator).
    parts = re.split(r"\s+-\s+", t, maxsplit=1)
    if len(parts) == 2:
        return parts[1].strip()
    return t.strip()


def split_name(first: str, last: str, fallback_title: str) -> tuple[str, str]:
    """Spider raw_urls.json doesn't carry firstName/lastName for persona
    modes — the Spider query was org-based, not name-based. Extract the
    name from the page title's "First Last - ..." prefix.
    """
    if first or last:
        return first or "", last or ""
    if not fallback_title:
        return "", ""
    prefix = re.split(r"\s+-\s+", fallback_title, maxsplit=1)[0]
    # Drop suffixes like ", MD", ", PhD"
    prefix = re.split(r",\s*(?:M\.?D\.?|Ph\.?D\.?|RN|MPH|JD|BCBA|LCSW|MBA)\b", prefix)[0]
    parts = prefix.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aco", required=True, help="Q2A_ACO_raw_urls.json path")
    ap.add_argument("--bh", help="Q2A_BH_raw_urls.json path (optional)")
    ap.add_argument("--out-heyreach", required=True)
    ap.add_argument("--out-meta", required=True)
    ap.add_argument(
        "--apply-anti-persona",
        action="store_true",
        help="Drop anti-persona titles and unknown-low-confidence rows before HeyReach export.",
    )
    args = ap.parse_args()

    rows: list[dict] = []
    for path, source_query in [(args.aco, "aco-persona"), (args.bh, "bh-persona")]:
        if not path:
            continue
        p = Path(path)
        if not p.exists():
            print(f"[skip] {path} (not found)", file=sys.stderr)
            continue
        data = json.loads(p.read_text())
        for r in data["results"]:
            rows.append({**r, "_source_query": source_query})

    print(f"[merge] {len(rows)} raw rows from inputs", file=sys.stderr)

    # Dedup by LinkedIn URL (keep first occurrence, prefer aco-persona over bh).
    seen: dict[str, dict] = {}
    for r in rows:
        url = (r.get("linkedin_profile_url") or "").rstrip("/").lower()
        if not url:
            continue
        if url not in seen:
            seen[url] = r
        else:
            # If we already saw it from bh-persona and this is aco-persona,
            # prefer the aco-persona record (broader buyer search).
            if seen[url]["_source_query"] == "bh-persona" and r["_source_query"] == "aco-persona":
                seen[url] = r
    rows = list(seen.values())
    print(f"[dedup] {len(rows)} unique LinkedIn URLs", file=sys.stderr)

    # Classify persona + extract name/position.
    enriched: list[dict] = []
    for r in rows:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        url = (r.get("linkedin_profile_url") or "").rstrip("/")
        company = r.get("source_account", "")
        state = r.get("source_state", "")

        persona, conf = classify_persona(title, snippet)
        position = extract_position(title)
        first, last = split_name("", "", title)

        enriched.append({
            "profileUrl": url,
            "firstName": first,
            "lastName": last,
            "companyName": company,
            "position": position,
            "_persona_bucket": persona,
            "_persona_confidence": conf,
            "_match_score": r.get("match_score", 0),
            "_source_query": r["_source_query"],
            "_title": title,
            "_snippet": snippet,
            "_state": state,
            "_brand_token": brand_token(company) or "",
            "_brand_is_state_only": brand_is_state_only(company),
        })

    if args.apply_anti_persona:
        pre = len(enriched)
        kept, dropped = filter_persona_rows(enriched)
        enriched = kept
        print(
            f"[anti-persona] dropped {len(dropped)} of {pre} "
            f"(kept {len(enriched)})",
            file=sys.stderr,
        )

    # Hit count per ACO (post-dedup).
    aco_hits: dict[str, int] = defaultdict(int)
    for e in enriched:
        aco_hits[e["companyName"]] += 1

    # Tier assignment.
    for e in enriched:
        n = aco_hits[e["companyName"]]
        if e["_brand_is_state_only"]:
            e["_tier"] = "C"
        elif n >= 3:
            e["_tier"] = "A"
        elif n >= 1:
            e["_tier"] = "B"
        else:
            e["_tier"] = "C"

    # Sort: Tier A first, then B, then C; within tier by hits-per-ACO desc,
    # then by persona-confidence (H > M > L), then alpha.
    conf_rank = {"H": 0, "M": 1, "L": 2}
    enriched.sort(key=lambda r: (
        {"A": 0, "B": 1, "C": 2}[r["_tier"]],
        -aco_hits[r["companyName"]],
        conf_rank.get(r["_persona_confidence"], 3),
        r["companyName"].lower(),
        r["lastName"].lower(),
    ))

    # Write the strict HeyReach JSON (Tier A + B only).
    heyreach_rows = [
        {
            "profileUrl": e["profileUrl"],
            "firstName": e["firstName"],
            "lastName": e["lastName"],
            "companyName": e["companyName"],
            "position": e["position"],
        }
        for e in enriched if e["_tier"] in ("A", "B")
    ]
    out_hr = Path(args.out_heyreach)
    out_hr.parent.mkdir(parents=True, exist_ok=True)
    out_hr.write_text(json.dumps(heyreach_rows, indent=2))

    # Write the full metadata CSV (all tiers).
    out_meta = Path(args.out_meta)
    out_meta.parent.mkdir(parents=True, exist_ok=True)
    with out_meta.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank", "tier", "hits_per_aco", "persona_bucket",
            "persona_confidence", "match_score", "source_query",
            "firstName", "lastName", "companyName", "state",
            "brand_token", "position", "profileUrl",
            "linkedin_title", "snippet",
        ])
        for i, e in enumerate(enriched, 1):
            writer.writerow([
                i, e["_tier"], aco_hits[e["companyName"]], e["_persona_bucket"],
                e["_persona_confidence"], e["_match_score"], e["_source_query"],
                e["firstName"], e["lastName"], e["companyName"], e["_state"],
                e["_brand_token"], e["position"], e["profileUrl"],
                e["_title"], e["_snippet"],
            ])

    # Diagnostics.
    from collections import Counter
    tier_counts = Counter(e["_tier"] for e in enriched)
    persona_counts = Counter(e["_persona_bucket"] for e in enriched)
    print(f"[wrote] {out_hr} — {len(heyreach_rows)} rows (Tier A+B)", file=sys.stderr)
    print(f"[wrote] {out_meta} — {len(enriched)} rows (all tiers)", file=sys.stderr)
    print(f"[tiers] {dict(tier_counts)}", file=sys.stderr)
    print(f"[personas] {dict(persona_counts)}", file=sys.stderr)
    print(f"[orgs] {len(aco_hits)} unique ACOs in output", file=sys.stderr)


if __name__ == "__main__":
    main()
