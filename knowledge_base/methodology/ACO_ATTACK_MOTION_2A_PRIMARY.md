---
name: ACO_ATTACK_MOTION_2A_PRIMARY
description: Canonical decision — attack ACOs as Tier 2A entities (sync blitz + Wave 2 LinkedIn); 1C ACO-affiliated groups are secondary, deduped channel.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-21
tags:
  - methodology
  - gtm-motion
  - market-segmentation
  - outbound
  - workflow
topics:
  - gtm-motion
  - market-segmentation
  - workflow
  - execution-cadence
related_concepts:
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[TAM_TIER_2_ACO_VBC_73M]]"
  - "[[ACO_BLITZ_2026_05_W2_PLAN]]"
  - "[[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
  - "[[KIVIRA_ENGAGEMENT_STRUCTURE_JP_INTERMEDIARY]]"
source:
  type: notes
  file: "Plan ACO placement and TAM 2026-05-21"
  date: "2026-05-21"
---

# ACO attack motion — 2A primary (2026-05-21)

[VERIFIED: Subtier and TAM counts from [[TAM_TIER_2_ACO_VBC_73M]] and CMS PY2026 Organizations ingest via `scripts/build_aco_attack_lists.py`.]

## Decision

**Primary motion for “attacking ACOs” is subtier 2A — the ACO legal entity** with distinct contracting and a population-health operating team. **Secondary motion** is Tier **1C** provider groups tagged `2A_aco_affiliated` (~1,500 logos) — same VBC pain, different buyer (practice/group COO vs ACO network performance).

Do **not** run both motions against the same logo without `parent_org_id` routing.

| Motion | When to use | Channel | List artifact |
|--------|-------------|---------|----------------|
| **2A entity (primary)** | MSSP/REACH ACO holds the contract; pop health / quality / risk leaders | Sync blitz (CMS exec email/phone) + Wave 2 LinkedIn (Spider persona hits) | `fixtures/aco_attack/blitz_focus_2a.csv`, `wave2_linkedin_2a.csv` |
| **1C + 2A_aco_affiliated (secondary)** | Provider group is the economic buyer; ACO is administrative overlay | Tier 1C HeyReach / phone wedge | `fixtures/wave1_raw_accounts.csv` (1C rows), not duplicate 2A logos |

## Taxonomy placement (no separate “vertical”)

| Lens | Placement |
|------|-----------|
| Subtier | **2A** |
| Tier | **2** — risk-bearing / enablement |
| ICP segment | **Segment 2** — Health System / ACO / VBC Care Management |
| Pain segment | **VBC Risk-Squeezed ACOs** (priority #2, 0.85) |

## TAM (2A entities only)

| Metric | Value | Source |
|--------|-------|--------|
| Net logos | **395** (model); **~450+** CMS PY2026 org file before 1C dedup at ingest | [[TAM_TIER_2_ACO_VBC_73M]] |
| ACV | **$120K** | [[TAM_TIER_2_ACO_VBC_73M]] |
| Dollar TAM | **$47.4M** | [[TAM_TIER_2_ACO_VBC_73M]] |
| HIGH fit (ENHANCED + agreement period ≥3) | **~156** from CMS PY2026 Organizations (`enhanced_track` + `agreement_period_num`) | `fixtures/aco_attack/high_fit_2a.csv` (regenerate via script) |

Do not conflate with **Tier 2 total ($73.2M / 675 logos)** — that includes 2B enablers and 2C care management.

## Value prop by motion

- **2A:** [[REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT]], network TCO / quality — not CoCM self-funding alone ([[THREE_SEGMENT_ICP_FRAMEWORK]] Segment 2).
- **1C affiliated:** [[DIRECT_BILLING_MODEL_FFS]] + VBC quality — Segment 1 wedge with sharper VBC story.

## Wave 1 learnings (why 2A is sync-first)

- 359 OperationalOwner-2A LinkedIn leads → **zero** in-scope accepts ([[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] Wave 1 read).
- **2A primary attack = synchronous depth** on CMS named contacts; LinkedIn is a **parallel test** on persona-qualified titles, not CMS placeholder execs ([[ACO_BLITZ_2026_05_W2_PLAN]], [[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]).

## List build (operator)

```bash
python3 scripts/build_aco_attack_lists.py
```

Regenerates `fixtures/aco_attack/*` from CMS MSSP Organizations CSV (cached under `artifacts/cms_mssp_orgs_py2026.csv`). Optional `--reach-csv` for REACH participants.

See `_system/agent_workflows/aco-attack-list-build.md` for runbook.

## Dedup checklist before outreach

1. If provider group is primary → **1C**, tag `2A_aco_affiliated`; do not also cold-call the ACO shell.
2. If `parent_org_id` matches Tier 3A/3B (~158 ACOs) → route enterprise thread to health-system owner, not duplicate 2A-only pitch.
3. Blitz cohort excludes org names already in `fixtures/heyreach_loads/heyreach_leads_2a.json` (Wave 1 touched).

## Related Concepts

- [[ACO_BLITZ_2026_05_W2_PLAN]] — sync block execution
- [[PUBLIC_DATA_SOURCES_TAM]] — CMS field map
- [[TAM_DEDUP_METHODOLOGY]] — 1C vs 2A counting rules
