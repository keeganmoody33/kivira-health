---
name: DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER
description: Starter discovery checklist for PCP-centric behavioral health + EHR-integrated CDS deals—maps to public integration and safety surfaces.
domain: methodology
node_type: pattern
status: validated
last_updated: 2026-05-11
tags:
  - methodology
  - discovery-calls
  - gtm-motion
topics:
  - buyer-diligence
  - workflow
related_concepts:
  - "[[GTM_MOTION_HYPOTHESIS]]"
  - "[[EHR_INTEGRATION_SMART_ON_FHIR]]"
  - "[[PRIMARY_CARE_WEDGE_ICP]]"
  - "[[PATIENT_APP_SAFETY_ALERTS]]"
source:
  type: document
  file: "raw-context/MARKETANALYSIS.md; internal GTM pattern"
  date: "2026-04-03"
---

# Discovery questions (primary care buyer)

Use these as a **pattern**, not a script—tailor to FQHC vs IDN vs community practice.

## Workflow & integration

- Which EHR (Epic/Cerner/athena/Other)? SMART on FHIR maturity? Who owns integration backlog?
- Where do behavioral health assessments live today (LMSW embedded, BH clinic only, paper)?
- How are **safety escalations** handled today for positive screens—who is paged, and within what SLA expectations? ([[PATIENT_APP_SAFETY_ALERTS]])

## Clinical governance

- Who signs off on **CDS** content and AI-assisted outputs—medical staff committee, QI, compliance?
- What language must appear in **patient-facing** materials per system policy?

## Economics

- Is budget **BH**, **primary care operations**, **digital/innovation**, or **IT**?
- Any **value-based** contracts influencing BH integration metrics?

## Evidence & procurement

- What proof is required for pilot → expansion (clinical outcomes, time savings, coding/reimbursement)?
- Standard **security** packet timing and redlines history?

## Related Concepts

- [[GTM_MOTION_HYPOTHESIS]] — Overall motion context.
- [[EHR_INTEGRATION_SMART_ON_FHIR]] — Technical depth to probe.
- [[PRIMARY_CARE_WEDGE_ICP]] — Why the buyer cares.
