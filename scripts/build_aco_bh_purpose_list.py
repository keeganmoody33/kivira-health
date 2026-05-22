#!/usr/bin/env python3
"""Rank the 340-row 2A ACO list by behavioral-health-purpose evidence.

CMS Contact Title is the generic "ACO Executive (per CMS public filing)" placeholder
for nearly every row, so this script scores against the Spider snippet text (LinkedIn
profile description) instead of CMS title. BH keyword patterns reuse
tam_builder/persona_rules.py::_BH_QUALITY_HARD and the clinical-champion BH lines.

Inputs:
  --leads     fixtures/heyreach_loads/heyreach_leads_2a.json
  --cms       fixtures/wave1_raw_accounts.csv
  --snippets  fixtures/wave1_runs/20260502T000500Z_smoke2/Q2A_progress.jsonl
  --out       fixtures/aco_bh_purpose_ranked.csv

Output columns:
  rank, score, firstName, lastName, companyName, profileUrl, cms_title,
  spider_page_title, snippet, persona_bucket, signal_tags, evidence_quote
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path


# ---------- Keyword libraries ----------

# Reused (verbatim) from tam_builder/persona_rules.py::_BH_QUALITY_HARD (lines 177-194)
BH_QUALITY_HARD = (
    "director of behavioral health",
    "vp behavioral health",
    "behavioral health director",
    "bh program director",
    "behavioral health program director",
    "director of bh integration",
    "director of behavioral health integration",
    "behavioral health quality",
    "director of quality measurement",
    "director of hedis",
    "stars program director",
    "vp stars performance",
    "director of quality improvement",
    "quality performance director",
    "director of clinical quality programs",
    "director of bh quality",
)

# Reused from persona_rules.py::_CLINICAL_CHAMPION_HARD (BH-relevant entries only)
CLINICAL_CHAMPION_BH = (
    "behavioral health medical director",
    "chief behavioral health officer",
)

# Phase C bio-mining signals. Each entry is (regex_pattern, signal_tag).
# Short tokens (nami, afsp, etc) require word boundaries to avoid matches
# inside larger words like "dyNAMIc" or "VietNAM".
BIO_SIGNALS = [
    (r"\bnami\b", "advocacy_nami"),
    (r"\bafsp\b", "advocacy_afsp"),
    (r"\bsamhsa\b", "samhsa_affiliation"),
    (r"\bbhi\b", "bhi_billing"),
    (r"\bcocm\b", "cocm_published"),
    (r"\bmat (clinic|program|provider|services|therapy)\b", "prior_role_mat"),
    (r"\bopioid\b", "topic_opioid"),
    (r"collaborative care", "cocm_published"),
    (r"behavioral health integration", "bhi_published"),
    (r"community mental health", "prior_role_cmh"),
    (r"mental health center", "prior_role_cmh"),
    (r"psychiatric hospital", "prior_role_psych_hosp"),
    (r"addiction treatment", "prior_role_addiction"),
    (r"medication-assisted treatment", "prior_role_mat"),
    (r"depression screening", "publication_depression"),
    (r"suicide prevention", "publication_suicide"),
    (r"opioid use disorder", "publication_oud"),
    (r"primary care psychiatry", "specialty_pcp_psych"),
    (r"behavioral health", "general_bh_role"),
    (r"mental health", "general_mh_role"),
    (r"\bpsychiatric\b", "general_psych"),
    (r"\bpsychiatry\b", "general_psych"),
    (r"\bpsychiatrist\b", "general_psych"),
    (r"\bpsychology\b", "general_psych"),
    (r"\bpsychologist\b", "general_psych"),
    (r"\bdepression\b", "topic_depression"),
    (r"\banxiety\b", "topic_anxiety"),
    (r"\bphq-9\b", "tool_phq9"),
    (r"\bgad-7\b", "tool_gad7"),
    # integrated_care is intentionally LAST and only triggers if the snippet
    # contains a behavior/action verb near it (not just a company name).
    (r"(advancing|implementing|expanding|driving|leading|building) integrated care",
     "integrated_care_active"),
]

# Persona bucket inference from snippet text
PERSONA_PATTERNS = {
    "clin_champ": (
        "medical director", "cmo", "chief medical", "physician executive",
        "chief clinical", "vp medical", "vp clinical affairs",
    ),
    "op_owner": (
        "vp population health", "director of population health",
        "director of care coordination", "quality director",
        "director of network performance", "director of value-based",
        "director of value based", "care manager", "director of operations",
    ),
    "econ_buyer": (
        "ceo ", "chief executive", "president ", "cfo ", "chief financial",
        "coo ", "chief operating", "executive director",
    ),
    "tech_gate": (
        "cio ", "chief information", "director of analytics", "vp data",
        "interoperability", "health it",
    ),
    "bh_quality": (
        "behavioral health", "mental health", "psychiatric", "quality",
        "hedis", "stars",
    ),
}


# ---------- Helpers ----------

def normalize_url(url: str) -> str:
    if not url:
        return ""
    return url.rstrip("/").lower()


def normalize_company(name: str) -> str:
    if not name:
        return ""
    n = name.lower().strip()
    for suffix in (", llc", ", llc.", ", l.l.c.", ", inc.", ", inc", ", l.p.",
                   ", lp", ", pa", ", p.a.", ", pllc", ", p.c.", " llc.", " llc",
                   " inc.", " inc", "."):
        if n.endswith(suffix):
            n = n[: -len(suffix)].strip()
    n = re.sub(r"\s+", " ", n)
    return n


def normalize_name(first: str, last: str) -> str:
    return f"{(first or '').strip().lower()} {(last or '').strip().lower()}".strip()


def find_persona_bucket(text: str) -> str:
    t = text.lower()
    # Priority order: clinical champion > op owner > bh/quality > econ buyer > tech gate
    for bucket in ("clin_champ", "op_owner", "bh_quality", "econ_buyer", "tech_gate"):
        for pattern in PERSONA_PATTERNS[bucket]:
            if pattern in t:
                return bucket
    return "unknown"


def score_bh(text: str):
    """Return (total_score, signal_tags_set, evidence_quotes_list)."""
    t = text.lower()
    score = 0
    tags = set()
    quotes = []

    # Hard-BH title hits (high signal, +8 each)
    for kw in BH_QUALITY_HARD + CLINICAL_CHAMPION_BH:
        if kw in t:
            score += 8
            tags.add(f"hard_title:{kw.replace(' ', '_')}")
            # Capture a +/- 60 char window for evidence
            idx = t.find(kw)
            quotes.append(text[max(0, idx - 40): idx + len(kw) + 60])

    # Bio-signal matches (+2 each, distinct signal_tags only)
    for pattern, tag in BIO_SIGNALS:
        if tag in tags:
            continue
        m = re.search(pattern, t)
        if m:
            score += 2
            tags.add(tag)
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 60)
            quotes.append(text[start:end])

    return score, tags, quotes


# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads", required=True)
    ap.add_argument("--cms", required=True)
    ap.add_argument("--snippets", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # Load the 340-row seed
    with open(args.leads) as f:
        leads = json.load(f)
    print(f"[leads]    {len(leads)} rows", file=sys.stderr)

    # Index leads by normalized profileUrl for fast lookup
    leads_by_url = {normalize_url(ld["profileUrl"]): ld for ld in leads}

    # Index CMS by (name, normalized_company) -> Contact Title
    cms_by_key = {}
    with open(args.cms, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "2A" not in (row.get("Internal Notes") or ""):
                continue
            full_name = (row.get("Contact Name") or "").strip()
            if not full_name:
                continue
            parts = full_name.split()
            if len(parts) < 2:
                continue
            first = parts[0]
            last = parts[-1]
            org_key = normalize_company(row.get("Organization Name") or "")
            cms_by_key[(normalize_name(first, last), org_key)] = {
                "title": (row.get("Contact Title") or "").strip(),
                "email": (row.get("Contact Email") or "").strip(),
                "state": (row.get("State Code") or "").strip(),
            }
    print(f"[cms 2A]   {len(cms_by_key)} unique (name, org) keys", file=sys.stderr)

    # Index snippets by profile URL
    snippet_by_url = {}
    with open(args.snippets) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            for hit in rec.get("hits") or []:
                url = normalize_url(hit.get("linkedin_profile_url") or "")
                if not url:
                    continue
                if url not in snippet_by_url:
                    snippet_by_url[url] = {
                        "page_title": hit.get("title") or "",
                        "snippet": hit.get("snippet") or "",
                        "query_org": rec.get("org") or "",
                        "query_contact": rec.get("contact_name") or "",
                        "query_state": rec.get("state") or "",
                    }
    print(f"[snippets] {len(snippet_by_url)} URL→snippet entries", file=sys.stderr)

    # Score each lead
    scored = []
    matched_snippets = 0
    for ld in leads:
        url = ld["profileUrl"]
        first = ld.get("firstName") or ""
        last = ld.get("lastName") or ""
        company = ld.get("companyName") or ""

        cms = cms_by_key.get((normalize_name(first, last), normalize_company(company))) or {}
        sn = snippet_by_url.get(normalize_url(url)) or {}
        if sn:
            matched_snippets += 1

        # Compose the text we score against: page title + snippet (CMS title is usually generic)
        scoring_text = " || ".join(filter(None, [
            sn.get("page_title", ""),
            sn.get("snippet", ""),
            cms.get("title", ""),  # included on the off-chance it has real content
        ]))

        score, tags, quotes = score_bh(scoring_text)
        persona = find_persona_bucket(scoring_text)

        scored.append({
            "score": score,
            "firstName": first,
            "lastName": last,
            "companyName": company,
            "profileUrl": url,
            "cms_title": cms.get("title", ""),
            "spider_page_title": sn.get("page_title", ""),
            "snippet": sn.get("snippet", ""),
            "persona_bucket": persona,
            "signal_tags": "; ".join(sorted(tags)),
            "evidence_quote": " | ".join(q.strip() for q in quotes[:3]),
        })

    # Sort descending by score, then alpha by lastName for stable ties
    scored.sort(key=lambda r: (-r["score"], r["lastName"].lower()))

    # Write CSV
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank", "score", "firstName", "lastName", "companyName",
            "profileUrl", "cms_title", "spider_page_title", "snippet",
            "persona_bucket", "signal_tags", "evidence_quote",
        ])
        writer.writeheader()
        for i, row in enumerate(scored, 1):
            row["rank"] = i
            writer.writerow(row)

    # Surface diagnostics
    nonzero = [r for r in scored if r["score"] > 0]
    high = [r for r in scored if r["score"] >= 6]
    print(f"[matched]  {matched_snippets}/{len(leads)} leads got a Spider snippet", file=sys.stderr)
    print(f"[scored]   {len(scored)} total", file=sys.stderr)
    print(f"[scored]   {len(nonzero)} with any BH signal", file=sys.stderr)
    print(f"[scored]   {len(high)} with score >= 6 (A-list)", file=sys.stderr)
    print(f"[scored]   {len([r for r in scored if 4 <= r['score'] < 6])} with score 4-5 (B-list)", file=sys.stderr)
    print(f"[wrote]    {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
