---
name: GRAPH_HEALTH_REPORT
description: Latest /graph-health output for the Kivira Context-OS graph (2026-05-11 post-maintenance snapshot).
type: system-report
last_updated: 2026-05-11
generator: .claude/commands/graph-health (Claude Code)
inputs: _system/GRAPH_INDEX.json (latest)
---

# Context OS Health Report

**Generated:** 2026-05-11
**Index:** `_system/GRAPH_INDEX.json` (82 nodes, 502 resolved links)

## Summary

**Overall Health: Healthy → Warning (borderline).**

Materially improved from the 2026-05-04 baseline across every metric. The one remaining drag is tag sprawl at **28.6%** — barely above the "Healthy" 20% threshold and well below the 30% consulting-trigger. Lifecycle, links, and hub structure are all clean.

### Delta vs the 2026-05-04 baseline

| Metric | 2026-05-04 | 2026-05-11 | Δ |
|---|---|---|---|
| Total nodes | 74 | **82** | +8 |
| Resolved wiki-links | 363 | **502** | **+139** |
| Validated nodes | 32 | **49** | +17 |
| Emergent nodes | 27 | 13 | -14 |
| Archived nodes | 1 | 4 | +3 |
| Tag sprawl | **46% (Unhealthy)** | **28.6% (Warning)** | -17.4 pp |
| Aging emergent (>30d) | 19 | **1** | -18 |
| Indexer false-positive "taxonomy issues" | 9 | **0** | -9 |
| Hubs (>10 inbound) | 6 | **14** | +8 |
| Orphans (0 inbound, has domain) | 0 | 0 | — |

## Inventory

**Total Nodes:** 82

**By Domain:**
- business: 29
- methodology: 31
- technical: 9
- _unset_ (Layer-2 synthesis docs, weekly MOCs, upstream quickstart): 13

**By Status:**
- validated: 49
- emergent: 13
- draft: 8 (weekly MOCs stay `status: draft` per template; counted separately)
- archived: 4
- _unset_ (Layer-2 + upstream): 8

**By Node Type:**
- framework: 37
- concept: 14
- pattern: 8
- gtm_signal: 4
- execution_digest: 2
- principle: 2
- workflow: 1
- case-study: 1
- _unset_ (Layer-2 + upstream): 13

## Tag Health

**Tag Sprawl: 28.6%** — Warning (barely; threshold for Healthy is < 20%, for Unhealthy is > 40%)
**Total unique tags:** 42
**Single-use tags:** 12

The bulk of last week's tag-sprawl problem was resolved by the consolidation pass (collapsed 6 single-use tool-name tags into `gtm-tooling`, merged `smart-on-fhir` → `ehr-integration`, archived two single-use HCC tags).

**Most-used tags (the load-bearing taxonomy as it actually exists):**

| Tag | Count |
| --- | --- |
| methodology | 27 |
| source-research-synthesis | 26 |
| business | 23 |
| gtm-motion | 20 |
| source-public-web | 14 |
| market-segmentation | 10 |
| tam-total-addressable-market | 10 |
| source-internal-doc | 9 |
| technical | 8 |
| b2b-health-system | 7 |

**Single-use tags (consider consolidating):**

| Tag | Used by |
| --- | --- |
| account-schema | `FRESH_LIST_BUILD_RUNBOOK_1ABC` |
| data-enrichment | `LIST_BUILDING_STACK_CLAY_ENRICHMENT` |
| discovery-calls | `DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER` |
| ehr-integration | `EHR_INTEGRATION_SMART_ON_FHIR` |
| fee-for-service-ffs | `DIRECT_BILLING_MODEL_FFS` |
| funding-signals | `FUNDING_AND_BACKING_SIGNALS` |
| metrics | `OUTREACH_BASELINE_METRICS` |
| publicity | `KIVIRA_BACKER_COPY_SHIFT_2026_05` |
| risk-adjustment-raf | `REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT` |
| safety-risk-notification | `PATIENT_APP_SAFETY_ALERTS` |
| third-party-press | `POLSKY_UCHICAGO_KIVIRA_PROFILE_2026` |
| tier-architecture | `FRESH_LIST_BUILD_RUNBOOK_1ABC` |

These are mostly concept-specific labels that map 1:1 to a single node. They aren't sprawl in the negative sense — they're a node's own canonical descriptor. Three could legitimately collapse:

- `publicity` + `third-party-press` are conceptually the same — pick one and apply to both `KIVIRA_BACKER_COPY_SHIFT_2026_05` and `POLSKY_UCHICAGO_KIVIRA_PROFILE_2026`. Would convert both to 2-use tags.
- `metrics` is generic; could be folded into `gtm-motion` or `outreach-metrics`.

Doing those two consolidations would push sprawl to ~24% — still Warning, but closer to Healthy. Not worth a dedicated pass; can roll into next month's maintenance.

## Link Health

**Resolved wiki-links:** 502
**Broken / unresolved links:** 0
**Orphans (0 inbound, has domain):** 0
**knowledge_base nodes with < 3 outbound links:** 0

**Hub nodes (>10 inbound) — 14 total, doing structural work:**

| Node | Inbound | Status |
| --- | --- | --- |
| `PRIMARY_CARE_WEDGE_ICP` | 29 | validated |
| `THREE_SEGMENT_ICP_FRAMEWORK` | 22 | validated |
| `GTM_TIER_ARCHITECTURE_9_SUBTIERS` | 20 | validated |
| `GTM_30_60_90_EXECUTION_CADENCE` | 18 | validated |
| `CDS_NOT_DIAGNOSIS_FRAMING` | 17 | validated |
| `OUTREACH_WAVE_STRUCTURE` | 14 | validated |
| `TECH_STACK_OUTBOUND_INFRASTRUCTURE` | 13 | validated |
| `B2B_CLINIC_BUYER_MODEL` | 12 | validated |
| `CLINICAL_INSTRUMENTS_SURFACE` | 12 | validated |
| `WEEKLY_MOC_2026_05_04` | 12 | draft (weekly-MOC convention) |
| `PUBLIC_VALUE_PROPOSITION_HOME` | 11 | validated |
| `EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS` | 11 | validated |
| `OUTREACH_BASELINE_METRICS` | 11 | draft |
| `WEEKLY_MOC_GRAPH_RITUAL` | 11 | emergent |

12 of 14 hubs are validated or are weekly-MOCs (draft by template). The two non-validated outliers worth attention:

- `OUTREACH_BASELINE_METRICS` (11 inbound, draft) — heavily cited but the node body is a draft. Worth promoting once it has real reply-rate data (post-2026-05-17).
- `WEEKLY_MOC_GRAPH_RITUAL` (11 inbound, emergent) — the methodology node defining the weekly ritual; cited 11 times by other methodology nodes. Should promote to validated; it's clearly proven.

## Lifecycle Health

**Total emergent nodes:** 13
**Aging emergent nodes (>30 days):** **1**

| Node | Age | Inbound | Path |
| --- | --- | --- | --- |
| `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` | 36 d | 2 | `knowledge_base/business/MEDICAL_SPEND_MODEL_ER_AVOIDANCE.md` |

This is the last remaining node from the original 19-node aging-emergent backlog from 5/4. Two inbound citations puts it above the archive threshold (≤1) but below the auto-promote bar (≥7) we used during the Sunday batch. Two paths:

- **Hold** until inbound grows organically — if it accumulates a third citation in the next 4 weeks it earns its promotion.
- **Promote now** by judgment call — ER avoidance is part of the standard CoCM revenue narrative and likely load-bearing for future investor messaging; importance moderates heat per [[HEAT_EXCEPTION_EXTERNAL_VALIDATION]] (though that rule was specifically for external-validation nodes, the broader principle applies).

No emergent nodes are over the 60-day critical threshold.

## What changed this session (graph-level)

- **17 emergent → validated** promotions (THREE_SEGMENT_ICP_FRAMEWORK, B2B_CLINIC_BUYER_MODEL, PUBLIC_VALUE_PROPOSITION_HOME, DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER, GTM_MOTION_HYPOTHESIS, COMPETITIVE_EVIDENCE_GAP, EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS, EHR_INTEGRATION_SMART_ON_FHIR, PATIENT_APP_SAFETY_ALERTS, PRIVACY_AND_HIPAA_ROLE, CLINICAL_INSTRUMENTS_SURFACE, DIRECT_BILLING_MODEL_FFS, REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT, CPT_BILLING_CODES_BHI, POLSKY_UCHICAGO_KIVIRA_PROFILE_2026, plus the prior 5/4 promotion of CDS_NOT_DIAGNOSIS_FRAMING and the validate-on-create HEAT_EXCEPTION_EXTERNAL_VALIDATION)
- **3 emergent → archived** (CLINICAL_TRIALS_DIGITAL_ENDPOINTS, LIFE_SCIENCES_VALUE_PROP, HCC_V28_CODING_OPPORTUNITY)
- **5 new nodes added** (KIVIRA_COMPANY_PROFILE_2026_05_11, KIVIRA_BACKER_COPY_SHIFT_2026_05, HEAT_EXCEPTION_EXTERNAL_VALIDATION, HEAT_2026_05_11, WEEKLY_LINEAR_SHIPPED_2026_05_10, plus WEEKLY_MOC_2026_05_10 and WEEKLY_HEYREACH_EVIDENCE_2026_05_10 from earlier in session)
- **Indexer rewritten** to retire v1 BLESSED_* enforcement; wikilink regex updated to handle pipe-aliases and lowercase/hyphens; the +139 link delta is largely a recount of previously-invisible pipe-aliased links surfacing for the first time
- **Tag consolidation pass** introduced `gtm-tooling` as an umbrella tag across 6 nodes, removed 6 single-use tool names + `shipped` + `smart-on-fhir`

## Recommendations

1. **Promote `WEEKLY_MOC_GRAPH_RITUAL` to validated.** 11 inbound, 6+ weeks old, defining the standing ritual that produced this entire health pass. Clearest case for promotion outside the heat rule.
2. **Resolve `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` (the last aging emergent).** Quick judgment call — either promote on importance grounds or wait one more week for the third citation.
3. **(Optional, next month):** Two tiny tag consolidations to push sprawl from 28.6% → ~24%: `publicity` + `third-party-press` → pick one; `metrics` → fold into `gtm-motion` or rename `outreach-metrics`. Not blocking; defer if not motivated.

---

**Consulting moments triggered:** _none._ Tag sprawl 28.6% is below the 30% trigger; aging emergent count is 1 (below the >10 trigger); orphans are 0 (below the >5 trigger). All three thresholds passed for the first time since the report was first run on 2026-05-04.
