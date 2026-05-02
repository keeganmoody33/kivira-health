# GTM plan — Kivira (v1.1, ~20-minute read)

**Purpose:** Single synthesis for new GTM hires. Details live in `knowledge_base/` nodes—follow `[[wiki-links]]` before editing this file.

---

## 1. Market Position

- **Stage:** Late Early Adoption → Early Majority crossing (2026–2027 window) ([[MARKET_ADOPTION_STAGE_2026]])
- **Existential Data Point:** CoCM Revenue Realization Rate — % of eligible MH encounters billed under CPT 99492–99494 ([[EDP_COCM_REVENUE_REALIZATION]])
- **Why now:** Healthcare AI adoption surged 7× YoY; ambient documentation wave built organizational AI muscle; CMS AI CPT codes expected 2026

## 2. Segment & ICP

- **Wedge:** Mental health in **primary care** ([[PRIMARY_CARE_WEDGE_ICP]]).
- **Buyer:** **B2B** clinic/health system; patient app **free** to patients ([[B2B_CLINIC_BUYER_MODEL]]).
- **Strategic segments:** ([[THREE_SEGMENT_ICP_FRAMEWORK]]) → operationalized as 9 subtiers ([[GTM_TIER_ARCHITECTURE_9_SUBTIERS]])
- **Pain-based priority:** CoCM Cap-Maxed Systems (0.95) > VBC ACOs (0.85) > Ambient AI Graduates (0.70) ([[PAIN_SEGMENT_MATRIX]])
- **Champion map:** See Section 3 below

## 3. Buying Committee

Three personas dominate every deal ([[BUYING_COMMITTEE_DYNAMICS]]):

| Persona | Role | Primary Motivation | Trigger to Yes |
|---------|------|-------------------|----------------|
| **Clinical Champion** ([[BUYER_PERSONA_CLINICAL_CHAMPION]]) | Medical Director, IBH | Clinical outcomes & patient safety | Peer reference call + co-author offer |
| **Technology Gatekeeper** ([[BUYER_PERSONA_TECHNOLOGY_GATEKEEPER]]) | CMIO / VP Clinical Informatics | Workflow integrity & EHR governance | Pre-completed FHIR docs + HITRUST cert |
| **Operational Buyer** ([[BUYER_PERSONA_OPERATIONAL_BUYER]]) | Director BH Services / VP Pop Health | CoCM revenue capture & efficiency | ROI one-pager with CoCM billing math |

**Sequence:** Operator first → Clinical champion second → Economic buyer once pain validated.

## 4. Value proposition (external)

- Marketing home emphasizes screening + digital phenotyping + AI/DSM-5-aligned analytics + EHR fit ([[PUBLIC_VALUE_PROPOSITION_HOME]]).
- **Legal/clinical frame:** CDS, not replacement of judgment ([[CDS_NOT_DIAGNOSIS_FRAMING]]).
- **Proof surfaces:** Named instruments + citations page ([[CLINICAL_INSTRUMENTS_SURFACE]]); avoid conflating with product outcome studies ([[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]]).

## 5. Differentiation & diligence risks

- **Integration story:** SMART on FHIR, Epic MyChart OAuth (PKCE), clinic configuration ([[EHR_INTEGRATION_SMART_ON_FHIR]]).
- **Safety story:** Provider notifications + crisis emails, **not** real-time monitoring ([[PATIENT_APP_SAFETY_ALERTS]]).
- **Trust/compliance:** HIPAA BAA framing, AI disclosures, no ads/sale/broker claims per public privacy policy ([[PRIVACY_AND_HIPAA_ROLE]]).
- **Diligence gap:** Kivira-specific clinical validation still thin in public sources—prepare roadmap slide ([[COMPETITIVE_EVIDENCE_GAP]]).

## 6. TAM Building & Outreach

**Tier architecture:** 9 subtiers across 3 tiers ([[GTM_TIER_ARCHITECTURE_9_SUBTIERS]])

| Tier | Subtiers | Motion |
|------|----------|--------|
| **Tier 1** — Provider wedge | 1A Mid-market groups, 1B PCP groups, 1C VBC providers | Email + phone, pilot |
| **Tier 2** — Risk-bearing | 2A ACOs, 2B VBC enablers, 2C Care mgmt cos | Direct + channel |
| **Tier 3** — Enterprise | 3A Health systems, 3B IDNs, 3C Regional payers | Enterprise sales |

**Account schema:** 40+ fields for CRM/list building ([[ACCOUNT_SCHEMA_EXTENDED]])

**Exclusion rules:** Per-subtier filters before enrichment ([[SUBTIER_EXCLUSION_RULES]])

**Persona-title dictionary:** LinkedIn search strings by subtier ([[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]])

**Public data sources:** NPPES, CMS MSSP/ACO REACH, HRSA, NCQA BHI ([[PUBLIC_DATA_SOURCES_TAM]])

## 7. Motion & milestones (30 / 60 / 90)

| Horizon | Outcomes (suggested) |
|--------|----------------------|
| **30d** | Internal **claims matrix** (marketing vs legal); approved **discovery question bank** ([[DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER]]); CRM tagging for EHR + buyer persona. |
| **60d** | 10+ structured discovery calls logged → ingest as `methodology/` case nodes; security packet + architecture one-pager aligned to [[EHR_INTEGRATION_SMART_ON_FHIR]] / [[PRIVACY_AND_HIPAA_ROLE]]. |
| **90d** | 1–2 **written pilots** or LOIs targeted; press page live if comms ready; re-scrape `raw-context/kivira-public/` after site changes. |

## 8. Metrics (starter set)

- Pipeline: qualified opportunities by **EHR** and **org type** (FQHC, IDN, community).
- Technical win rate: % accounts completing **security review** without fatal finding.
- Clinical win rate: **clinician committee** or QI sign-off velocity.
- Evidence: # of **approved** outcome artifacts shared externally (counter mis-use of marketing charts).

## 9. Operating rhythm (Context OS)

- **Weekly:** Ingest 1–3 artifacts (calls, emails, site changes) via `/ingest` pattern; update nodes’ `last_updated`.
- **Monthly:** Run **`/graph-health`** (see [`_system/GRAPH_HEALTH_REPORT.md`](../../_system/GRAPH_HEALTH_REPORT.md)); fix broken `[[links]]` and tag drift.
- **Before launches:** [[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]] + legal review of hero claims.

## 10. Source-of-truth map

| Artifact | Location |
|----------|-----------|
| Public web archive | `raw-context/kivira-public/` |
| Deep research synthesis | `raw-context/MARKETANALYSIS.md` |
| Atoms | `knowledge_base/**` |
| Positioning / messaging | `00_foundation/positioning/`, `00_foundation/messaging/` |
| Taxonomy / ontology | `_system/knowledge_graph/` |
| Upstream quickstart | `gtm-context-os-quickstart/` |
