---
source_path: "/Users/keeganmoody/Downloads/Kivira docs/kivira deployment guide.pdf"
ingested_at: 2026-04-06
source_type: pdf
status: canonical-markdown-ingest
note: "Extracted with PDFKit into markdown summary. This file is the repo-local canonical ingest for the deployment guide."
---

# Kivira CoCM Estimate Engine Deployment Guide

## Purpose

This internal guide explains how the CoCM estimate workflow should be run, how accounts should be classified, how account tiers should be interpreted, and how buyer/persona routing should change by org type.

## Core workflow

### Prerequisites

- Python 3.10+
- `requests`
- A local script file
- Internet access for public CMS and NPPES APIs
- An account list that can be converted into `ACCOUNT_PROFILES`

### CLI examples

Single account:

```bash
python3 kivira_cocm_estimate_v2.py \
  --org-name "Banner Medical Group" \
  --state AZ \
  --city Phoenix \
  --org-type health_system_medical_group \
  --json --csv \
  --output-dir ./output
```

Batch run:

```bash
python3 kivira_cocm_estimate_v2.py --batch --json --csv --output-dir ./output
```

### Output contract

Per account, the guide expects:

- `*_estimate.json`
- `*_estimate.csv`
- `*_provider_debug.csv`

The JSON is positioned as CRM/import-friendly structured data. The CSV is a one-row summary. The provider debug CSV is for analysts and validation.

## Account profile schema

Each account profile is expected to contain:

```json
{
  "org_name": "Exact name as it would appear in NPPES",
  "state": "Two-letter code",
  "city": "Primary city or None for statewide",
  "org_type": "one of the four guide-defined types",
  "priority_personas": ["who you want messages for"],
  "max_candidates": 150,
  "notes": ["internal notes for your team"]
}
```

### Org types

- `solo_practice`
- `independent_group`
- `health_system_medical_group`
- `aco_parent`

### Max candidate guidance

- Solo / small: `20-50`
- Medium group: `80-150`
- Large system / ACO: `150-300`

## Tiering logic

### Tier 1

- Confidence grade `A` or `B`
- Base gap `> $75K`
- High-confidence clinicians `>= 10`

Interpretation: strong signal, large opportunity, trustworthy attribution.

### Tier 2

- Confidence grade `B` or `C`
- Base gap `$25K-$75K`
- High-confidence clinicians `>= 5`

Interpretation: real signal but needs validation or has a smaller footprint.

### Tier 3

- Confidence grade `C`
- Base gap `$10K-$25K`

Interpretation: directional only; nurture rather than direct outreach.

### Tier 4

- Confidence grade `D`, or
- Base gap `< $10K`

Interpretation: do not outbound on public signal alone.

### Spreadsheet score

```text
SCORE = (base_gap / 1000) + (high_confidence_clinicians * 5) + (g0444_benes * 0.5)
```

## Confidence grade usage

- Grade `A`: strong attribution + solid screening signal; lead confidently with numbers plus caveats.
- Grade `B`: decent attribution + real screening activity; lead with workflow story and use numbers as support.
- Grade `C`: category signal exists, but do not lead with specific numbers in email.
- Grade `D`: public signal is too thin; qualify via other channels first.

## Buyer mapping by org type

### Solo / small independent practice

- Primary buyer: PCP owner / founding clinician
- Secondary: practice administrator / office manager
- Message: lead with workflow, not revenue
- Script personas: `pcp` primary, `cfo` only if they ask about money

### Medium independent group

- Primary: medical director
- Secondary: practice administrator / COO
- Tertiary: managing partner / lead physician
- Script personas: `medical_director` primary, `cfo` for admin/COO

### Large PCP medical group / health system

- Primary: VP Primary Care / medical director / service line leader
- Secondary: CFO / VP Revenue Cycle / COO
- Third: CMIO / VP Clinical Informatics / CIO
- Fourth: CMO / Chief Quality Officer
- Fifth: BH Integration Director / VP Behavioral Health
- Script personas: `medical_director`, `cfo`, `cmio`

### ACO / IPA / VBC parent org

- Primary: VP Population Health / director of care management / VP Quality
- Secondary: VP Clinical Transformation / director of practice transformation
- Third: CFO / VP Strategy / VP Finance
- Fourth: network medical director
- Script personas: `pop_health` primary, `cfo` supporting, `bh_ops` when BH integration exists

## Persona title mapping

- `pcp`: PCP owner, founding clinician, lead physician, NP/PA owner
- `medical_director`: medical director, VP primary care, service line leader, managing partner
- `cfo`: CFO, COO, VP revenue cycle, practice administrator, VP finance
- `cmio`: CMIO, VP clinical informatics, CIO secondary
- `pop_health`: VP population health, VP quality, director of care management, VP clinical transformation
- `bh_ops`: BH integration director, VP behavioral health, BH-focused care management leader

## Outreach sequencing

### Tier 1

1. Week 1: send `medical_director` or `pop_health` discovery-first outreach.
2. Week 2: if clinical interest appears, send `cfo` message with range + caveats.
3. Week 3: if clinical + finance both engage, send `cmio` message and implementation case.

### Tier 2

1. Week 1: send only the `medical_director` message.
2. If interest exists, discuss the estimated range verbally rather than leading with it in writing.

### Tier 3

1. Put into nurture.
2. Use the category story, not account-specific numbers.
3. Re-run when new CMS data drops.

### Tier 4

- Do not outbound based on this signal.

## Important guardrails

- Grade `A/B` numbers can be used with caveats.
- Grade `C` numbers should not lead written outbound.
- Grade `D` should not drive outbound at all.
- CMIO is the informatics champion for workflow integration; CIO and CISO matter later but are not discovery champions.
