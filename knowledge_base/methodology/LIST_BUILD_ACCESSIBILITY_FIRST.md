---
name: LIST_BUILD_ACCESSIBILITY_FIRST
description: List-build and scrape optimization prioritizes reachable channels (website, NPPES endpoint, phone) before subtier-only filtering; subtier drives message fit, not crawl viability.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - workflow
  - gtm-motion
  - tam-total-addressable-market
topics:
  - workflow
  - gtm-motion
  - tam-total-addressable-market
related_concepts:
  - "[[PUBLIC_DATA_SOURCES_TAM]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[LIST_BUILDING_STACK_CLAY_ENRICHMENT]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OPERATIONAL_LIST_VS_STRATEGIC_TAM]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
source:
  type: notes
  file: "agent-transcript/70fb541d-c48a-4f21-954d-63f15e578d3c"
  date: "2026-05-22"
---

# List build: accessibility-first (not subtier-first)

For the repo GTM pipeline (`01_seed` → `08_campaign_export`), **crawl and enrichment budget should follow accounts that have a reachable channel**, not a subtier label alone. Subtier remains essential for **ICP fit, persona mapping, and message** ([[GTM_TIER_ARCHITECTURE_9_SUBTIERS]], [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]); it does not create URLs or emails by itself.

[INFERRED: GA pilot runs in agent session 2026-05-22 — stages 03–06 produced 0% URL/email/persona when seed `website` was empty.]

## Key points

- **Subtier filter controls volume, not accessibility.** Expanding Georgia from Tier 1A only to all nine subtiers increases row count but does not fix discovery if `website` and evidence URLs are blank at seed.
- **Seed must populate channels early.** [[PUBLIC_DATA_SOURCES_TAM]] lists NPPES core + **endpoint** files; joining `endpoint_pfile_*.csv` (and/or other registries) into `01_seed_accounts_by_state.py` is higher leverage than re-scoping subtier before URLs exist.
- **Phone can bypass web for some paths.** Classifier output can carry `phone_main` from seed; persona and wave gates may still require email/LinkedIn—treat phone as partial accessibility, not full wave-ready.
- **Pilot metrics before threshold tuning.** Per-stage % with URL, email, persona, `demo_bookable`, `wave_ready` (see `scripts/validate_pipeline_outputs.py`) should gate whether to raise crawl budget vs relax [[WAVE_1_SCORING_FRAMEWORK]] thresholds.
- **Split exports when needed.** When scrape yield is low, export **research_queue** contacts separately from **send_ready** rather than forcing all rows through wave inclusion.

## Failure mode observed (GA)

| Stage | Symptom when `website` empty |
|-------|------------------------------|
| 03 discover | No real crawl targets; fast pass with no evidence |
| 04 extract | Evidence = 0; no email/phone from pages |
| 05–06 | No persona / all excluded from wave lists |

[INFERRED: Pilot output under `output/pilot/` after GA Tier 1A classify — ~52k rows, 0% channel fill through wave export.]

## Recommended order of operations

1. Fix **channel at seed** (NPPES endpoint URL, website field, phone).
2. Filter operational cohort to **has_url OR has_phone OR enrichment_pending** before HTTP crawl budget.
3. Apply **subtier + state + size** for message and prioritization.
4. Tune scoring thresholds only after stage metrics show non-zero accessibility.

## Evidence

> "Is it better to focus on all 9 subtiers in Georgia instead of Tier 1A only, and optimize scraping/workflow?" — strategic question; answer: broaden subtiers only after accessibility layer works.

## Related concepts

- [[PUBLIC_DATA_SOURCES_TAM]] — NPPES + endpoint as primary free stack
- [[LIST_BUILDING_STACK_CLAY_ENRICHMENT]] — enrichment when public scrape insufficient
- [[OPERATIONAL_LIST_VS_STRATEGIC_TAM]] — GA NPPES row counts ≠ national logo TAM
- [[WAVE_1_SCORING_FRAMEWORK]] — wave inclusion after data exists
