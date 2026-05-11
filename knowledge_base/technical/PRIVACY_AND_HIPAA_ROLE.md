---
name: PRIVACY_AND_HIPAA_ROLE
description: Privacy policy states HIPAA Business Associate role for EHR-integrated processing; limits on advertising, sale, and broker sharing; AI-assisted features with human review emphasis.
domain: technical
node_type: framework
status: validated
last_updated: 2026-05-11
tags:
  - technical
  - patient-app
  - source-public-web
topics:
  - compliance
  - buyer-diligence
related_concepts:
  - "[[EHR_INTEGRATION_SMART_ON_FHIR]]"
  - "[[PATIENT_APP_SAFETY_ALERTS]]"
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
source:
  type: document
  file: "raw-context/kivira-public/legal-privacy-policy.md"
  date: "2026-04-03"
---

# Privacy, HIPAA, and data use (public)

Privacy policy covers websites, patient app, clinician tools, admin, and EHR integrations. When integrated with EHRs, Kivira acts as a **HIPAA Business Associate** under BAAs. The policy states **no targeted advertising**, **no sale** of personal information, and **no data broker** sharing. [VERIFIED: privacy policy §3, §4, §6 openings.]

AI-assisted features are described as supporting providers, with **human review** emphasized for recommendations. [VERIFIED: privacy policy §5.]

## Key Points

- Security reviews will map subprocessors and cross-border processing disclosures in the full policy text.
- Pair with legal for **DPAs/BAAs** before quoting externally.

## Evidence

> "When Kivira integrates with EHR systems, we act as a HIPAA Business Associate under Business Associate Agreements with healthcare providers."
> [SOURCE: Privacy Policy — Health and sensitive information]

## Related Concepts

- [[EHR_INTEGRATION_SMART_ON_FHIR]] — Where PHI enters/exits.
- [[PATIENT_APP_SAFETY_ALERTS]] — Safety-related uses of information.
- [[CDS_NOT_DIAGNOSIS_FRAMING]] — Clinical + AI disclosure alignment.
