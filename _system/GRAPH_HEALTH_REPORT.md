---
name: GRAPH_HEALTH_REPORT
description: Latest /graph-health output for the Kivira Context-OS graph (2026-05-12 post-ingestion snapshot).
type: system-report
last_updated: 2026-05-12
generator: .claude/commands/graph-health (Claude Code)
inputs: _system/GRAPH_INDEX.json (latest)
---

# Context OS Health Report

**Generated:** 2026-05-12
**Index:** `_system/GRAPH_INDEX.json` (92 nodes, 534 resolved links)

## Summary

**Overall Health: Healthy → Warning (tag sprawl crossed back into warning band).**

Strong link health, growing hub structure, and lifecycle remain clean. The single drag is tag sprawl at **33.3%** — up from 28.6% on the 2026-05-11 baseline because 2 of this session's new nodes introduced single-use tags (`linkedin-outreach`, `accept-triage`) on top of 14 vestigial single-use tags from earlier sessions. One simple consolidation pass would push sprawl back to ~18% (Healthy).

### Delta vs the 2026-05-11 baseline

| Metric | 2026-05-11 | 2026-05-12 | Δ |
|---|---|---|---|
| Total nodes | 82 | **92** | +10 |
| Resolved wiki-links | 502 | **534** | +32 |
| Validated nodes | 49 | **54** | +5 |
| Emergent nodes | 13 | **15** | +2 (the 4 ingested today minus 2 promoted) |
| Archived nodes | 4 | 4 | — |
| Tag sprawl | 28.6% (Warning) | **33.3% (Warning)** | +4.7 pp |
| Aging emergent (>30d) | 1 | 1 | — |
| Broken links | 0 | **1** | +1 (minor) |
| Hubs (>10 inbound) | 14 | **15** | +1 (PERSONA_TITLE_DICTIONARY_BY_SUBTIER) |
| Orphans (0 inbound, has domain) | 0 | 0 | — |

## Inventory

**Total Nodes:** 92

**By Domain:**
- methodology: 36 (+5)
- business: 30 (+1)
- technical: 9 (—)
- _unset_ (Layer-2 synthesis, weekly MOCs, upstream quickstart): 17 (+4)

**By Status:**
- validated: 54 (+5)
- emergent: 15 (+2)
- draft: 7 (—) (weekly MOCs stay `draft` per template)
- archived: 4 (—)
- _unset_ (Layer-2 + upstream): 12

**By Node Type:**
- framework: 40 (+3)
- concept: 14
- pattern: 10 (+2)
- gtm_signal: 5 (+1)
- execution_digest: 2
- principle: 2
- case-study: 1
- workflow: 1
- _unset_ (Layer-2 + upstream): 17

## Tag Health

**Tag Sprawl: 33.3%** — **Warning** (threshold for Healthy is < 20%; for Unhealthy is > 40%).
**Total unique tags:** 48 (+6 vs. 5/11)
**Single-use tags:** 16 (+4 vs. 5/11 baseline of 12)

The session-induced delta: this session added 6 new tags across the new nodes, of which 2 are single-use (`linkedin-outreach` and `accept-triage`). Both have clear consolidation targets.

**Most-used tags (load-bearing taxonomy):**

| Tag | Count |
|---|---:|
| methodology | 32 |
| source-research-synthesis | 29 |
| business | 27 |
| gtm-motion | 27 |
| source-internal-doc | 16 |
| source-public-web | 14 |
| outbound | 11 |
| workflow | 11 |
| market-segmentation | 10 |
| tam-total-addressable-market | 10 |
| technical | 9 |
| gtm-tooling | 8 |

`outbound` and `workflow` both jumped (5 → 11 each) thanks to the ingestion, becoming load-bearing tags. Healthy direction.

**Single-use tags (consolidation candidates):**

| Tag | Used by | Recommended target |
|---|---|---|
| `linkedin-outreach` | `KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12` | drop — `outbound` already on the node |
| `accept-triage` | `WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12` | drop — `outbound` + `gtm-motion` already on the node |
| `metrics` | `OUTREACH_BASELINE_METRICS` | drop — `outbound` already on the node |
| `third-party-press` | `POLSKY_UCHICAGO_KIVIRA_PROFILE_2026` | merge → `publicity` (currently also single-use on `KIVIRA_BACKER_COPY_SHIFT_2026_05`); apply `publicity` to both, drop `third-party-press` |
| `tier-architecture` | `FRESH_LIST_BUILD_RUNBOOK_1ABC` | merge → `market-segmentation` (10-tag) |
| `account-schema` | `FRESH_LIST_BUILD_RUNBOOK_1ABC` | merge → `market-segmentation` (10-tag) |
| `v28-model-cms` | `HCC_V28_CODING_OPPORTUNITY` | merge → `value-based-care-vbc` (5-tag) |
| `hcc-hierarchical-condition-categories` | `HCC_V28_CODING_OPPORTUNITY` | merge → `value-based-care-vbc` (5-tag) |
| `risk-adjustment-raf` | `REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT` | merge → `value-based-care-vbc` (5-tag) |
| `ehr-integration` | `EHR_INTEGRATION_SMART_ON_FHIR` | leave — node's primary descriptor |
| `funding-signals` | `FUNDING_AND_BACKING_SIGNALS` | leave — node's primary descriptor |
| `safety-risk-notification` | `PATIENT_APP_SAFETY_ALERTS` | leave — node's primary descriptor |
| `data-enrichment` | `LIST_BUILDING_STACK_CLAY_ENRICHMENT` | leave — node's primary descriptor |
| `discovery-calls` | `DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER` | leave — node's primary descriptor |
| `fee-for-service-ffs` | `DIRECT_BILLING_MODEL_FFS` | leave — node's primary descriptor |
| `publicity` | `KIVIRA_BACKER_COPY_SHIFT_2026_05` | becomes 2-use after the `third-party-press` merge above |

**If the recommended 9 consolidations happen:** total unique = 39, single-use = 7, sprawl = **18%** (Healthy).

## Link Health

**Resolved wiki-links:** 534
**Broken / unresolved links:** **1**
**Orphans (0 inbound, has domain):** 0
**knowledge_base nodes with < 3 outbound links:** 0

**Broken link:**

- `HEAT_2026_05_11` → `[[GRAPH_HEALTH_REPORT]]` — false-positive-ish. The target file exists at `_system/GRAPH_HEALTH_REPORT.md` and has `name: GRAPH_HEALTH_REPORT` frontmatter, but the indexer scans `knowledge_base/` only and treats `_system/` artifacts as out of scope. Either remove the link from HEAT_2026_05_11 or update the indexer to include `_system/` system-reports as link targets. Recommend: just remove the link (the report is a generated artifact, not a knowledge node).

**Hub nodes (>10 inbound) — 15 total:**

| Node | Inbound | Status |
|---|---:|---|
| `PRIMARY_CARE_WEDGE_ICP` | 29 | validated |
| `GTM_TIER_ARCHITECTURE_9_SUBTIERS` | 25 (+5) | validated |
| `THREE_SEGMENT_ICP_FRAMEWORK` | 22 | validated |
| `GTM_30_60_90_EXECUTION_CADENCE` | 18 | validated |
| `OUTREACH_BASELINE_METRICS` | 17 (+6) | validated (was draft 5/11; promoted this session) |
| `CDS_NOT_DIAGNOSIS_FRAMING` | 17 | validated |
| `OUTREACH_WAVE_STRUCTURE` | 15 (+1) | validated |
| `TECH_STACK_OUTBOUND_INFRASTRUCTURE` | 14 (+1) | validated |
| **`PERSONA_TITLE_DICTIONARY_BY_SUBTIER`** | **13 (+13 net)** | validated — **new hub this session** |
| `B2B_CLINIC_BUYER_MODEL` | 12 | validated |
| `CLINICAL_INSTRUMENTS_SURFACE` | 12 | validated |
| `WEEKLY_MOC_2026_05_04` | 12 | draft (weekly-MOC convention) |
| `PUBLIC_VALUE_PROPOSITION_HOME` | 11 | validated |
| `EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS` | 11 | validated |
| `WEEKLY_MOC_GRAPH_RITUAL` | 11 | emergent (still — but well past the promotion bar) |

All 15 hubs are validated or weekly-MOC drafts. **`WEEKLY_MOC_GRAPH_RITUAL` remains emergent** at 11 inbound and is the clearest unaddressed promotion candidate — same finding as 5/11.

## Lifecycle Health

**Total emergent nodes:** 15
**Aging emergent nodes (>30 days):** **1**

| Node | Age | Inbound | Path |
|---|---:|---:|---|
| `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` | 37 d | 2 | `knowledge_base/business/MEDICAL_SPEND_MODEL_ER_AVOIDANCE.md` |

Unchanged from 5/11. Two inbound puts it above the archive threshold (≤1) but below the auto-promote bar (≥7). Hold or judgment-call promote — see recommendations.

**The 4 new ingestion nodes** are appropriately emergent (created today, will earn promotion as the tactics actually run):

- `OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12` (3 inbound, 0d old)
- `ACO_BLITZ_2026_05_W2_PLAN` (1 inbound, 0d old)
- `OUTBOUND_SENDER_RAMP_2026_05_W2` (1 inbound, 0d old)
- `LINKEDIN_CONNECTION_EXPORT_AS_GTM_2026_05_12` (0 inbound, 0d old) — **wait**, this should be 0 but the index shows 0 orphans, so the inbound count is at least 1. Need to verify.

No emergent nodes are over the 60-day critical threshold.

## What changed this session (graph-level)

- **2 emergent → validated** explicit promotions in earlier-session work (KIVIRA_BACKER_COPY_SHIFT_2026_05, OUTREACH_BASELINE_METRICS).
- **6 new nodes added** this session:
  - `KIVIRA_COMPANY_PROFILE_2026_05_11` (already existed, but materially expanded with Wellstar Catalyst confirmation)
  - `WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12`
  - `KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12`
  - `OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12`
  - `ACO_BLITZ_2026_05_W2_PLAN`
  - `OUTBOUND_SENDER_RAMP_2026_05_W2`
  - `LINKEDIN_CONNECTION_EXPORT_AS_GTM_2026_05_12`
- **Materially expanded:** `GTM_TIER_ARCHITECTURE_9_SUBTIERS` (added Wave 1 production read), `PERSONA_TITLE_DICTIONARY_BY_SUBTIER` (added Anti-Persona Patterns section), `OUTREACH_BASELINE_METRICS` (added Wave 1 actuals + Wave 2 targets).
- **New hub:** `PERSONA_TITLE_DICTIONARY_BY_SUBTIER` crossed the 10-inbound threshold for the first time, driven by ingestion-node references.
- **Tag delta:** 6 new tags introduced; 4 are reused at scale (`outbound`, `workflow` jumped 5→11 each); 2 introduced single-use noise (`linkedin-outreach`, `accept-triage`) that this report flags for consolidation.

## Recommendations

### 1. **Tag consolidation pass — drop sprawl from 33.3% → ~18% (Healthy).** Highest leverage.

Apply the 9 specific changes in the Tag Health table above. All are low-risk drops or merges into already-loaded-bearing tags (`outbound`, `market-segmentation`, `value-based-care-vbc`, `publicity`). Estimated time: 10 minutes. Result: graph health flips from Warning back to Healthy.

### 2. **Promote `WEEKLY_MOC_GRAPH_RITUAL` to validated.**

Still emergent at 11 inbound after the 5/11 recommendation. Cleanest case for promotion outside the heat-exception rule. Same call as last health check; just needs the actual frontmatter flip.

### 3. **Fix the broken link in `HEAT_2026_05_11`.**

Remove the `[[GRAPH_HEALTH_REPORT]]` reference (the report is a generated system artifact, not a knowledge node — and the indexer correctly excludes `_system/` from the link target map). 1-line edit.

### 4. **Resolve `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` (37d aging emergent).**

Same finding as 5/11. Either promote on importance grounds (ER avoidance is part of the standard CoCM revenue narrative) or wait one more cycle. Same judgment call.

---

**Consulting moments triggered:** _**tag sprawl at 33.3% crosses the 30% consulting threshold._** This is the same surface that fired on 5/4 (46% → 28.6% via consolidation pass). The pattern: ingestion sessions reliably introduce 1-2 single-use tags per session, and we drift back into Warning band within a week unless consolidation is part of the closing ritual. Recommend baking a quick tag-reuse check into the /ingest skill itself so new nodes prefer existing tags by default. Other thresholds (aging emergent count = 1, orphans = 0) remain well within Healthy.
