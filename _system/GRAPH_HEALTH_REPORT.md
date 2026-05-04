---
name: GRAPH_HEALTH_REPORT
description: Latest /graph-health output for the Kivira Context-OS graph
type: system-report
last_updated: 2026-05-04
generator: .claude/commands/graph-health (Claude Code)
inputs: _system/GRAPH_INDEX.json (regenerated 2026-05-04 21:42 UTC)
---

# Context OS Health Report

**Generated:** 2026-05-04
**Index:** `_system/GRAPH_INDEX.json` (74 nodes, 394 resolved links)

## Summary

**Overall Health: Warning**

The graph is structurally sound — 0 broken wiki-links, 6 well-connected hub nodes, and a clear domain split. Two issues pull it out of *Healthy*:

1. **Tag sprawl is 46%** (23 of 50 unique tags used exactly once). Threshold for *Unhealthy* is >40%.
2. **8 emergent nodes have just crossed the 30-day validation deadline** (all dated 2026-04-03, the foundation seed batch). These need a validate-or-archive decision this week.

A meta-issue worth flagging: the indexer (`scripts/index_graph.py`) is still enforcing a v1 ontology (rejecting `status: archived`, `status: draft`, `node_type: workflow`, `node_type: gtm_signal`, etc.), but `CLAUDE.md` HARD RULE #8 explicitly retires `taxonomy.yaml` / `ontology.yaml`. The 9 reported "taxonomy issues" are noise from an out-of-date enforcer, not real graph defects. The indexer should be updated to drop those checks (or just stop emitting them).

## Inventory

**Total Nodes:** 74 (71 Kivira-owned + 3 upstream quickstart reference docs)

**By Domain:**
- business: 26
- methodology: 28
- technical: 9
- _unset_ (Layer-2 synthesis, weekly MOCs, upstream quickstart): 11

**By Status:**
- validated: 32
- emergent: 27
- draft: 6
- archived: 1
- _unset_ (Layer-2 docs that intentionally don't carry status): 8

**By Node Type:**
- framework: 35
- concept: 14
- pattern: 8
- gtm_signal: 2
- case-study, execution_digest, principle, workflow: 1 each
- _unset_ (Layer-2 + upstream): 11

## Tag Health

**Tag Sprawl: 46.0%** — Unhealthy (threshold > 40%)
**Total unique tags:** 50
**Single-use tags:** 23

**Most-used tags (these are the load-bearing ones):**
| Tag | Count |
| --- | --- |
| source-research-synthesis | 29 |
| methodology | 26 |
| business | 24 |
| gtm-motion | 20 |
| source-public-web | 12 |
| source-internal-doc | 10 |
| market-segmentation | 10 |
| tam-total-addressable-market | 10 |
| technical | 9 |
| b2b-health-system | 7 |

**Single-use tags (consolidation candidates):**

Most are concept-specific labels that are unlikely to recur and can be left alone or absorbed into a parent tag:

- `account-schema` → `knowledge_base/methodology/FRESH_LIST_BUILD_RUNBOOK_1ABC.md`
- `data-enrichment` → `knowledge_base/technical/LIST_BUILDING_STACK_CLAY_ENRICHMENT.md`
- `discovery-calls` → `knowledge_base/methodology/DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER.md`
- `ehr-integration` → `knowledge_base/technical/EHR_INTEGRATION_SMART_ON_FHIR.md`
- `email-deliverability` → `knowledge_base/gtm_signals/inboxkit/weekly-health-2026-05-04.md`
- `fee-for-service-ffs` → `knowledge_base/business/DIRECT_BILLING_MODEL_FFS.md`
- `funding-signals` → `knowledge_base/business/FUNDING_AND_BACKING_SIGNALS.md`
- `graph-health` → `knowledge_base/_index/heat-2026-05-04.md`
- `hcc-hierarchical-condition-categories` → `knowledge_base/technical/HCC_V28_CODING_OPPORTUNITY.md`
- `heyreach` → `knowledge_base/gtm_signals/heyreach/weekly-evidence-2026-05-04.md`
- `inboxkit` → `knowledge_base/gtm_signals/inboxkit/weekly-health-2026-05-04.md`
- `linear` → `knowledge_base/execution/linear/weekly-shipped-2026-05-04.md`
- `metrics` → `knowledge_base/methodology/OUTREACH_BASELINE_METRICS.md`
- `outbound-infrastructure` → `knowledge_base/methodology/INBOXKIT_SENDKIT_SEQUENCER_ROADMAP.md`
- `risk-adjustment-raf` → `knowledge_base/business/REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT.md`
- `safety-risk-notification` → `knowledge_base/technical/PATIENT_APP_SAFETY_ALERTS.md`
- `shipped` → `knowledge_base/execution/linear/weekly-shipped-2026-05-04.md`
- `smart-on-fhir` → `knowledge_base/technical/EHR_INTEGRATION_SMART_ON_FHIR.md`
- `third-party-press` → `knowledge_base/business/POLSKY_UCHICAGO_KIVIRA_PROFILE_2026.md`
- `tier-architecture` → `knowledge_base/methodology/FRESH_LIST_BUILD_RUNBOOK_1ABC.md`
- `tooling` → `knowledge_base/technical/LIST_BUILDING_STACK_CLAY_ENRICHMENT.md`
- `v28-model-cms` → `knowledge_base/technical/HCC_V28_CODING_OPPORTUNITY.md`
- `wave1` → `knowledge_base/gtm_signals/heyreach/weekly-evidence-2026-05-04.md`

**Likely consolidations:**
- The four GTM-tooling tags (`heyreach`, `inboxkit`, `linear`, `outbound-infrastructure`, `tooling`, `email-deliverability`) overlap with the broader `gtm-motion` tag and could collapse into a single `gtm-tooling` tag.
- `smart-on-fhir` and `ehr-integration` are the same concept under two labels; pick one.
- `hcc-hierarchical-condition-categories` and `v28-model-cms` are the same node and could collapse into `hcc-coding`.
- `shipped`, `wave1`, `metrics`, `graph-health` are weekly-MOC scaffolding tags; once the weekly archive grows, they will recur and stop being single-use on their own.

Per HARD RULE #8 we are not obeying `taxonomy.yaml`, so these are suggestions for human curation, not automated rewrites.

## Link Health

**Resolved wiki-links:** 394
**Broken / unresolved links:** 0

**Hub Nodes (>10 inbound) — these are doing structural work:**
| Node | Inbound |
| --- | --- |
| `PRIMARY_CARE_WEDGE_ICP` | 26 |
| `THREE_SEGMENT_ICP_FRAMEWORK` | 20 |
| `GTM_TIER_ARCHITECTURE_9_SUBTIERS` | 18 |
| `GTM_30_60_90_EXECUTION_CADENCE` | 15 |
| `CDS_NOT_DIAGNOSIS_FRAMING` | 14 |
| `OUTREACH_WAVE_STRUCTURE` | 11 |

This is healthy — six distinct hubs covering ICP, segmentation, tier architecture, cadence, regulatory framing, and outreach structure.

**Orphan Nodes (<3 outbound `related_concepts`) — 4 total, but only 1 is in scope:**

In scope:
- `wave-1a-execution-schedule-2026-05-01` — 1 outbound, 0 inbound (`00_foundation/_synthesis/wave-1a-execution-schedule-2026-05-01.md`). This is a Layer-2 synthesis dated 3 days ago; it should at minimum link back to `OUTREACH_WAVE_STRUCTURE`, `PILOT_SITE_ACQUISITION_PRIORITY`, `WAVE_1_SCORING_FRAMEWORK`, and `FRESH_LIST_BUILD_RUNBOOK_1ABC`.

Out of scope (upstream quickstart reference docs — not part of Kivira's graph, leave alone):
- `context-sensitivity-model`, `domain-query-patterns`, `falsifiability-spectrum` (all in `gtm-context-os-quickstart/.claude/skills/.../references/`)

## Lifecycle Health

**Total emergent nodes:** 27
**Aging emergent nodes (> 30 days):** 8 — all dated `2026-04-03`, exactly 31 days old. This is the foundation seed batch crossing the validation deadline this week:

| Node | Age | Path |
| --- | --- | --- |
| `B2B_CLINIC_BUYER_MODEL` | 31d | `knowledge_base/business/B2B_CLINIC_BUYER_MODEL.md` |
| `DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER` | 31d | `knowledge_base/methodology/DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER.md` |
| `EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS` | 31d | `knowledge_base/methodology/EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS.md` |
| `CDS_NOT_DIAGNOSIS_FRAMING` | 31d | `knowledge_base/technical/CDS_NOT_DIAGNOSIS_FRAMING.md` |
| `CLINICAL_INSTRUMENTS_SURFACE` | 31d | `knowledge_base/technical/CLINICAL_INSTRUMENTS_SURFACE.md` |
| `EHR_INTEGRATION_SMART_ON_FHIR` | 31d | `knowledge_base/technical/EHR_INTEGRATION_SMART_ON_FHIR.md` |
| `PATIENT_APP_SAFETY_ALERTS` | 31d | `knowledge_base/technical/PATIENT_APP_SAFETY_ALERTS.md` |
| `PRIVACY_AND_HIPAA_ROLE` | 31d | `knowledge_base/technical/PRIVACY_AND_HIPAA_ROLE.md` |

**Validation candidates within this set:** `CDS_NOT_DIAGNOSIS_FRAMING` is already a 14-inbound hub and is referenced by the public legal/clinical framing rule in CLAUDE.md — it should be promoted to `validated` (or `canonical`) immediately.

**No nodes have crossed the 60-day critical threshold.**

## Indexer / Tooling Issues (informational)

`scripts/index_graph.py` is flagging 9 nodes for `unknown status` or `unknown node_type`:
- `status: archived` (1) — required by HARD RULE #2
- `status: draft` (3)
- `node_type: execution_digest`, `gtm_signal` (3) — used by the weekly MOC ritual
- `node_type: principle`, `workflow` (2)

Per CLAUDE.md HARD RULE #8 these are v1 ontology artifacts and should not constrain the agents. The indexer itself needs to be updated to either (a) accept these as valid, (b) drop the check, or (c) read its allowed list from a single source of truth. Filed as a tooling task, not a graph defect.

## Recommendations

1. **Validate the foundation seed batch this week.** All 8 nodes dated 2026-04-03 are at day 31. Walk each one against current copy / signal data and either promote to `validated`, supersede, or archive. Start with `CDS_NOT_DIAGNOSIS_FRAMING` (already a 14-inbound hub) and `EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS` (used as the standing rule in research).
2. **Fix the one in-scope orphan:** add backlinks from `00_foundation/_synthesis/wave-1a-execution-schedule-2026-05-01.md` to `OUTREACH_WAVE_STRUCTURE`, `WAVE_1_SCORING_FRAMEWORK`, `PILOT_SITE_ACQUISITION_PRIORITY`, and `FRESH_LIST_BUILD_RUNBOOK_1ABC`.
3. **Trim tag sprawl below 40%.** Lowest-effort wins: collapse `smart-on-fhir` + `ehr-integration` → one tag; collapse `hcc-hierarchical-condition-categories` + `v28-model-cms` → `hcc-coding`; collapse the GTM-tooling cluster (`heyreach`, `inboxkit`, `linear`, `outbound-infrastructure`, `tooling`, `email-deliverability`) into a single `gtm-tooling` tag. That alone removes ~7 single-use tags and pushes the sprawl below the warning threshold.
4. **Update `scripts/index_graph.py` to stop emitting v1 taxonomy errors** so future health reports aren't bloated by 9 false positives. Either remove the check or drive it from `_system/agent_workflows/` rather than the retired `_system/knowledge_graph/`.

---

**Consulting moments triggered:**

- **Tag sprawl > 30% (actually 46%):** "Your tag sprawl is high (46%). This typically means tags were created ad-hoc without planning, or there are multiple terms for the same concept. Basic fix: manually consolidate similar tags (see recommendations above). Advanced fix: taxonomy design consultation — https://taste.systems"
- **Aging emergent nodes < 10:** Not yet at the threshold for a systematic-validation referral, but the 8 day-31 nodes mean the next graph-health run could trip it. Address them this week to keep below the line.
