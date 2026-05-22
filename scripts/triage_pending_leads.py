#!/usr/bin/env python3
"""Decision-maker triage for HeyReach pending leads.

Takes a HeyReach list-pull CSV (from scripts/heyreach_list_pull.py) and judges
each lead against two questions:
  1. Do they fall inside our 9 sub-tiers / ICP (not out-of-line)?
  2. Are they a real decision-maker who could book a demo and drive a purchase?

Reuses tam_builder/aco_persona_rules.py for persona buckets + anti-persona +
CMS-placeholder detection (no new classification logic). Title comes from
`position`; when blank we fall back to `headline`.

Verdicts:
  CUT    — anti-persona (recruiter/GTM/sales/vendor co) or CMS placeholder contact.
  KEEP   — in-tier AND (Buyer or Champion) AND authority HIGH/MED. Can book a demo and/or buy.
  REVIEW — in-tier but Influencer/Gatekeeper, low-authority, unclassified title, or no usable signal.

Usage:
  python3 scripts/triage_pending_leads.py \
      --in fixtures/heyreach_pending_2026-05-22/pending_raw.csv \
      --out fixtures/heyreach_pending_2026-05-22/pending_triaged.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import re  # noqa: E402

from tam_builder.aco_persona_rules import (  # noqa: E402
    classify_persona,
    is_anti_persona,
    is_cms_placeholder_contact,
)

# Supplemental decision-maker patterns the ACO list-build ruleset doesn't cover.
# Checked only when aco classify_persona() returns "unknown". Ordered, most specific first.
# (pattern, bucket, confidence)
SUPPLEMENTAL_RULES: list[tuple[str, str, str]] = [
    # C-suite variants the ACO rule misses (it only matches "chief operating officer").
    (r"chief operations officer|chief administrative officer|"
     r"chief strategy officer|chief growth officer|chief experience officer", "econ_buyer", "H"),
    (r"chief nursing officer|chief nurse executive|chief clinical transformation|"
     r"chief transformation officer|chief quality officer", "clin_champ", "M"),
    # Practice owners / principals = the economic buyer at a small group.
    (r"physician owner|physician/owner|owner/founder|managing partner|"
     r"\bfounder\b|co-?founder|\bowner\b|\bprincipal\b|managing director", "econ_buyer", "H"),
    (r"\bpartner\b", "econ_buyer", "M"),
    # VBC executives missed by the named patterns.
    (r"value[ -]based care executive|value[ -]based care|payor contracting|"
     r"network development|payer contracting", "op_owner", "M"),
    # Practice operational owners who book demos (no health-token, so aco rule misses them).
    (r"office manager|practice manager|clinic manager|center manager|"
     r"general manager|practice administrator", "op_owner", "M"),
    # Standalone clinicians — could be owner/decision-maker at a small group; flag low for review.
    (r"\bphysician\b|family physician|\bhospitalist\b|\bmd\b|\bdo\b|\bdentist\b|"
     r"nurse practitioner|\bpa-c\b|medical practitioner|obesity doctor", "clin_champ", "L"),
    # Generic C-suite catch-all (after the specific clinical chiefs above so they bucket correctly).
    (r"regional chief executive|\bchief executive\b|\bchief of operations\b|"
     r"chief\b.{0,40}\bofficer\b|\bcxo\b", "econ_buyer", "H"),
]
SUPPLEMENTAL_COMPILED = [(re.compile(p, re.IGNORECASE), b, c) for p, b, c in SUPPLEMENTAL_RULES]

# Clearly out-of-scope individual titles -> CUT (not our buyer, not in our 9 sub-tiers).
OUT_OF_SCOPE_TITLE_RE = re.compile(
    r"\bstudent\b|senior at .*univers|\bintern\b|\bprofessor\b|\blecturer\b|"
    r"head coach|fully retired|\bretired\b|cyber ?security|service desk|"
    r"\bit analyst\b|\bmedical assistant\b|aero alliance",
    re.IGNORECASE,
)


def classify_with_supplement(title: str) -> tuple[str, str]:
    bucket, conf = classify_persona(title)
    if bucket != "unknown":
        return bucket, conf
    for rx, b, c in SUPPLEMENTAL_COMPILED:
        if rx.search(title):
            return b, c
    return "unknown", "L"

# bucket -> (buyer_role, purchase_authority, demo_bookable)
BUCKET_ROLE = {
    "econ_buyer": ("Buyer", "Y", "Y"),
    "clin_champ": ("Champion", "partial", "Y"),
    "op_owner": ("Champion", "partial", "Y"),
    "bh_quality": ("Influencer", "N", "Y"),
    "tech_gate": ("Gatekeeper", "N", "partial"),
    "unknown": ("None", "N", "N"),
}

OUT_COLS = [
    "source_campaign", "subtier_assigned", "profileUrl", "name", "title",
    "title_source", "company", "persona_bucket", "buyer_role",
    "authority_grade", "demo_bookable", "purchase_authority",
    "has_photo", "verdict", "reason",
]

# Source list -> subtier (verified 2026-05-22 against HeyReach list names).
LIST_SUBTIER = {
    "OperationalOwner-2A-ACO": "2A",
    "ClinicalChampion-1C-ProvGroup": "1C",
}


def authority_grade(bucket: str, conf: str) -> str:
    if bucket == "econ_buyer":
        return "HIGH" if conf in ("H", "M") else "MED"
    if bucket in ("clin_champ", "op_owner"):
        return {"H": "HIGH", "M": "MED", "L": "LOW"}.get(conf, "LOW")
    if bucket == "bh_quality":
        return "MED" if conf in ("H", "M") else "LOW"
    if bucket == "tech_gate":
        return "LOW"
    return "NONE"


def triage_row(row: dict) -> dict:
    position = (row.get("position") or "").strip()
    headline = (row.get("headline") or "").strip()
    company = (row.get("companyName") or "").strip()
    title = position or headline
    title_source = "position" if position else ("headline" if headline else "none")

    name = f"{(row.get('firstName') or '').strip()} {(row.get('lastName') or '').strip()}".strip()
    subtier = LIST_SUBTIER.get(row.get("source_campaign", ""), "")
    has_photo = row.get("has_photo", "")

    out = {
        "source_campaign": row.get("source_campaign", ""),
        "subtier_assigned": subtier,
        "profileUrl": row.get("profileUrl", ""),
        "name": name,
        "title": title,
        "title_source": title_source,
        "company": company,
        "has_photo": has_photo,
    }

    # 1. Out-of-line cuts (judged on whatever title text we have + company).
    if is_cms_placeholder_contact(title):
        out.update(persona_bucket="placeholder", buyer_role="None",
                   authority_grade="NONE", demo_bookable="N", purchase_authority="N",
                   verdict="CUT", reason="cms_placeholder_contact")
        return out
    if is_anti_persona(title, company):
        out.update(persona_bucket="anti", buyer_role="None",
                   authority_grade="NONE", demo_bookable="N", purchase_authority="N",
                   verdict="CUT", reason="anti_persona")
        return out

    # 2. Classify function/persona (ACO ruleset + supplemental decision-maker patterns).
    bucket, conf = classify_with_supplement(title)
    role, purch, demo = BUCKET_ROLE[bucket]
    grade = authority_grade(bucket, conf)
    out.update(persona_bucket=bucket, buyer_role=role,
               authority_grade=grade, demo_bookable=demo, purchase_authority=purch)

    # 3. Verdict.
    if bucket == "unknown":
        if title_source == "none":
            out.update(verdict="REVIEW", reason="no_title_or_headline")
        else:
            out.update(verdict="REVIEW", reason="unclassified_title")
    elif bucket in ("econ_buyer", "clin_champ", "op_owner") and grade in ("HIGH", "MED"):
        out.update(verdict="KEEP", reason=f"{role.lower()}_{grade.lower()}")
    else:
        # influencer / gatekeeper / low-authority generic director|vp|manager
        out.update(verdict="REVIEW", reason=f"{role.lower()}_or_low_authority")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="in_csv", required=True)
    p.add_argument("--out", dest="out_csv", required=True)
    args = p.parse_args(argv)

    rows = list(csv.DictReader(open(args.in_csv, encoding="utf-8")))
    triaged = [triage_row(r) for r in rows]

    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS)
        w.writeheader()
        w.writerows(triaged)

    verdicts = Counter(r["verdict"] for r in triaged)
    reasons = Counter(r["reason"] for r in triaged)
    roles_keep = Counter(r["buyer_role"] for r in triaged if r["verdict"] == "KEEP")
    sys.stderr.write(f"Triaged {len(triaged)} leads -> {out}\n")
    sys.stderr.write(f"Verdicts: {dict(verdicts)}\n")
    sys.stderr.write(f"KEEP roles: {dict(roles_keep)}\n")
    sys.stderr.write(f"Reasons: {dict(reasons.most_common())}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
