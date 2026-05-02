---
name: ACCOUNT_SCHEMA_EXTENDED
description: Extended 40+ field account schema for Kivira TAM building - core ID, tier classification, tech signals, scoring, and dedup logic.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - methodology
  - workflow
  - gtm-motion
  - source-research-synthesis
topics:
  - workflow
  - buyer-diligence
  - gtm-motion
  - tam-total-addressable-market
related_concepts:
  - "[[COCM_ACCOUNT_PROFILE_SCHEMA]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[TAM_DEDUP_METHODOLOGY]]"
  - "[[PUBLIC_DATA_SOURCES_TAM]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# Extended Account Schema (40+ Fields)

Canonical schema for Kivira CRM/list building. Use as field spec for spreadsheet, Airtable, Clay table, or CRM object.

[VERIFIED: Field structure derived from CoCM wedge analysis and TAM methodology research]

## Core Identification Fields

| Field | Type | Notes |
|-------|------|-------|
| `account_id` | String (UUID) | Internal unique key |
| `parent_org_id` | String | Dedup anchor. Parent system/network name. |
| `org_name` | String | Operating entity name |
| `org_aliases` | Array | DBAs, prior names, abbreviations |
| `website` | URL | Primary domain |
| `hq_state` | String | Two-letter state code |
| `hq_city` | String | City |
| `hq_metro` | String | Metro area (e.g., Atlanta-Sandy Springs-Alpharetta) |
| `employee_count` | Integer | Staff headcount, not just clinicians |
| `clinician_count_est` | Integer | Estimated active clinicians |
| `pcp_count_est` | Integer | Estimated primary care physicians specifically |

## Tier & Segment Classification

| Field | Type | Notes |
|-------|------|-------|
| `subtier_primary` | Enum | 1A, 1B, 1C, 2A, 2B, 2C, 3A, 3B, 3C |
| `subtier_secondary_tags` | Array | e.g., ["2A_aco_affiliated", "3A_health_system"] for overlap accounts |
| `care_setting` | Enum | ambulatory, mixed_ambulatory_inpatient, inpatient_dominant, virtual, community_health |
| `risk_model` | Enum | fee_for_service, shared_savings, downside_risk, global_capitation, mixed, unknown |
| `vbc_contract_types` | Array | e.g., ["MSSP", "ACO_REACH", "MA_capitation", "PCMH"] |
| `payer_mix_dominant` | Enum | commercial, medicare, medicaid, mixed, ma_heavy, unknown |
| `aco_participant` | Boolean | |
| `aco_name` | String | Name of ACO if participant |
| `aco_model` | Enum | MSSP, ACO_REACH, PC_Flex, other, N/A |
| `pcmh_recognized` | Boolean | NCQA PCMH recognition |
| `bhi_distinction` | Boolean | NCQA Behavioral Health Integration distinction |
| `cocm_active` | Boolean | Collaborative Care Model billing active |
| `cocm_evidence` | Enum | confirmed, inferred, unknown |

## Technology & Integration Signals

| Field | Type | Notes |
|-------|------|-------|
| `ehr_platform` | Enum | Epic, Oracle_Cerner, athenahealth, eClinicalWorks, Greenway, MEDITECH, NextGen, other, unknown |
| `ehr_version` | String | Version if known |
| `smart_on_fhir_likely` | Boolean | Inferred from EHR platform + size |
| `ambient_ai_deployed` | Boolean | Abridge, DAX Copilot, Ambience, etc. |
| `ambient_ai_vendor` | String | Vendor name if known |
| `mh_tool_current` | String | Current mental health screening or CDS tool if known |
| `mh_tool_type` | Enum | paper_only, basic_ehr_alert, measurement_platform, ai_cds, none_identified, unknown |

## Size & Commercial Signals

| Field | Type | Notes |
|-------|------|-------|
| `owned_clinic_count` | Integer | |
| `site_count_est` | Integer | Including affiliated/managed sites |
| `covered_lives_estimate` | Integer | For payer/ACO-adjacent accounts |
| `annual_mh_encounters_est` | Integer | Estimated mental health–relevant PCP visits per year |
| `cocm_revenue_gap_est` | Enum | high, medium, low, unknown — based on size × payer mix |
| `health_system_affiliate` | String | Parent health system if employed/affiliated group |
| `investment_backed` | Boolean | PE/VC-backed org |
| `investor_name` | String | If known |

## Scoring & Prioritization

| Field | Type | Notes |
|-------|------|-------|
| `pilot_feasibility_score` | Float (0–10) | Composite of EHR fit, org size, VBC signal, BH readiness |
| `buyer_complexity_score` | Float (0–10) | Higher = more stakeholders, longer cycle |
| `pain_intensity_score` | Float (0–1) | Maps to EDP segment |
| `outreach_priority` | Enum | wave_1, wave_2, wave_3, hold, disqualified |
| `account_stage` | Enum | uncontacted, researched, contacted, responded, meeting_set, pilot_discussion, contract, customer |
| `last_touched_date` | Date | |
| `source` | String | How account entered list (e.g., CMS_MSSP_PUF, NCQA_BHI, LinkedIn, manual) |
| `data_confidence` | Enum | high, medium, low |
| `notes` | Text | Free-form research notes |

---

## TAM Deduplication Logic

Follow this five-step sequence to produce clean numbers:

### Step 1 — Count unique logos per subtier
Pull all unique `org_name` + `hq_state` combinations within each subtier.

### Step 2 — Assign `parent_org_id`
For every account belonging to a larger system (e.g., provider group employed by health system, ACO run by health system), assign the same `parent_org_id`. Affiliated entities share a parent; independent entities are their own parent.

### Step 3 — Apply `subtier_primary` + `subtier_secondary_tags`
If an account could fit two subtiers, assign the most specific or highest-priority fit as `subtier_primary` and tag the secondary relationship.

**Example:** A provider group in an MSSP ACO is 1C primary, 2A secondary — not two logos.

### Step 4 — Score each unique logo
Use `pilot_feasibility_score` (0–10) and `buyer_complexity_score` (0–10). Accounts scoring ≥7 feasibility and ≤5 complexity are Wave 1.

### Step 5 — Roll up to three TAM views

| View | Definition | Use |
|------|------------|-----|
| **Logo TAM** | Unique `parent_org_id` count by subtier | Strategy / board |
| **Reachable Pilot TAM** | Logos with `pilot_feasibility_score` ≥ 7 and identified Wave 1 contact | Outbound now |
| **Expandable TAM** | Logos that could expand to additional sites/covered lives | Series A narrative |

Report all three separately. Never collapse them into one number for internal planning.

---

## Implementation Rule

Repo-local tooling should normalize arbitrary CSV headers into this schema first, then add enrichment, observed signals, modeled outputs, and outbound eligibility as later-stage fields.

## Related Concepts

- [[COCM_ACCOUNT_PROFILE_SCHEMA]] — Minimal schema for CoCM workflow (subset)
- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — Subtier definitions
- [[TAM_DEDUP_METHODOLOGY]] — Dedup logic detail
- [[PUBLIC_DATA_SOURCES_TAM]] — Where to source account data
