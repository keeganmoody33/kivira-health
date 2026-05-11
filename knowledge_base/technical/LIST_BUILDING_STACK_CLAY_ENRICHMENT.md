---
name: LIST_BUILDING_STACK_CLAY_ENRICHMENT
description: List-building approach using Clay as an orchestration/enrichment layer, combined with public-data scraping and finite-TAM list hygiene.
domain: technical
node_type: workflow
status: draft
tags:
  - technical
  - outbound
  - data-enrichment
  - source-research-synthesis
  - gtm-tooling
related_concepts:
  - "[[COCM_ACCOUNT_PROFILE_SCHEMA]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
source:
  type: research-synthesis
  file: "raw-context/kivira-internal/jp-km-outbound-strategy-meeting-notes-2026-04-07.md"
  date: "2026-04-07"
---

# List-building stack: Clay + enrichment

[INFERRED: Treat list building as a finite-TAM build step: once a quality list exists per subtier/persona, it becomes a reusable asset; enrichment is layered on top.]

## Core pattern

- **Start** with a base table of accounts + target roles (by subtier).
- Use **Clay as an orchestration layer** to run enrichments from multiple providers via integrations.
- Export to downstream outreach tooling only after basic quality checks.

## Inputs

- **Account universe**: per subtier (e.g., Tier 1A / 1B / 1C)
- **Target roles**: use `[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]` to define demo-bookable titles and search strings
- **Public data** (optional): scrape publicly available sources when contact data is missing

## Enrichment approach

[INFERRED: Enrichment quality can only be validated once you attempt outreach; treat providers/trials as iterative and measured.]

- **Enrich contact fields**: email, phone, LinkedIn URL
- **Log provenance**: which provider/source populated which field
- **Measure deliverability**: feed results into `[[OUTREACH_BASELINE_METRICS]]` (bounce rates, reply rates by provider/source if possible)

## Budget note

[UNVERIFIABLE: A $400–$1,000 initial tooling budget range is discussed; treat as directional because vendor pricing changes frequently.]
