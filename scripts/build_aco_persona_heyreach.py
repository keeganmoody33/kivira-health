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


# Persona bucket patterns. Match on lowercased title. Order matters: most
# specific/highest-value buckets first so a "VP Pop Health" title doesn't
# get caught by the generic "VP" pattern.
PERSONA_RULES = [
    # (regex, bucket, confidence). Patterns match against title+snippet
    # lowercased. Order matters: most specific first. Spider page titles
    # frequently truncate at ~60 chars (e.g. "Administrative Director of
    # Behavioral ..." cuts before "Health"), so patterns are also tolerant
    # of partial phrases.

    # BH/Quality Influencer
    (r"chief behavioral health officer|behavioral health medical director", "clin_champ", "H"),
    (r"director of behavioral health|director of bh|vp behavioral health|"
     r"behavioral health director|director, behavioral health", "bh_quality", "H"),
    (r"(?:director|administrator|administrative director|regional director|"
     r"clinical director|program director).*\bbehavioral\b", "bh_quality", "M"),
    (r"\bbh integration\b|bh program", "bh_quality", "M"),

    # Clinical Champion
    (r"\bcmo\b|chief medical officer|chief clinical officer", "clin_champ", "H"),
    (r"medical director.*population health|population health.*medical director", "clin_champ", "H"),
    (r"medical director.*(?:quality|value[ -]based|aco)", "clin_champ", "H"),
    (r"physician executive|vp medical|vp clinical|chief physician", "clin_champ", "M"),
    (r"director.*clinical (?:initiatives|programs|integration|operations|quality)", "clin_champ", "M"),
    (r"medical director", "clin_champ", "M"),

    # Operational Owner — pop health / care coordination / value-based ops
    (r"vp population health|vice president[, ]+population health|"
     r"svp population health", "op_owner", "H"),
    (r"(?:executive |senior |regional |sr\.? )?director[, ]+population health|"
     r"director of population health|director.*\bpopulation health\b", "op_owner", "H"),
    (r"director of care coordination|director of value[ -]based|"
     r"vp value[ -]based|vp care management", "op_owner", "H"),
    (r"director of network performance|risk operations leader|"
     r"director of aco|aco.*operations", "op_owner", "M"),
    (r"director,? care management|director of programs|"
     r"director of operations", "op_owner", "M"),

    # BH/Quality Influencer — pure quality role
    (r"vp quality|director of quality (?:improvement|measurement|programs|operations)|"
     r"quality performance director|stars program director|"
     r"director,? hedis|hedis director", "bh_quality", "M"),

    # Economic Buyer
    (r"chief executive officer|\bceo\b|^president\b|\bpresident\b at |"
     r"\bsvp\b.*(?:clinical|medical)", "econ_buyer", "H"),
    (r"chief financial officer|\bcfo\b", "econ_buyer", "H"),
    (r"chief operating officer|\bcoo\b", "econ_buyer", "M"),
    (r"executive director", "econ_buyer", "M"),
    (r"president\b", "econ_buyer", "M"),

    # Technical Gatekeeper
    (r"chief medical information officer|\bcmio\b", "tech_gate", "H"),
    (r"\bcio\b|chief information officer|chief technology officer|\bcto\b", "tech_gate", "H"),
    (r"director of analytics|vp data|interoperability|"
     r"director.*analytics", "tech_gate", "M"),
    (r"health it director|director of clinical analytics", "tech_gate", "M"),

    # Snippet-side patterns. Many Spider titles collapse to "<Company> |
    # LinkedIn" with the actual role only in the snippet. These rules match
    # role-indicator phrases that frequently appear in LinkedIn About/headline
    # snippets even when the title is uninformative.
    (r"chief population health officer", "econ_buyer", "H"),
    (r"physician.*(?:population health|value[ -]based|aco|quality)", "clin_champ", "M"),
    (r"population health (?:manager|specialist|coordinator|analyst|"
     r"administrator|consultant|lead)", "op_owner", "M"),
    (r"(?:value[ -]based|vbc).*(?:director|manager|leader|lead|administrator)", "op_owner", "M"),
    (r"aco (?:practice engagement|engagement|operations|administrator|"
     r"administration|manager|coordinator|specialist|analyst|lead)", "op_owner", "M"),
    (r"care management.*(?:director|manager|administrator)|"
     r"director.*care management", "op_owner", "M"),
    (r"quality (?:improvement|measurement|management|analyst|specialist).*"
     r"(?:lead|coordinator|manager|administrator)", "bh_quality", "M"),

    # Fallback: any "director", "vp", or visible "manager/administrator" we
    # couldn't classify — likely mid-level operator. Confidence L; user
    # should manually verify before sending.
    (r"\bvp\b|vice president", "op_owner", "L"),
    (r"\bdirector\b", "op_owner", "L"),
    (r"\bmanager\b.*(?:health|care|quality|operations|practice)|"
     r"(?:health|care|quality|operations|practice).*\bmanager\b", "op_owner", "L"),
    (r"\badministrator\b.*(?:health|care|quality|operations|practice|aco)|"
     r"(?:health|care|quality|operations|practice|aco).*\badministrator\b", "op_owner", "L"),
]

# US state names + abbreviations — when an ACO's brand token is just a state,
# the match is much more likely to be a cross-org collision (different org in
# the same state). These get pushed to Tier C by the tiering rule.
US_STATE_TOKENS = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada", "hampshire",
    "jersey", "mexico", "york", "carolina", "dakota", "ohio", "oklahoma",
    "oregon", "pennsylvania", "rhode", "tennessee", "texas", "utah",
    "vermont", "virginia", "washington", "wisconsin", "wyoming",
}

# Generic healthcare tokens — mirrors spider_account_search.py BH_GENERIC.
# Used here to identify the org brand token for ranking & for state-only
# detection in the tier rule.
GENERIC_ORG_TOKENS = {
    "health", "healthcare", "care", "medical", "medicine", "clinical",
    "services", "service", "partners", "partner", "network", "networks",
    "associates", "association", "physicians", "physician", "hospital",
    "hospitals", "clinic", "clinics", "consultation", "management",
    "solutions", "coalition", "accountable", "organization", "professional",
    "group", "alliance", "system", "systems", "wellness", "primary",
    "community", "regional", "national", "integrated", "advanced",
    "premier", "select", "performance", "aco", "llc", "inc", "the",
    "and", "of", "co", "corp", "corporation", "company", "or", "ltd",
    "pa", "pc", "llp", "mssp", "for",
}


def tokenize_org(name: str) -> list[str]:
    raw = re.findall(r"[a-z]+", (name or "").lower())
    return [t for t in raw if len(t) >= 3 and t not in GENERIC_ORG_TOKENS]


def brand_token(org_name: str) -> str | None:
    toks = sorted(tokenize_org(org_name), key=len, reverse=True)
    return toks[0] if toks else None


def classify_persona(title: str, snippet: str) -> tuple[str, str]:
    """Return (persona_bucket, confidence) by matching title+snippet against
    PERSONA_RULES. First match wins (rules ordered by specificity).
    """
    blob = f"{title} {snippet}".lower()
    for pattern, bucket, conf in PERSONA_RULES:
        if re.search(pattern, blob):
            return bucket, conf
    return "unknown", "L"


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
            "_brand_is_state_only": (brand_token(company) or "") in US_STATE_TOKENS,
        })

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
