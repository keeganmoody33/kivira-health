---
name: COCM_ACCOUNT_PROFILE_SCHEMA
description: Internal schema for account-level inputs to the CoCM opportunity workflow, including org identity, org type, persona priorities, and candidate-search bounds.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - methodology
  - workflow
  - gtm-motion
  - source-internal-doc
topics:
  - workflow
  - buyer-diligence
  - gtm-motion
related_concepts:
  - "[[COCM_PUBLIC_ESTIMATE_ENGINE_V2]]"
  - "[[ORG_TYPE_BUYER_MAP_COCM]]"
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
  - "[[COCM_OUTREACH_SEQUENCING]]"
source:
  type: document
  file: "raw-context/kivira-internal/kivira-deployment-guide-cocm-2026-04-05.md"
  date: "2026-04-05"
---

# CoCM Account Profile Schema

The deployment guide defines a minimal but durable account schema for CoCM/TAM work. Every account needs a clear organizational identity plus enough routing metadata to determine assumptions, personas, and search breadth.

## Required input fields

- `org_name`
- `state`
- `city` or `None`
- `org_type`
- `priority_personas`
- `max_candidates`
- `notes`

## Why it matters

- `org_type` controls both modeling assumptions and buyer routing.
- `priority_personas` determines which outputs should be surfaced first.
- `max_candidates` is a runtime and coverage control, not just a convenience field.

## Implementation rule

Repo-local tooling should normalize arbitrary CSV headers into this schema first, then add enrichment, observed signals, modeled outputs, and outbound eligibility as later-stage fields.

## Related Concepts

- [[COCM_PUBLIC_ESTIMATE_ENGINE_V2]] - Engine that consumes the schema
- [[ORG_TYPE_BUYER_MAP_COCM]] - Persona routing depends on org type
- [[THREE_SEGMENT_ICP_FRAMEWORK]] - Strategic segment lens for account selection
- [[COCM_OUTREACH_SEQUENCING]] - Downstream execution uses these fields
