#!/usr/bin/env python3
"""Generate Spider Boolean queries from the canonical 9-subtier × 5-role matrix.

Source of truth: the user's Miro board "Kivira GTM: 9 Subtier Architecture"
(https://miro.com/app/board/uXjVGmT5mbo=/), captured as project memory in
~/spaces/<id>/memory/project_subtier_persona_canonical.md.

This script encodes that matrix in Python and emits a Q-block markdown file
that `scripts/spider_query_runner.py` can consume.

Output: `fixtures/canonical_linkedin_queries.md`

Each cell produces a query like:
  ("title1" OR "title2" OR ...) AND ("anchor1" OR "anchor2")

Skips "Demo stage" priority (BH/Quality Influencer per row 5 of every standard
table) — these are validators after a demo is scheduled, not cold-outbound
targets per the canonical sequencing rules.

2B uses a non-standard role set (vendor-channel: Partnership/Channel Lead,
Product/Clinical Owner, Clinical Champion, Economic Buyer, Technical
Gatekeeper) — handled with its own role data.

Usage:
  python3 scripts/generate_spider_queries.py
  python3 scripts/generate_spider_queries.py --include-demo-stage
  python3 scripts/generate_spider_queries.py --out fixtures/my_queries.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "fixtures" / "canonical_linkedin_queries.md"


# ---------------------------------------------------------------------------
# Canonical subtier data (mirrors project_subtier_persona_canonical.md memory)
# ---------------------------------------------------------------------------

# Subtier anchors — company-side keywords used in the Boolean to constrain
# results to the right subtier of organization. Pick 3-5 terms that are
# discriminative AND likely to appear in a LinkedIn person's current_company
# field or headline.
SUBTIER_ANCHORS: dict[str, list[str]] = {
    "1A": ["medical group", "physicians group", "physician practice", "multi-specialty"],
    "1B": ["primary care", "family practice", "family medicine", "PCP"],
    "1C": ["value-based care", "VBC", "shared savings", "MSSP"],
    "2A": ["ACO", "Accountable Care Organization", "MSSP ACO"],
    "2B": ["Aledade", "Privia Health", "Pearl Health", "Evolent", "agilon health"],
    "2C": ["care management", "chronic care management", "CCM", "remote patient monitoring"],
    "3A": ["health system", "regional health"],
    "3B": ["IDN", "integrated delivery network", "integrated health"],
    "3C": ["Medicare Advantage", "Blue Cross", "health plan", "regional payer"],
}

# Which LinkedIn industry filter to default for each subtier.
SUBTIER_INDUSTRY: dict[str, str] = {
    "1A": "Medical Practice",
    "1B": "Medical Practice",
    "1C": "Medical Practice",
    "2A": "Hospital & Health Care",
    "2B": "Hospital & Health Care",  # Healthcare SaaS companies
    "2C": "Hospital & Health Care",
    "3A": "Hospital & Health Care",
    "3B": "Hospital & Health Care",
    "3C": "Insurance",
}

# Persona roles per subtier. ROW 5 BH/Quality Influencer carries priority
# "Demo stage" — skip in cold-outbound generation by default.
# Each entry: (role_code, role_label, priority, primary_theme, secondary_theme, [title_variants])

STANDARD_SUBTIERS = {
    "1A": [
        ("OO", "Operational Owner", "First", "Workflow / Ops", "ROI / Revenue",
         ["Director of Operations", "VP Operations", "Director of Care Management",
          "Population Health Director", "Director of Clinical Programs",
          "Director of Quality", "VP Clinical Operations"]),
        ("CC", "Clinical Champion", "Second", "Clinical Outcomes", "Quality / Compliance",
         ["CMO", "Chief Medical Officer", "Medical Director", "Primary Care Medical Director",
          "VP Medical Affairs", "Associate Medical Director"]),
        ("EB", "Economic Buyer", "Third", "ROI / Revenue", "Workflow / Ops",
         ["COO", "CEO", "President", "CFO", "Managing Director", "Executive Director", "VP Finance"]),
        ("TG", "Technical Gatekeeper", "Fourth", "Technical / Integration", "Workflow / Ops",
         ["IT Director", "Director of Health IT", "EHR Administrator",
          "Director of Clinical Informatics", "CMIO", "Health IT Manager"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "Clinical Outcomes",
         ["Director of Behavioral Health", "BH Integration Director",
          "Director of Quality Improvement", "VP Quality", "Quality Program Manager",
          "Behavioral Health Program Director"]),
    ],
    "1B": [
        ("OO", "Operational Owner", "First", "Workflow / Ops", "ROI / Revenue",
         ["Practice Administrator", "Office Manager", "Practice Manager",
          "Director of Practice Operations", "Operations Manager", "Clinic Administrator"]),
        ("EB", "Economic Buyer", "First (co-equal)", "ROI / Revenue", "Clinical Outcomes",
         ["Physician Owner", "Managing Partner", "Practice Owner",
          "Founding Physician", "Senior Partner", "Principal Physician"]),
        ("CC", "Clinical Champion", "Second", "Clinical Outcomes", "Workflow / Ops",
         ["Medical Director", "Lead Physician", "Behavioral Health Champion",
          "Clinical Director", "Chief of Medicine", "Supervising Physician"]),
        ("TG", "Technical Gatekeeper", "Third", "Technical / Integration", "Workflow / Ops",
         ["EHR Administrator", "IT Manager", "Operations Lead",
          "EHR Coordinator", "Practice Technology Lead"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "Clinical Outcomes",
         ["Behavioral Health Director", "Quality Improvement Lead",
          "BH Program Coordinator", "Clinical Quality Manager", "BH Integration Lead"]),
    ],
    "1C": [
        ("OO", "Operational Owner", "First", "Quality / Compliance", "Workflow / Ops",
         ["VP Population Health", "Director of Population Health", "Director of Care Management",
          "Director of Quality", "Director of Risk Adjustment", "Care Transformation Lead",
          "Director of Value-Based Programs"]),
        ("CC", "Clinical Champion", "First (co-equal)", "Clinical Outcomes", "Quality / Compliance",
         ["CMO", "VP Medical Affairs", "Medical Director of Population Health",
          "VP Medical Director Value-Based Care", "Chief Clinical Officer",
          "Medical Director Quality Programs"]),
        ("EB", "Economic Buyer", "Second", "ROI / Revenue", "Quality / Compliance",
         ["VP Value-Based Care", "CFO", "COO", "President", "VP Finance",
          "VP Revenue Cycle", "Chief Strategy Officer"]),
        ("TG", "Technical Gatekeeper", "Third", "Technical / Integration", "Workflow / Ops",
         ["Analytics Director", "VP Analytics", "IT/EHR Lead", "Interoperability Lead",
          "Director of Clinical Informatics", "Director of Health Information Exchange"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "Clinical Outcomes",
         ["Director of Behavioral Health Integration", "VP Quality Performance",
          "BH Program Director", "Quality Improvement Director", "Director of Clinical Quality"]),
    ],
    "2A": [
        ("OO", "Operational Owner", "First", "Quality / Compliance", "ROI / Revenue",
         ["VP Population Health", "Director of Population Health", "Director of Care Coordination",
          "Quality Director", "Director of Network Performance", "Risk Operations Leader",
          "Director of Value-Based Operations"]),
        ("CC", "Clinical Champion", "First (co-equal)", "Clinical Outcomes", "Quality / Compliance",
         ["CMO", "VP Medical Affairs", "Medical Director Population Health",
          "Physician Executive VBC", "Chief Clinical Officer",
          "Medical Director Quality", "VP Clinical Affairs"]),
        ("EB", "Economic Buyer", "Second", "ROI / Revenue", "Quality / Compliance",
         ["CEO", "President", "CFO", "VP Network Performance",
          "SVP Clinical Affairs", "Executive Director"]),
        ("TG", "Technical Gatekeeper", "Third", "Technical / Integration", "Quality / Compliance",
         ["Director of Analytics", "VP Data & Analytics", "Interoperability Lead",
          "Director of Reporting", "Health IT Director", "Director of Clinical Analytics"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "ROI / Revenue",
         ["Director of Behavioral Health Programs", "VP Quality Operations",
          "Director of Quality Improvement", "Quality Performance Director",
          "Director of Clinical Quality Programs"]),
    ],
    "2C": [
        ("OO", "Operational Owner", "First", "Workflow / Ops", "Clinical Outcomes",
         ["VP Clinical Operations", "Director of Care Management", "Director of Care Navigation",
          "Director of Clinical Programs", "Director of Behavioral Health",
          "Director of Patient Engagement", "VP Care Delivery"]),
        ("EB", "Economic Buyer", "Second", "ROI / Revenue", "Workflow / Ops",
         ["CEO", "GM", "President", "VP Operations", "COO", "Executive Director", "CFO"]),
        ("CC", "Clinical Champion", "Second (co-equal)", "Clinical Outcomes", "Workflow / Ops",
         ["Medical Director", "VP Clinical Programs", "Chief Clinical Officer",
          "Clinical Director", "VP Medical Affairs", "Chief Nursing Officer"]),
        ("TG", "Technical Gatekeeper", "Third", "Technical / Integration", "Workflow / Ops",
         ["VP Product", "IT Director", "Director of Integrations",
          "VP Technology", "CTO", "Director of Clinical Systems"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Clinical Outcomes", "Quality / Compliance",
         ["BH Program Director", "Director of Clinical Supervision",
          "VP Behavioral Health Services", "Clinical Supervisor",
          "Director of BH Integration", "BH Quality Director"]),
    ],
    "3A": [
        ("OO", "Operational Owner", "First", "Workflow / Ops", "ROI / Revenue",
         ["VP Ambulatory", "VP Population Health", "Director of Ambulatory Operations",
          "Director of Care Management", "VP Primary Care Service Line",
          "VP Clinical Transformation", "Director of Ambulatory Strategy"]),
        ("CC", "Clinical Champion", "First (co-equal)", "Clinical Outcomes", "Quality / Compliance",
         ["CMO", "Chief Medical Officer", "VP Medical Affairs",
          "Behavioral Health Service Line Medical Director",
          "Primary Care Medical Executive", "VP Medical Operations", "Associate CMO Ambulatory"]),
        ("TG", "Technical Gatekeeper", "Second", "Technical / Integration", "Workflow / Ops",
         ["CMIO", "CIO", "VP Clinical Informatics", "Director of EHR Applications",
          "VP Interoperability", "Digital Health Director", "Director of Clinical Systems"]),
        # 3A_EB: do NOT cold-outreach CEO — exclude CEO/President from the title list.
        ("EB", "Economic Buyer", "Third", "ROI / Revenue", "Workflow / Ops",
         ["VP Ambulatory", "COO", "CFO", "SVP Clinical Affairs",
          "VP Finance", "SVP Operations"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "Clinical Outcomes",
         ["Service Line Director Behavioral Health", "VP Behavioral Health Services",
          "Director of Ambulatory BH", "Director of Behavioral Health Integration",
          "Director of Psychiatry Service Line", "BH Service Line Medical Director"]),
    ],
    "3B": [
        ("OO", "Operational Owner", "First", "Workflow / Ops", "Quality / Compliance",
         ["VP Population Health", "VP Care Transformation", "Director of Care Transformation",
          "Enterprise Care Management Director", "Director of Ambulatory Strategy",
          "VP Ambulatory Operations"]),
        ("CC", "Clinical Champion", "First (co-equal)", "Clinical Outcomes", "Workflow / Ops",
         ["CMO", "CMIO", "VP Medical Affairs", "Enterprise Physician Executive",
          "VP Ambulatory Strategy", "Chief Clinical Officer", "Associate CMO Population Health"]),
        ("TG", "Technical Gatekeeper", "Second", "Technical / Integration", "Workflow / Ops",
         ["CMIO", "VP Enterprise Applications", "VP Interoperability",
          "Digital Health Officer", "Director of Clinical Systems", "VP Health IT",
          "Director of Enterprise Architecture"]),
        # 3B_EB: do NOT cold-approach system CEO — exclude CEO/President from the title list.
        ("EB", "Economic Buyer", "Third", "ROI / Revenue", "Workflow / Ops",
         ["SVP Enterprise Operations", "VP Care Transformation", "VP Population Health",
          "SVP Strategy", "CFO", "COO"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "Clinical Outcomes",
         ["VP Behavioral Health Services", "Enterprise BH Director",
          "Director of Behavioral Health Strategy", "Director of Enterprise BH Integration",
          "SVP Behavioral Health", "System Director of Psychiatry"]),
    ],
    "3C": [
        ("OO", "Operational Owner", "First", "Quality / Compliance", "ROI / Revenue",
         ["VP Medical Management", "VP Quality", "Director of Quality",
          "Director of Behavioral Health Programs", "VP Stars",
          "Director of Risk Adjustment", "Director of Care Management", "VP Clinical Operations"]),
        ("CC", "Clinical Champion", "First (co-equal)", "Clinical Outcomes", "Quality / Compliance",
         ["CMO", "Chief Medical Officer", "VP Clinical Affairs",
          "Behavioral Health Medical Director", "Population Health Medical Director",
          "VP Medical Director", "Chief Behavioral Health Officer"]),
        ("EB", "Economic Buyer", "Second", "ROI / Revenue", "Quality / Compliance",
         ["CFO", "VP Medical Management", "VP Stars Performance", "COO",
          "VP Finance", "Chief Strategy Officer", "SVP Health Plan Operations"]),
        ("TG", "Technical Gatekeeper", "Third", "Technical / Integration", "Quality / Compliance",
         ["VP Data & Analytics", "Director of Clinical Analytics", "VP Interoperability",
          "Product/Program Operations Director", "Director of Health Informatics",
          "Director of Data Science"]),
        ("BH", "BH / Quality Influencer", "Demo stage", "Quality / Compliance", "ROI / Revenue",
         ["VP Stars Performance", "Director of HEDIS", "BH Network Director",
          "VP Behavioral Health Network", "Stars Program Director",
          "Director of Quality Measurement", "Director of BH Quality Improvement"]),
    ],
}

# 2B uses a NON-standard role set (vendor-channel buying dynamic, not internal
# buying committee). Title clusters reflect partner/product roles at companies
# like Aledade, Privia, Pearl Health, Evolent.
SUBTIER_2B = [
    ("PCL", "Partnership / Channel Lead", "First", "ROI / Revenue", "Workflow / Ops",
     ["VP Partnerships", "VP Business Development", "VP Strategic Alliances",
      "Director of Partnerships", "GM Provider Solutions",
      "Head of Partnerships", "SVP Business Development"]),
    ("PCO", "Product / Clinical Owner", "First (co-equal)", "Workflow / Ops", "Clinical Outcomes",
     ["VP Product", "VP Clinical Programs", "Chief Product Officer",
      "Director of Product Management", "VP Product Strategy",
      "Head of Product", "SVP Product"]),
    ("CC", "Clinical Champion", "Second", "Clinical Outcomes", "Workflow / Ops",
     ["CMO", "VP Clinical Strategy", "Medical Director", "VP Clinical Operations",
      "Chief Clinical Officer", "SVP Clinical"]),
    ("EB", "Economic Buyer", "Third", "ROI / Revenue", "Workflow / Ops",
     ["CEO", "GM", "COO", "VP Revenue", "Chief Revenue Officer", "President", "CFO"]),
    ("TG", "Technical Gatekeeper", "Third (co-equal)", "Technical / Integration", "Workflow / Ops",
     ["CTO", "VP Engineering", "VP Integrations", "Director of Platform Engineering",
      "VP Technology", "Head of Engineering"]),
]


# Priority sort order — lowest = run first.
PRIORITY_ORDER = {
    "First": 1,
    "First (co-equal)": 2,
    "Second": 3,
    "Second (co-equal)": 4,
    "Third": 5,
    "Third (co-equal)": 6,
    "Fourth": 7,
    "Demo stage": 99,
}


# ---------------------------------------------------------------------------
# Boolean assembly
# ---------------------------------------------------------------------------


def boolean_query(titles: list[str], anchors: list[str]) -> str:
    titles_part = " OR ".join(f'"{t}"' for t in titles)
    anchors_part = " OR ".join(f'"{a}"' for a in anchors)
    return f"({titles_part}) AND ({anchors_part})"


def build_cells(include_demo_stage: bool):
    """Yield (qid, subtier, role_code, role_label, priority, primary, secondary, titles, anchors, industry)."""
    for subtier, roles in STANDARD_SUBTIERS.items():
        for role_code, role_label, priority, primary, secondary, titles in roles:
            if priority == "Demo stage" and not include_demo_stage:
                continue
            yield (
                f"Q{subtier}-{role_code}",
                subtier,
                role_code,
                role_label,
                priority,
                primary,
                secondary,
                titles,
                SUBTIER_ANCHORS[subtier],
                SUBTIER_INDUSTRY[subtier],
            )
    # 2B special case
    for role_code, role_label, priority, primary, secondary, titles in SUBTIER_2B:
        if priority == "Demo stage" and not include_demo_stage:
            continue
        yield (
            f"Q2B-{role_code}",
            "2B",
            role_code,
            role_label,
            priority,
            primary,
            secondary,
            titles,
            SUBTIER_ANCHORS["2B"],
            SUBTIER_INDUSTRY["2B"],
        )


def emit_q_block(
    qid: str,
    subtier: str,
    role_code: str,
    role_label: str,
    priority: str,
    primary: str,
    secondary: str,
    boolean: str,
    industry: str,
) -> str:
    return (
        f"### {qid} — {subtier} | {role_label}\n"
        f"- **Cluster:** {role_code} ({role_label})\n"
        f"- **Boolean:** {boolean}\n"
        f"- **Industry filter:** {industry}\n"
        f"- **Location:** United States\n"
        f"- **Expected subtiers:** {subtier}\n"
        f"- **Why this slot:** {priority} priority — primary theme {primary}, secondary {secondary}\n\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument(
        "--include-demo-stage",
        action="store_true",
        help="Also emit BH/Quality 'Demo stage' queries (skipped by default — they're validators, not cold-outbound).",
    )
    args = p.parse_args(argv)

    cells = list(build_cells(include_demo_stage=args.include_demo_stage))
    # Sort by (priority_order, subtier code) for ergonomic top-down execution
    cells.sort(key=lambda c: (PRIORITY_ORDER.get(c[4], 999), c[1]))

    lines: list[str] = []
    lines.append("# Canonical LinkedIn Spider Queries — auto-generated from 9-subtier × 5-role matrix\n")
    lines.append("Source: scripts/generate_spider_queries.py (do not hand-edit — re-run the generator)\n")
    lines.append(f"Total cells: {len(cells)}\n")
    lines.append("Sorted by priority (First → First co-equal → Second → ...), then subtier code.\n\n")
    lines.append("---\n\n")

    for cell in cells:
        qid, subtier, role_code, role_label, priority, primary, secondary, titles, anchors, industry = cell
        boolean = boolean_query(titles, anchors)
        lines.append(emit_q_block(qid, subtier, role_code, role_label, priority, primary, secondary, boolean, industry))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines), encoding="utf-8")

    # Stats
    by_priority: dict[str, int] = {}
    for c in cells:
        by_priority[c[4]] = by_priority.get(c[4], 0) + 1
    print(f"Wrote {len(cells)} queries to {out_path.relative_to(REPO_ROOT)}")
    print("Priority distribution:")
    for pri, count in sorted(by_priority.items(), key=lambda x: PRIORITY_ORDER.get(x[0], 999)):
        print(f"  {pri}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
