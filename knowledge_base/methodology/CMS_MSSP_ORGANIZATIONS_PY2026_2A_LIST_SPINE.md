---
name: CMS_MSSP_ORGANIZATIONS_PY2026_2A_LIST_SPINE
description: ACO-level CMS PY2026 MSSP Organizations CSV as the canonical spine for Tier 2A list build, high-fit filtering, and blitz cohorts — distinct from the participant-level Par_LBN file.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-21
tags:
  - methodology
  - tam-total-addressable-market
  - gtm-motion
  - workflow
  - source-public-web
topics:
  - tam-total-addressable-market
  - gtm-motion
  - workflow
  - market-segmentation
related_concepts:
  - "[[PUBLIC_DATA_SOURCES_TAM]]"
  - "[[ACO_ATTACK_MOTION_2A_PRIMARY]]"
  - "[[TAM_TIER_2_ACO_VBC_73M]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
  - "[[TAM_DEDUP_METHODOLOGY]]"
source:
  type: document
  file: "Cursor session ACO placement and TAM plan implementation 2026-05-21"
  date: "2026-05-21"
---

# CMS MSSP Organizations (PY2026) — 2A list spine

[VERIFIED: Counts from `scripts/build_aco_attack_lists.py` run against live CMS download 2026-05-21.]

## Why a separate file from “participants”

The **participant** export (`Par_LBN` rows) powers **Tier 1C** VBC provider groups under an ACO umbrella. The **Organizations** export is **one row per ACO legal entity** — the correct spine for **subtier 2A** attack lists, CMS exec contacts, and ENHANCED-track / agreement-period filters.

Do not size 2A HIGH-fit from participant row counts alone.

## Canonical download

**Title (data.cms.gov):** Accountable Care Organizations  
**PY2026 CSV:**

`https://data.cms.gov/sites/default/files/2026-04/358ddf60-c203-41ef-a0c6-a62a79f466ee/PY2026_Medicare_Shared_Savings_Program_Organizations.csv`

**Repo cache after first script run:** `artifacts/cms_mssp_orgs_py2026.csv`

## Fields used for 2A fit and outreach

| Field | Use |
|-------|-----|
| `aco_name` | Logo key |
| `aco_service_area` | State (first code if comma-list) |
| `agreement_period_num` | HIGH fit requires ≥3 with ENHANCED |
| `enhanced_track` | `1` = ENHANCED (highest VBC accountability) |
| `basic_track` / `basic_track_level` | MEDIUM fit signal |
| `pc_flex_agreement_status` | PC Flex bump to MEDIUM when not HIGH |
| `aco_exec_name` / `aco_exec_email` / `aco_exec_phone` | Sync blitz primary contact |
| `aco_medical_director_name` | Clinical champion seed |

## Fit tiers (script logic)

| Tier | Rule |
|------|------|
| **HIGH** | `enhanced_track=1` AND `agreement_period_num≥3`, OR ACO REACH ingest |
| **MEDIUM** | ENHANCED without period≥3, or BASIC / period 2 |
| **LOWER** | Period 1 |

Aligns with [[WAVE_1_SCORING_FRAMEWORK]] VBC participation weighting (ENHANCED = highest urgency).

## Exclusions at ingest

Applied in `tam_builder/aco_attack.py` before net 2A count:

- **admin_shell** — holding / consultation-management names without physician-network signal
- **hospital_only** — hospital / medical center without PCP-network keywords

[INFERRED: Stricter than Wave 1 list; reconciles ~511 MSSP org rows → ~504 net vs [[TAM_TIER_2_ACO_VBC_73M]] model 395 after 1C-primary and manual TAM dedup.]

## PY2026 ingest snapshot (2026-05-21)

| Slice | Count |
|-------|------:|
| MSSP org rows loaded | 508 |
| Excluded (shell/hospital) | 4 |
| **Net 2A org spine** | **504** |
| HIGH fit + CMS exec contact | **156** |
| Wave 2 LinkedIn account spine (`wave2_linkedin_2a.csv`) | **135** |
| Blitz focus (`blitz_focus_2a.csv`, fresh vs Wave 1 HeyReach) | **40** |

## Operator command

```bash
python3 scripts/build_aco_attack_lists.py
```

Outputs: `fixtures/aco_attack/`. Runbook: `_system/agent_workflows/aco-attack-list-build.md`.

## Related Concepts

- [[PUBLIC_DATA_SOURCES_TAM]] — broader CMS stack (participant file still used for 1C)
- [[ACO_ATTACK_MOTION_2A_PRIMARY]] — when to use this spine vs 1C affiliated
- [[ACO_BLITZ_2026_05_W2_PLAN]] — sync cohort from `blitz_focus_2a.csv`
