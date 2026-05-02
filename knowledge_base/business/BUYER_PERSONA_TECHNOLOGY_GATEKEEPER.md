---
name: BUYER_PERSONA_TECHNOLOGY_GATEKEEPER
description: Dr. Marcus A. archetype - CMIO/VP Clinical Informatics who approves or blocks integration based on architecture, security, and workflow burden.
domain: business
node_type: concept
status: validated
last_updated: 2026-04-06
tags:
  - business
  - buyer-persona
  - b2b-health-system
  - source-research-synthesis
topics:
  - buyer-persona
  - ehr-integration
  - buyer-diligence
  - compliance
related_concepts:
  - "[[BUYER_PERSONA_CLINICAL_CHAMPION]]"
  - "[[BUYER_PERSONA_OPERATIONAL_BUYER]]"
  - "[[BUYING_COMMITTEE_DYNAMICS]]"
  - "[[EHR_INTEGRATION_SMART_ON_FHIR]]"
  - "[[PRIVACY_AND_HIPAA_ROLE]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# Buyer Persona: The Technology Gatekeeper

**Archetype:** Dr. Marcus A. — Chief Medical Information Officer (CMIO) / VP Clinical Informatics

[VERIFIED: Pattern synthesized from LinkedIn profiles, AMIA membership patterns, HIMSS attendance data]

## Professional Snapshot

Began as an internist with technology interest, completed NLM fellowship in biomedical informatics, and pursued executive MBA. Title evolution through the CMIO lifecycle: entered informatics in 1.0 role (EHR adoption, CPOE), matured into 2.0 (care coordination, decision support governance), now in 3.0/4.0 territory—leading AI adoption strategy, governing CDS algorithms, managing Epic optimization at enterprise level.

**Profile markers:**
- LinkedIn activity features posts about Epic Gold Stars, SMART on FHIR implementation challenges, AI governance
- AMIA (American Medical Informatics Association) member
- HIMSS annual attendee
- Team of 15–25 informatics physicians, clinical analysts, project managers, Epic build specialists

**Compensation:** $310,000–$450,000

**Real-world analog:** Hasan Ahmad, VP Associate CMIO at Parkview—leading enterprise inpatient Epic rollout, building CDS governance using "Clickbusters" principles, overseeing ambient documentation adoption (Microsoft DAX Copilot).

## Daily Reality

| Day | Activities |
|-----|------------|
| Monday AM | EHR governance steering committee—reviewing backlog of CDS alert requests from 12 service lines, each convinced their alert is most important |
| Tuesday | Three vendor demos in pipeline; assigned clinical analyst to score each against 40-point requirements matrix (HIPAA, FHIR conformance, Epic integration architecture, security certs) |
| Wednesday | Quarterly CISO briefing—reviewing BAA portfolio and third-party risk assessments; new AI vendor = new security review cycle |
| Thursday | Working session with Epic consultants on SMART on FHIR app integration—previous one took 14 weeks and three escalations |
| Friday | Department review—reports to CMO and CFO on digital health ROI; needs numbers, not narratives |

**His KPIs:**
- Clinical alert acceptance rate (target: >65%; often far lower due to alert fatigue)
- EHR integration uptime and error rates
- Time-to-live for new clinical applications
- HIPAA/security incident count
- Physician technology satisfaction scores
- AI governance compliance metrics

**Vendor landscape experience:** He has been burned before. A digital health vendor promised seamless Epic integration; implementation took 9 months, broke two existing workflows, tool was quietly sunset within 18 months. Now requires a reference call with a health system of comparable size before any integration moves to contract.

## Decision Driver Analysis

Dr. Marcus is a **"show me the architecture" buyer**. His evaluation process is methodical and non-negotiable.

**Evaluation checklist:**
1. **Integration architecture review:** Wants SMART on FHIR implementation specs, OAuth scopes, data flows, write-back capabilities documented before second demo. Kivira's explicit SMART on FHIR and HL7 posture—and Epic MyChart invitation route—is a strong early credential.
2. **Security and compliance package:** HIPAA BAA templates, SOC 2 Type II or HITRUST certification, data governance document are table stakes. 42 CFR Part 2 mapping is a bonus signaling vendor maturity.
3. **FDA regulatory positioning:** Will ask directly: "Is this a medical device? Do you have FDA clearance?" Kivira's CDS-only framing must be defensible, not vague. May consult in-house legal if answer is ambiguous.
4. **AI model governance:** Wants to know how AI models are updated, how model drift is monitored, whether there is a Predetermined Change Control Plan (PCCP) or equivalent. After a year of high-profile AI incidents, this is now standard diligence.
5. **Alert fatigue modeling:** Will ask how many alerts/notifications the tool generates per provider per day. Any tool that adds net alert volume without corresponding reduction elsewhere will be deprioritized.
6. **Reference check:** Will personally call the CMIO or informatics director at Wellstar or any other live deployment site.

**Veto power is real.** Even if Dr. Jennifer is enthusiastic, Dr. Marcus can delay or kill a deal by declaring integration timeline infeasible for current Epic release cycle, or flagging unresolved security issues.

**What accelerates approval:** A vendor who arrives to first technical call with pre-completed HIPAA compliance summary, FHIR conformance statement, and 2-page integration architecture diagram. This signals "we have done this before and we respect your time."

## Communication Profile

**Preferred channels:** Email for formal requests; Slack or Teams for rapid coordination with informatics team; in-person or video for complex architecture walkthroughs

**Content he consumes:** HIMSS white papers, JAMIA articles on CDS implementation, Epic UserWeb, KLAS Research vendor reports. AMIA newsletter subscriber. Follows @HealthITSecurity on social.

**Red flags:** Vendors who say "Epic integration is easy" (it isn't), who cannot produce data flow diagram on request, who dodge FDA classification questions

**Meeting preference:** Technical working sessions with his informatics team present, not executive-to-executive pitches. Wants vendor's implementation lead in the room, not just sales rep.

**Follow-up cadence:** Weekly status updates during active evaluation; will disengage from vendors who send generic email sequences rather than tailored technical responses

## Professional Motivation Map

**Career driver:** Wants to be known as the CMIO who built a scalable, safe AI governance framework—not the CMIO who approved a tool that made national headlines for a clinical AI failure. Legacy goal: enterprise-level clinical informatics capability that outlasts his tenure.

**Recognition currency:** Professional reputation within AMIA and HIMSS; invitations to present at Epic UGM; being referenced in KLAS Research commentary as a leader who "did AI governance right."

**Fear that shapes decisions:** Signing a BAA with a vendor that subsequently mishandles PHI or deploys a biased AI model without adequate fairness monitoring. Not abstract—he has watched peers navigate OCR investigations and class-action exposure after vendor breaches.

**Personal values:** Clinical safety, physician experience (still a clinician at heart, knows exactly what alert fatigue does to physicians), principle that technology should reduce cognitive burden of care delivery, not add to it.

## Trigger to Yes

**Strongest proof point:** FHIR conformance statement + HITRUST cert + Epic sandbox access provided at first technical call

**Fastest path to champion:** Provide pre-completed integration architecture docs before they ask

**Most common deal-killer:** Integration timeline slippage or unresolved security review

## Related Concepts

- [[BUYER_PERSONA_CLINICAL_CHAMPION]] — Clinical champion who initiates the deal
- [[BUYER_PERSONA_OPERATIONAL_BUYER]] — Operational buyer who validates ROI
- [[BUYING_COMMITTEE_DYNAMICS]] — How the three personas move together
- [[EHR_INTEGRATION_SMART_ON_FHIR]] — The integration story he evaluates
- [[PRIVACY_AND_HIPAA_ROLE]] — Compliance framing he requires
