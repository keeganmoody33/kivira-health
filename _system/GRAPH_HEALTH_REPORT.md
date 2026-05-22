---
name: GRAPH_HEALTH_REPORT
description: Latest /graph-health output for the Kivira Context-OS graph (2026-05-21 snapshot).
type: system-report
last_updated: 2026-05-21
generator: .claude/commands/graph-health (Claude Code)
inputs: _system/GRAPH_INDEX.json (latest)
---

# Context OS Health Report

**Generated:** 2026-05-21
**Index:** `_system/GRAPH_INDEX.json` (93 nodes, 534 resolved links, generated 2026-05-21 09:28 UTC)

## Summary

**Overall Health: Warning — no-op cycle vs 5/20.**

Numerical state is identical to the 2026-05-20 snapshot. No knowledge_base/ or 00_foundation/ .md file has been modified since the prior index. Tag sprawl is still **33.3%** (consolidation pass not run). The single aging-emergent node — `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` — is now **46 days** old, +1 day vs yesterday and 14 days from the 60-day critical threshold. Bumping it ahead of the tag-consolidation rec for this cycle.

### Delta vs the 2026-05-20 baseline (1 day)

| Metric | 2026-05-20 | 2026-05-21 | Δ |
|---|---:|---:|---:|
| Total nodes | 93 | **93** | — |
| Resolved wiki-links | 534 | **534** | — |
| Validated nodes | 54 | **54** | — |
| Emergent nodes | 15 | **15** | — |
| Archived nodes | 4 | 4 | — |
| Draft nodes | 7 | 7 | — |
| Tag sprawl | 33.3% (Warning) | **33.3% (Warning)** | — |
| Aging emergent (>30d) | 1 (45d) | **1 (46d)** | +1 day on the same node |
| Broken links | 1 | **1** | — |
| Hubs (>10 inbound) | 15 | **15** | — |
| Orphans (0 inbound, has domain) | 0 | 0 | — |

**Net read:** the graph has been operationally stable for 9 days (last ingestion 5/12). The Warning band carries because none of yesterday's three open punch-list items have been actioned.

## Inventory

**Total Nodes:** 93

**By Domain:**
- methodology: 36
- business: 30
- technical: 9
- _unset_ (Layer-2 synthesis, weekly MOCs, upstream quickstart): 18

**By Status:**
- validated: 54
- emergent: 15
- draft: 7 (weekly MOCs stay `draft` per template)
- archived: 4
- _unset_ (Layer-2 + upstream): 13

**By Node Type:**
- framework: 40
- concept: 14
- pattern: 10
- gtm_signal: 5
- execution_digest: 2
- principle: 2
- workflow: 1
- case-study: 1
- _unset_ (Layer-2 + upstream): 18

Identical to 5/20.

## Tag Health

**Tag Sprawl: 33.3%** — **Warning** (Healthy < 20%, Unhealthy > 40%).
**Total unique tags:** 48
**Single-use tags:** 16

Unchanged for the 9th consecutive day. The carried-over consolidation table (same 9 specific edits → projected sprawl 18%) is in the 5/20 report; targets have not moved.

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
| b2b-health-system | 7 |
| execution-cadence | 7 |
| evidence-discipline | 6 |

**Single-use tags (16):** `accept-triage`, `account-schema`, `data-enrichment`, `discovery-calls`, `ehr-integration`, `fee-for-service-ffs`, `funding-signals`, `hcc-hierarchical-condition-categories`, `linkedin-outreach`, `metrics`, `publicity`, `risk-adjustment-raf`, `safety-risk-notification`, `third-party-press`, `tier-architecture`, `v28-model-cms`. See the 5/20 report table for per-tag consolidation targets — unchanged.

## Link Health

**Resolved wiki-links:** 534
**Broken / unresolved links:** **1** (same as 5/20)
**Orphans (0 inbound, has domain):** 0
**Knowledge_base nodes with < 3 outbound links:** 0

**Broken link (still open):**

- `HEAT_2026_05_11` → `[[GRAPH_HEALTH_REPORT]]` — system-artifact reference, indexer excludes `_system/`. Remove the wiki-link from `knowledge_base/_index/heat-2026-05-11.md`. 1-line edit, carried from 5/12 and 5/20.

**Hub nodes (>10 inbound) — 15 total, all non-emergent:**

| Node | Inbound | Status |
|---|---:|---|
| `PRIMARY_CARE_WEDGE_ICP` | 29 | validated |
| `GTM_TIER_ARCHITECTURE_9_SUBTIERS` | 25 | validated |
| `THREE_SEGMENT_ICP_FRAMEWORK` | 22 | validated |
| `GTM_30_60_90_EXECUTION_CADENCE` | 18 | validated |
| `OUTREACH_BASELINE_METRICS` | 17 | validated |
| `CDS_NOT_DIAGNOSIS_FRAMING` | 17 | validated |
| `OUTREACH_WAVE_STRUCTURE` | 15 | validated |
| `TECH_STACK_OUTBOUND_INFRASTRUCTURE` | 14 | validated |
| `PERSONA_TITLE_DICTIONARY_BY_SUBTIER` | 13 | validated |
| `B2B_CLINIC_BUYER_MODEL` | 12 | validated |
| `CLINICAL_INSTRUMENTS_SURFACE` | 12 | validated |
| `WEEKLY_MOC_2026_05_04` | 12 | draft |
| `PUBLIC_VALUE_PROPOSITION_HOME` | 11 | validated |
| `EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS` | 11 | validated |
| `WEEKLY_MOC_GRAPH_RITUAL` | 11 | validated |

## Lifecycle Health

**Total emergent nodes:** 15
**Aging emergent (>30d):** **1**
**Critical emergent (>60d):** 0

| Node | Age | Inbound | Path |
|---|---:|---:|---|
| `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` | **46 d** | 2 | `knowledge_base/business/MEDICAL_SPEND_MODEL_ER_AVOIDANCE.md` |

Same node as 5/12 / 5/20, age now 46 days — **14 days from the 60-day critical threshold.** This is the second cycle where promotion was recommended and not actioned; recommend escalating ahead of the tag-consolidation rec this cycle. It's referenced by `REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT` and `EDP_COCM_REVENUE_REALIZATION` (both validated) and sits in the standard CoCM revenue narrative — the staying-emergent paperwork drift is clearer with each day.

**Other emergent nodes (none aging):**

| Node | Age | Inbound |
|---|---:|---:|
| `HEAT_2026_05_04` | 17d | 2 |
| `HEAT_2026_05_11` | 10d | 1 |
| `KIVIRA_COMPANY_PROFILE_2026_05_11` | 10d | 3 |
| `ACO_BLITZ_2026_05_W2_PLAN` | 9d | 1 |
| `CANONICAL_GTM_SEGMENTATION_MIRO_BOARD` | 17d | 1 |
| `INBOXKIT_SENDKIT_SEQUENCER_ROADMAP` | 17d | 1 |
| `LINKEDIN_CONNECTION_EXPORT_AS_GTM_2026_05_12` | 9d | 1 |
| `OUTBOUND_SENDER_RAMP_2026_05_W2` | 9d | 1 |
| `OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12` | 9d | 2 |
| `WEEKLY_LINEAR_SHIPPED_2026_05_04` | n/a | 7 |
| `WEEKLY_LINEAR_SHIPPED_2026_05_10` | n/a | 2 |
| `WEEKLY_HEYREACH_EVIDENCE_2026_05_04` | n/a | 7 |
| `WEEKLY_HEYREACH_EVIDENCE_2026_05_10` | n/a | 4 |
| `WEEKLY_INBOXKIT_HEALTH_2026_05_04` | n/a | 5 |

`HEAT_2026_05_04`, `CANONICAL_GTM_SEGMENTATION_MIRO_BOARD`, and `INBOXKIT_SENDKIT_SEQUENCER_ROADMAP` cross the 30-day aging threshold within ~13 days at current cadence.

## What changed in 1 day (graph-level)

- **No node creates, no edits, no promotions, no archives.**
- **No tag changes.**
- **No link changes.**
- Only mechanical change: aging counter on `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` (45d → 46d).

This is the first health check in this series with zero substantive delta. Useful baseline: it confirms the indexer + scoring is stable.

## Recommendations

### 1. **Promote (or archive) `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` THIS WEEK.** Bumped from rec 2 → rec 1.

46 days old, 2 inbound from validated CoCM revenue nodes, 14 days from critical. Promotion is a frontmatter edit. If it's truly not validated, archive it — but it's actively cited from validated nodes, so the more honest move is `status: validated`.

### 2. **Tag consolidation pass — drops sprawl 33.3% → ~18% (Healthy).** Carried from 5/12 / 5/20.

Apply the 9 specific edits from the 5/20 tag-health table. ~10 minutes. Result: graph health flips Warning → Healthy.

### 3. **Fix the broken link in `HEAT_2026_05_11`.**

Remove `[[GRAPH_HEALTH_REPORT]]` from `knowledge_base/_index/heat-2026-05-11.md`. 1-line edit. Carried from 5/12 / 5/20.

### 4. **Bake tag-reuse into `/ingest`.**

Same consulting rec as 5/12 / 5/20 — surface existing tags by frequency before any new tag is written. Standing maintenance item, not session-bound.

---

**Consulting moment triggered:** tag sprawl at 33.3% (>30% threshold), unchanged for 9 days. Same finding for the fourth consecutive health check. The recurrence pattern is well-established; the fix is small. Standing-maintenance framing applies — not a per-session ask anymore.
