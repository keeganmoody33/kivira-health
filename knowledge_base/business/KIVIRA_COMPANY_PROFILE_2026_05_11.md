---
name: KIVIRA_COMPANY_PROFILE_2026_05_11
description: Single-doc synthesis of what Kivira is, what they offer, who they target, and who backs them — composed from public website + legal copy as of 2026-05-11.
domain: business
node_type: framework
status: emergent
last_updated: 2026-05-11
date: "2026-05-11"
tags:
  - business
  - kivira-profile
  - source-public-web
  - gtm-motion
topics:
  - market-positioning
  - team
  - credibility
related_concepts:
  - "[[PRIMARY_CARE_WEDGE_ICP]]"
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
  - "[[CLINICAL_INSTRUMENTS_SURFACE]]"
  - "[[PUBLIC_VALUE_PROPOSITION_HOME]]"
  - "[[B2B_CLINIC_BUYER_MODEL]]"
  - "[[POLSKY_UCHICAGO_KIVIRA_PROFILE_2026]]"
  - "[[PATIENT_APP_SAFETY_ALERTS]]"
  - "[[PRIVACY_AND_HIPAA_ROLE]]"
  - "[[KIVIRA_BACKER_COPY_SHIFT_2026_05]]"
  - "[[HEAT_EXCEPTION_EXTERNAL_VALIDATION]]"
source:
  type: document
  files:
    - "raw-context/kivira-public/www-home.md"
    - "raw-context/kivira-public/team.md"
    - "raw-context/kivira-public/instrument-overview.md"
    - "raw-context/kivira-public/legal-patient-app-terms.md"
    - "raw-context/kivira-public/legal-privacy-policy.md"
    - "raw-context/kivira-public/spider-www-home-2026-05-11.md"
  date: "2026-05-11"
---

# Kivira — Company Profile (snapshot 2026-05-11)

[VERIFIED: This synthesis composes from public marketing copy, legal documents, and a freshness-check Spider Cloud scrape on 2026-05-11. Every claim below traces to a `raw-context/kivira-public/` file listed in `source.files`.]

## What Kivira Is

A mental-health clinical decision support (CDS) product for primary care. Kivira combines **evidence-based screening + digital phenotyping + AI analytics** aligned with DSM-5 criteria, producing a **Clinical Advisory Report** that helps PCPs assess, screen, and surface high-risk indications (suicidal ideation, etc.) for the mental-health workload that increasingly lands in their offices. Outputs are **decision support** — not autonomous diagnosis — per the patient-app legal terms (see [[CDS_NOT_DIAGNOSIS_FRAMING]]).

**Tagline:** *"Solving mental health in primary care."* (`raw-context/kivira-public/www-home.md`)

## Who They're Focused On

**Wedge:** Primary care physicians as the de-facto front line of mental health. Marketing copy frames it directly: *"PCPs are now the front line of mental health and they can't keep up. Kivira gives them the clarity, confidence, and tools to diagnose and treat with precision."*

**Buyer model:** B2B sale to clinics and health systems; the patient app is **free to patients** per the patient-app terms — the revenue motion is institutional, not consumer (see [[B2B_CLINIC_BUYER_MODEL]] and [[PRIMARY_CARE_WEDGE_ICP]]).

**Operational segments (internal GTM):** Three priority segments under the wedge — see [[THREE_SEGMENT_ICP_FRAMEWORK]] and [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]. The public copy is wedge-only; the internal tier architecture sits below.

## The Three Public Value Pillars

| Pillar | Public claim |
|---|---|
| **Accuracy** | "Combine evidence-based screening, digital phenotyping, and AI analytics aligned with DSM-5 criteria to deliver accurate, reproducible mental-health diagnoses — improving treatment decisions and patient outcomes." |
| **Integrate** | "We fit directly into your existing EHR workflow. Screen and prescribe without extra steps — everything works naturally within how you already practice." |
| **Quality** | (same accuracy framing — public copy duplicates the "Accuracy" text under a "Quality" subhead) |

**Time-discounted accuracy claims** (PCP-facing marketing chart):

| Instrument | Claimed score |
|---|---|
| MINI | 27% |
| TTFNET | 27% |
| Y-BOCS | 65% (some renders show 69%) |
| PHQ-9 | 74% |
| GAD-7 | 82% |

[INFERRED: Marketing presentation; the underlying methodology / benchmark is not on the public site. Treat as "what Kivira claims" not "validated externally."]

## Clinical Credibility Surface

Kivira hosts a separate subdomain — `instrument-overview.kivira.health` — that lists **20 validated clinical instruments** in use within the product, each with a primary literature citation (see [[CLINICAL_INSTRUMENTS_SURFACE]]). Examples:

> AD8, AQ-10 (autism), AUDIT, DAST, GAD-7, HAMD-6, ISI, Mini-SPIN, PDSS, PHQ-9, SCOFF, TEPS, Y-BOCS, IIEF-15, FSFI, ASRS v1.1, C-SSRS Pediatric SLC, CAPE, Altman ASRM, ASEX.

The subdomain explicitly states: *"These tools are intended to support care, not to replace a clinician's judgment or provide a diagnosis by themselves."* — same CDS framing as the legal terms.

## Team

[VERIFIED: from 2026-04-03 `raw-context/kivira-public/team.md` (Spider HTTP-only re-pull on 2026-05-11 didn't capture team content due to Framer JS dynamic rendering — content unchanged at the rendered layer).]

**Leadership:**

| Role | Person | Public credential |
|---|---|---|
| Founder & CEO | Maria T Carmona, MBA | 3x tech founder, exited to PE, supported by Y Combinator |
| Chief Technology Officer | Matthew Vowels, PhD Eng., PhD Applied Math, MS, MSc | Machine Learning Engineer, 10+ years in healthcare ML |
| Chief Medical Director | Charles Nemeroff, MD, PhD | President of the Anxiety and Depression Association of America; board member of NIMH; former President of the American College of Psychiatrists |
| Chief Medical Officer | Teddy Akiki, MD | Professor at Stanford University; Co-Director of the Stanford Center for Precision Psychiatry |

**Medical Board:**

| Person | Public credential |
|---|---|
| Phil Harvey, MD, PhD | Cognitive assessment, outcomes measurement, NIH funding; top 1% of mental-health citation researchers every year since 2010 |
| Carol Alter, MD | Healthcare ops, EHR integration, reimbursement; collaborative care + behavioral-health-into-primary-care integration at scale |
| Jeff Newport, MD, MS | Pharmacological safety, precision prescribing; authority on high-risk psychiatric prescribing |
| Larry Kessler, MD, FACP | PCP strategy, American Board of Internal Medicine; 40+ years primary care; bridges clinical / industry / regulatory |

## Backers

**Current (2026-05-11):** *"Backed by Antler & major healthcare systems"* (per `raw-context/kivira-public/spider-www-home-2026-05-11.md`).

**Prior (2026-04-06):** *"Backed by Y Combinator & Antler"* (per `raw-context/kivira-public/www-home.md`).

[INFERRED: Backer copy shift between April and May. "Y Combinator" framing dropped from public marketing; "major healthcare systems" added — see [[KIVIRA_BACKER_COPY_SHIFT_2026_05]] for the signal node tracking this delta. Whether this represents new health-system investment, a partnership/pilot framing, or a marketing-only tweak is unverified.]

## Press / External Validation

- Public **press page** at `kivira.health/press` was a placeholder (*"Content inbound…"*) in both the 2026-04-06 and 2026-05-11 scrapes. No press content yet on Kivira's own site.
- External profile: Polsky Center (University of Chicago Booth) published a 2026 profile of Kivira — see [[POLSKY_UCHICAGO_KIVIRA_PROFILE_2026]]. Strategic publicity vector even though the inbound count in the graph is low.

## Legal / Regulatory Posture

- **Clinical decision support, not autonomous diagnosis.** Patient terms §5 and privacy policy §5 both explicitly state outputs *"support human decision-making and do not replace clinical judgment"* — see [[CDS_NOT_DIAGNOSIS_FRAMING]]. **External marketing must align with this framing.**
- **PHI / HIPAA posture:** see [[PRIVACY_AND_HIPAA_ROLE]] for how PHI is described to buyers.
- **Patient-app safety surface:** safety workflows are scoped per [[PATIENT_APP_SAFETY_ALERTS]] (the suicidal-ideation flow on the marketing sample is the canonical example).

## Public Web Surface (as of 2026-05-11)

| URL | Status |
|---|---|
| `https://www.kivira.health/` | Marketing home — content unchanged since April except backer copy |
| `https://www.kivira.health/team` | Leadership + medical board (4/3 scrape is source of truth) |
| `https://www.kivira.health/press` | Still a placeholder — no press articles yet |
| `https://www.kivira.health/contact` | Demo / inquiry form |
| `https://www.kivira.health/legal/patient-app-terms-and-conditions` | Patient app ToS — last refresh 4/6 |
| `https://www.kivira.health/legal/privacy-policy` | Privacy policy — last refresh 4/6 |
| `https://instrument-overview.kivira.health/` | 20 clinical instruments + primary refs |
| `https://www.linkedin.com/company/kivira/` | LinkedIn company page |

## What This Synthesis Is For

- **Onboarding:** "Read this first" doc for anyone new to the Kivira GTM context.
- **Investor / partner comms:** Single source for "what does Kivira do" framing that doesn't require reading 8 raw scrapes.
- **GTM guard-rail:** When drafting outbound or messaging, cross-check claims against the source files listed in `source.files`. If a claim doesn't trace, flag `[UNVERIFIABLE]` per [[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]].

## Refresh Cadence

Re-run the Spider Cloud freshness check monthly (or before any major comms cycle). If `Backed by …` copy, value-pillar copy, or accuracy claims shift, mint a new dated profile and link from `KIVIRA_COMPANY_PROFILE_2026_05_11` → `KIVIRA_COMPANY_PROFILE_<next-date>` as a versioned chain.
