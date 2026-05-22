---
name: JOSH_DRS_GROUP_LIST_INGEST_2026
description: Column semantics and ingest rules for Josh Drs Group 2026 physician-group CSV exports.
domain: methodology
node_type: pattern
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - list-building
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - buyer-diligence
related_concepts:
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[JOSH_PILOT_LIST_MOTION_2026]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
source:
  type: internal-doc
  file: "Drs Group US_Kivira Project 2026 - Physician_Group_Nationwide_Execs_.csv"
  date: "2026-05-22"
---

# Josh Drs Group list ingest (2026)

[VERIFIED: Derived from repo CSV structure analysis 2026-05-22]

Josh provided three files at repo root. Only the nationwide exec and PCP list are contact rows.

## Headerless 12-column exec layout

| Column | Field | Notes |
|--------|--------|--------|
| 0 | contact_name | |
| 1 | title_raw | |
| 2 | title_bucket | Vendor bucket (Owner, Medical Director, …) |
| 3 | email | Ingest-only for Apollo match; not HeyReach v1 |
| 4 | col4_misc | Often a **phone**, not LinkedIn — classify `col4_kind` |
| 5 | phone | Ingest-only |
| 6 | org_name | |
| 7 | org_type | Usually Single/Multi-Specialty Physician Group |
| 8–10 | address, city, state | |
| 11 | size_metric | Numeric 0–50+; treated as clinician/site proxy until Josh confirms |

## READ.csv

Title taxonomy + Sales Navigator boolean strings — maps to `read_title_buckets.yaml` (integrated care, regulatory/revenue, service line). Not a contact list.

## Normalization

`scripts/ingest_josh_drs_group_csv.py` writes `fixtures/josh_drs_group_2026/josh_exec_normalized.csv` and `josh_pcp_seed.csv` with explicit headers.
