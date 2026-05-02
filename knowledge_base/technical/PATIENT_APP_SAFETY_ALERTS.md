---
name: PATIENT_APP_SAFETY_ALERTS
description: Self-harm risk may trigger provider notification (clinic-configured) and optional crisis resource emails; explicitly not real-time monitoring or emergency care.
domain: technical
node_type: pattern
status: emergent
last_updated: 2026-04-03
tags:
  - technical
  - safety-risk-notification
  - patient-app
  - source-public-web
topics:
  - compliance
  - workflow
related_concepts:
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
  - "[[PRIVACY_AND_HIPAA_ROLE]]"
  - "[[PRIMARY_CARE_WEDGE_ICP]]"
source:
  type: document
  file: "raw-context/kivira-public/legal-patient-app-terms.md; raw-context/kivira-public/legal-privacy-policy.md"
  date: "2026-04-03"
---

# Patient app safety alerts

Terms and privacy policy describe **automatic notification to the patient’s healthcare provider** when responses indicate **risk of self-harm**, per clinic configuration, plus optional **crisis resource emails**. Both emphasize **no continuous/real-time monitoring** and that the app is **not for emergencies** (911 directive). [VERIFIED: patient terms §6–7; privacy §4, Safety alerts.]

## Key Points

- Implementation details (latency, escalation paths) are **clinic-configured**—do not promise instantaneous response in GTM materials.
- Align crisis language with legal copy in all patient-facing collateral reviews.

## Evidence

> "These notifications and emails are informational safety support only. They are not emergency care, are not continuously monitored, and are not guaranteed to be immediate."
> [SOURCE: Patient App Terms — Safety Alerts and Crisis Resource Emails]

## Related Concepts

- [[CDS_NOT_DIAGNOSIS_FRAMING]] — Clinical responsibility remains with licensed clinicians.
- [[PRIVACY_AND_HIPAA_ROLE]] — How safety processing intersects data use disclosures.
- [[PRIMARY_CARE_WEDGE_ICP]] — PCP workflows receive escalations.
