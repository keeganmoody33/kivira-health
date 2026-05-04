---
name: FRESH_LIST_BUILD_RUNBOOK_1ABC
description: Operational runbook for fresh GTM subtier lists (1A/1B/1C)—base_gap first, GA pilot, live-public gating, messaging deferred
domain: methodology
node_type: pattern
status: validated
last_updated: 2026-05-04
tags:
  - methodology
  - workflow
  - tam-total-addressable-market
  - tier-architecture
  - account-schema
topics:
  - workflow
  - tam-total-addressable-market
  - tier-architecture
  - account-schema
  - public-data-sources
related_concepts:
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[PUBLIC_DATA_SOURCES_TAM]]"
  - "[[SUBTIER_EXCLUSION_RULES]]"
  - "[[ACCOUNT_SCHEMA_EXTENDED]]"
  - "[[TAM_DEDUP_METHODOLOGY]]"
  - "[[COCM_CONFIDENCE_GRADE_RULES]]"
source:
  type: notes
  file: "Cursor conversation — GA pilot + fresh 1A/1B/1C list build (ingest)"
  date: "2026-04-07"
---

# Fresh list build runbook (1A / 1B / 1C)

[INFERRED: Internal operating decision — prioritize repeatable list math before outbound copy.]

This pattern describes **how to run** fresh subtier account lists (1A, 1B, 1C) without mixing concerns: **save opportunity sizing (`base_gap`) and persona routing first**; treat **pitch, messaging, and EDP-style narrative** as a **later** pass once accounts and personas are stable. Canonical definitions of subtiers, floors, exclusions, and public data sources live in linked methodology nodes; this node only encodes **workflow order, scope, and guardrails** for automation and agent sessions.

[INFERRED: Pilot geography — Georgia (GA) first — chosen to bound NPPES/CMS joins, Clay cost, and QA before multi-state or national scale.]

## Key Points

- **Phase split:** Persist **`base_gap`** (and related scoring such as confidence grade / CoCM tier) after `estimate-cocm` → `tier-accounts`; **defer EDP emphasis and messaging** until the account + persona graph is complete for the wave.
- **Scope:** Prefer **state-by-state or small multi-state pilots** (e.g. **GA first**) over a single “all 50 states” build; use fixed **row caps** per subtier for v1.
- **Three axes — do not conflate:** (1) **GTM subtier** (1A, 1B, 1C), (2) **`org_type`** in the CoCM engine (`solo_practice`, `independent_group`, `health_system_medical_group`, `aco_parent`), (3) **CoCM deployment tier** (Tier 1–4 from tiering). Store subtier in **`subtier_primary` / notes** when the schema supports it; see [[ACCOUNT_SCHEMA_EXTENDED]].
- **Live signals:** Use **`live-public`** for `estimate-cocm` **only when** local Part B signal files and org→NPI mapping are populated for the **in-scope** accounts; otherwise **stop and prep signals** — do not treat synthetic estimates as comparable for prioritization. Implementation detail: `tam_builder` live adapter reads under `data/public_signals/` (see repo `tam_builder/adapters.py`).
- **Pipeline order:** Raw CSV per subtier → `normalize-accounts` → (optional Clay) → `estimate-cocm` → `tier-accounts` → `route-personas`. Use **consistent artifacts** (e.g. `fresh_ga_1a.csv`) for traceability.
- **Dedup:** Follow [[TAM_DEDUP_METHODOLOGY]]; apply [[SUBTIER_EXCLUSION_RULES]] **before** heavy enrichment spend.

## Evidence

> "We're going to save the base gap; we're not worried about the EDP right now. Once we've generated all of the accounts and their specific personas associated with the accounts, let's then worry about how we're pitching and how we're messaging."  
> "For the first fresh build, pilot **Georgia only**; use **live-public** only if `data/public_signals/` is ready for in-scope NPIs/orgs, otherwise stop and prep those files first."

## Related Concepts

- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — Subtier definitions and PCP floors; context for 1A/1B/1C.
- [[PUBLIC_DATA_SOURCES_TAM]] — NPPES, CMS PAC, MSSP/REACH, and build sequence by subtier.
- [[SUBTIER_EXCLUSION_RULES]] — When to flag vs exclude before enrichment.
- [[ACCOUNT_SCHEMA_EXTENDED]] — Where subtier and account fields live in the normalized schema.
- [[TAM_DEDUP_METHODOLOGY]] — Keys and dedup across waves.
- [[COCM_CONFIDENCE_GRADE_RULES]] — How confidence and tiering relate to saved scores alongside `base_gap`.

## Production Validation

- [[WEEKLY_MOC_2026_05_04]] — Exercised at scale: LEC-41 (1A wedge taxonomy + NPPES proxy) and LEC-45 (cross-subtier baseline) shipped and run in `build_list_1a.py`
- [[WEEKLY_LINEAR_SHIPPED_2026_05_04]] — Execution node documenting list-build + launch week (includes LEC-41 / LEC-45); aligns with 1,219 leads loaded per weekly evidence
