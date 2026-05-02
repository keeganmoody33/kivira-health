---
name: COCM_PUBLIC_ESTIMATE_ENGINE_V2
description: Internal reference engine for modeled CoCM opportunity estimation using public Medicare and NPPES signals, with explicit caveats and persona messaging.
domain: technical
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - technical
  - collaborative-care-cocm
  - cpt-billing-codes
  - source-internal-doc
topics:
  - cpt-billing-codes
  - fee-for-service-ffs
  - buyer-diligence
related_concepts:
  - "[[CPT_BILLING_CODES_BHI]]"
  - "[[DIRECT_BILLING_MODEL_FFS]]"
  - "[[COCM_ACCOUNT_PROFILE_SCHEMA]]"
  - "[[COCM_CONFIDENCE_GRADE_RULES]]"
source:
  type: document
  file: "raw-context/kivira-internal/kivira-cocm-estimate-engine-v2-2026-04-05.md"
  date: "2026-04-05"
---

# CoCM Public Estimate Engine v2

This internal source defines the current reference architecture for the CoCM opportunity workflow. It is explicitly a **modeled public-signal engine**, not an audited revenue calculator.

## What it does

- Resolves organization identity from public NPPES data.
- Searches PCP candidates by geography and taxonomy.
- Pulls public Part B signals for G0444, 96127, CoCM, and related codes.
- Applies org-type-specific scenario assumptions.
- Emits conservative/base/aggressive gap estimates plus a confidence grade.
- Generates persona-specific messaging with public-data caveats built in.

## Operational implications

- The output is useful for ranking, routing, and discovery prep.
- It is **not** sufficient to support hard claims without grade-aware guardrails.
- The export contract in the source PDF should remain stable in repo-local tooling: JSON summary, one-row CSV summary, and provider debug CSV.

## Guardrails

- Public Medicare FFS only.
- Excludes MA, commercial, Medicaid, and uninsured.
- Provider-to-organization affiliation is inferred, not guaranteed.
- Missing CoCM rows can mean no visibility or CMS suppression.

## Related Concepts

- [[CPT_BILLING_CODES_BHI]] - Coding surfaces the engine relies on
- [[DIRECT_BILLING_MODEL_FFS]] - Revenue narrative built on similar logic
- [[COCM_ACCOUNT_PROFILE_SCHEMA]] - Input contract for the workflow
- [[COCM_CONFIDENCE_GRADE_RULES]] - How output trust is tiered
