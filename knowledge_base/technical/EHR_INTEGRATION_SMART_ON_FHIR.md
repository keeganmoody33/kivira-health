---
name: EHR_INTEGRATION_SMART_ON_FHIR
description: Public documentation highlights SMART on FHIR / HL7-class integration, Epic MyChart invitation OAuth (PKCE), and clinic-configured data flows.
domain: technical
node_type: concept
status: validated
last_updated: 2026-05-11
tags:
  - technical
  - ehr-integration
  - smart-on-fhir
  - source-public-web
topics:
  - buyer-diligence
  - workflow
related_concepts:
  - "[[B2B_CLINIC_BUYER_MODEL]]"
  - "[[PRIVACY_AND_HIPAA_ROLE]]"
  - "[[CLINICAL_INSTRUMENTS_SURFACE]]"
source:
  type: document
  file: "raw-context/kivira-public/legal-patient-app-terms.md; raw-context/kivira-public/legal-privacy-policy.md"
  date: "2026-04-03"
---

# EHR integration (SMART on FHIR / HL7)

Legal docs describe integration with EHRs **via SMART on FHIR, HL7, or similar methods**. The **Epic MyChart invitation route** uses OAuth 2.0 authorization code flow with PKCE; Kivira does **not** receive the MyChart password. [VERIFIED: patient app terms §4, §9, §10.]

## Key Points

- Security questionnaires will ask about scopes, token handling, and BAAs—pair with [[PRIVACY_AND_HIPAA_ROLE]].
- Non-Epic email invitation route also documented for completeness in enterprise discovery.

## Evidence

> "You authenticate via MyChart using Epic SMART on FHIR OAuth 2.0 authorization code flow with PKCE. Kivira does not receive your MyChart password."
> [SOURCE: Patient App Terms — Invitations, Accounts, and Authentication]

## Related Concepts

- [[B2B_CLINIC_BUYER_MODEL]] — Who procures and configures integrations.
- [[PRIVACY_AND_HIPAA_ROLE]] — HIPAA BA status when integrated.
- [[CLINICAL_INSTRUMENTS_SURFACE]] — What clinical content flows through the pipe.
