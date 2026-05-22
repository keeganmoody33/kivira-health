---
name: GTM_TIER_ARCHITECTURE_9_SUBTIERS
description: Nine-subtier GTM architecture for Kivira - Tier 1 Provider wedge, Tier 2 Risk-bearing/enablement, Tier 3 Enterprise expansion.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-05-04
tags:
  - methodology
  - gtm-motion
  - market-segmentation
  - source-research-synthesis
topics:
  - gtm-motion
  - workflow
  - market-segmentation
  - buyer-diligence
related_concepts:
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
  - "[[PAIN_SEGMENT_MATRIX]]"
  - "[[SUBTIER_EXCLUSION_RULES]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[COCM_ACCOUNT_PROFILE_SCHEMA]]"
  - "[[DEMO_FIRST_OUTBOUND_STRATEGY]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[ACO_ATTACK_MOTION_2A_PRIMARY]]"
  - "[[LIST_BUILDING_STACK_CLAY_ENRICHMENT]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# GTM Tier Architecture: 9 Subtiers

Operational segmentation for Kivira GTM. Tier 1 is the first outbound lane; Tiers 2-3 follow.

[INFERRED: Architecture derived from CoCM wedge analysis and Josh Pappas guidance; validate with outbound results]

## Tier Overview

```
Tier 1 — Provider-side pilot wedge
  1A  Mid-market provider groups
  1B  PCP groups
  1C  VBC provider groups

Tier 2 — Risk-bearing / enablement
  2A  ACOs
  2B  VBC enablement companies
  2C  Care management companies

Tier 3 — Enterprise expansion
  3A  Health systems
  3B  IDNs
  3C  Regional payers
```

---

## Universal Exclusions (All Subtiers)

Apply to every account regardless of subtier before enrichment or outreach:

- Entity is currently a known Kivira customer
- Entity is a known direct competitor
- Entity is a solo-practitioner (single-physician, no ancillary staff)
- Entity operates exclusively as a telehealth-only direct-to-consumer platform (no PCP workflow)
- Entity is located outside the U.S.
- Entity is inactive, closed, or in bankruptcy
- No identifiable clinical decision-maker reachable via LinkedIn or phone

---

## Tier 1 — Provider-Side Pilot Wedge

First outbound lane. Josh Pappas: target mid-market provider groups / PCP / VBC with email + phone and a pilot motion.

### Tier 1A — Mid-Market Provider Groups

**What counts:** Multi-site provider organizations, usually primary-care led or mixed primary care + specialty, but still operationally reachable.

**Size floor:** ≥5 PCPs or ≥2 clinic sites

**Include if:** Multi-site primary care-led or mixed primary care + specialty group. Typically 5-50+ clinicians, 2+ locations.

**Exclude if:**
- Single site, single-specialty (non-PCP), no primary care presence
- Fewer than 3 PCPs on staff or inferred
- Pure subspecialty (cardiology only, oncology only, etc.) with no primary care affiliate
- No EHR or EHR identified as outdated/non-interoperable (e.g., solo-custom legacy systems with no FHIR support)
- Revenue model is entirely fee-for-service with no quality contracts and no behavioral health services listed

**Economic buyer:** COO, CEO, President, occasionally CFO

**Clinical champion:** CMO, Medical Director, Primary Care Medical Director

**Operational owner:** Director of Operations, VP Operations, Director of Care Management, Population Health lead

**Technical gatekeeper:** IT Director, EHR/EMR lead, CMIO for more mature groups

**Why this lane matters:** Good pilot lane. They feel the PCP burden, can move faster than health systems, and usually have enough structure to care about workflow, coding, screening, follow-up, and referral leakage.

### Tier 1B — PCP Groups

**What counts:** Independent PCP practices, PCP group practices, family medicine / internal medicine groups, sometimes FQHC-like primary care orgs if they match workflow and buyer logic.

**Size floor:** ≥3 PCPs, ≥1 identifiable decision-maker

**Include if:** Independent PCP practice, family medicine group, internal medicine group, or FQHC-like primary care org where physician owner or practice administrator is identifiable and reachable.

**Exclude if:**
- Fewer than 3 PCPs (too small for Kivira's likely minimum ACV)
- Payer mix is entirely cash-pay or concierge without insurance billing
- No identifiable behavioral health burden (no depression/anxiety diagnoses in any public quality reporting)
- Practice administrator or physician owner is unreachable (no LinkedIn, no phone)
- Currently under acquisition or merger freeze (flag, don't exclude — revisit in 90 days)

**Payer mix filter:** Practices billing >60% self-pay/concierge are low-fit. Target groups with commercial + Medicare/Medicaid mix where CoCM codes are billable.

**Economic buyer:** Physician owner, Managing Partner, Practice Owner

**Clinical champion:** Lead physician, Medical Director, BH-integrated PCP champion

**Operational owner:** Practice Administrator, Office Manager, Clinical Manager

**Technical gatekeeper:** EHR admin, outsourced IT, practice operations lead

**Important note:** Should be tightly filtered. Small PCP groups can eat time and give weak ACV if you do not set a floor on size, payer mix, or behavioral-health pain.

### Tier 1C — VBC Provider Groups

**What counts:** Provider groups already operating in shared savings, downside risk, MA-heavy populations, ACO REACH, MSSP participation, or VBC contracts.

**Include if:** Provider explicitly participating in MSSP, ACO REACH, PC Flex, downside-risk MA, or otherwise public VBC contract. CMS public use files are the primary source.

**Exclude if:**
- VBC participation is purely administrative/nominal (no financial accountability signal)
- Group is a subsidiary already captured under Tier 3A/3B parent (tag as secondary, don't duplicate)
- No PCP presence — VBC groups without primary care leads are not Kivira-ready
- Predominantly specialist-driven shared savings arrangement with no primary care workflow

**Economic buyer:** VP Value-Based Care, CFO, COO, President

**Clinical champion:** CMO, Medical Director, VP/Medical Director of Population Health

**Operational owner:** Director of Population Health, Director of Care Management, Director of Quality, Director of Risk Adjustment

**Technical gatekeeper:** Analytics leader, IT/EHR lead, interoperability lead

**Why this lane matters:** Where Kivira story gets sharper around diagnosis accuracy, quality, utilization, and downstream cost. Still provider-side, but financially smarter than plain fee-for-service groups.

---

## Tier 2 — Risk-Bearing / Enablement Layer

Second lane. Some are direct customers; some are better as partners, channels, or embedded distribution.

### Tier 2A — ACOs

**What counts:** MSSP ACOs, provider-led ACOs, health-system-affiliated ACOs, physician-network ACOs. CMS defines ACOs as groups of doctors, hospitals, and other providers accountable for quality and cost of care.

**Include if:** MSSP ACO, ACO REACH participant, or provider-led ACO with Medicare/Medicaid accountability. Pull from CMS MSSP and ACO REACH participant public use files.

**Exclude if:**
- ACO entity is a holding/administrative shell without direct clinical operations (tag parent org instead)
- ACO is hospital-only with no affiliated PCP network
- Covered lives <500 (too small for enterprise ACO-level outreach)
- Already counted as primary entity under Tier 1C — use `subtier_secondary_tags` instead

**Dedup rule:** If a provider group in Tier 1C is an ACO participant, the provider group is the primary entity (Tier 1C primary + 2A_aco_affiliated secondary tag). The ACO entity itself is Tier 2A only if it has distinct decision-makers and a separate contracting structure.

**Economic buyer:** CEO, President, CFO, executive over network performance

**Clinical champion:** CMO, VP/Medical Director Population Health, physician executive for quality

**Operational owner:** Director of Population Health, Director of Care Coordination, Quality leader, Risk/Performance leader

**Technical gatekeeper:** Analytics, reporting, data integration, interoperability

**Why this lane matters:** Very strong fit for story around follow-up, risk capture, quality performance, and avoidable utilization.

### Tier 2B — VBC Enablement Companies

**What counts:** Companies helping provider groups succeed in VBC through analytics, care orchestration, risk adjustment, navigation, quality ops, or platform services.

**Include if:** Company sells analytics, risk adjustment, care orchestration, quality ops, navigation, or platform services to provider groups operating in VBC. Buyer may be VP Partnerships or VP Product who wants to embed Kivira into their platform.

**Exclude if:**
- Company is a pure data broker with no clinical workflow product
- Company is an EHR vendor (separate competitive/partnership analysis)
- Company has no clinical operations or care model — pure analytics without workflow
- Fewer than 50 employees (likely too early for a partnership deal to generate meaningful volume)

**Partnership flag:** Many Tier 2B accounts are better treated as channel partners or embedded distribution rather than direct end-customers. Flag `partnership_motion: true` for these.

**Economic buyer:** GM, VP Partnerships, VP Product, VP Clinical Strategy

**Clinical champion:** Chief Medical Officer, VP Clinical Programs

**Operational owner:** VP Client Success, VP Implementation, VP Operations, Director of Care Model

**Technical gatekeeper:** VP Product, CTO, integrations leader

**Important note:** Not always a straight end-customer motion. Often a channel / embed / partner motion. May not sell "Kivira to them" so much as "Kivira through them."

### Tier 2C — Care Management Companies

**What counts:** Organizations delivering care coordination, chronic care management, behavioral health integration, patient navigation, post-discharge follow-up, or outsourced population health services.

**Include if:** Organization delivers care coordination, chronic care management, behavioral health integration, post-discharge follow-up, or outsourced population health services and employs care managers or behavioral health navigators who interact with primary care workflows.

**Exclude if:**
- Organization's care management is exclusively disease management for non-behavioral conditions (e.g., pure diabetes care management) with no mental health workflow
- Company is direct-to-consumer (no B2B provider/payer contracting)
- No licensed clinical staff — pure lay-navigation models without clinician oversight

**Economic buyer:** CEO, GM, VP Operations, VP Clinical Operations

**Clinical champion:** Medical Director, VP Clinical Programs, behavioral-health lead

**Operational owner:** Director of Care Management, Director of Care Navigation, Director of Clinical Operations

**Technical gatekeeper:** IT/integration leader

**Why this lane matters:** These orgs live and die on patient engagement, risk stratification, escalation, and documentation workflows. Good fit if Kivira is framed as improving triage quality and follow-up performance.

---

## Tier 3 — Enterprise / Slower-Cycle Expansion

TAM gets big, sales cycle gets heavier.

### Tier 3A — Health Systems

**What counts:** Hospital systems with employed PCP networks, ambulatory platforms, behavioral-health services, or population-health infrastructure.

**Size floor:** ≥50 employed PCPs or ≥3 primary care clinic sites

**Include if:** Hospital system with employed PCP networks, ambulatory behavioral health services, or documented population health infrastructure. Wellstar is the reference archetype.

**Exclude if:**
- Purely inpatient with no ambulatory or employed PCP operations
- Critical Access Hospital (CAH) with no larger network affiliation — flag separately, lower priority
- Already captured as IDN parent under Tier 3B — use `subtier_secondary_tags`
- Active Epic/Oracle-native mental health CDS implementation underway (flag as high-risk competitive, not exclude — track)

**Economic buyer:** VP Ambulatory, COO, CFO, CMO

**Clinical champion:** CMO, service-line behavioral health leader, primary care medical executive

**Operational owner:** VP Population Health, Director of Ambulatory Operations, Care Management leader

**Technical gatekeeper:** CMIO, CIO, interoperability/EHR leader

**Critical sequence:** Do not lead with the CEO. Lead with the operator who owns ambulatory workflow and population outcomes.

### Tier 3B — IDNs

**What counts:** Integrated delivery networks with centralized governance across hospitals, clinics, employed groups, and often payer or risk-bearing relationships.

**Include if:** Organization has centralized governance across hospitals + clinics + often a payer/risk arm, with distinct VP-level decision-makers for care transformation, population health, and enterprise applications.

**Exclude if:**
- Entity is already captured as a Tier 3A health system with no distinct IDN governance layer (collapse into Tier 3A)
- No primary care ambulatory footprint — inpatient-heavy with no meaningful PCP network

**Dedup rule:** Many IDNs will overlap with health-system entities. Use `parent_org_id` to link. Do not count the same logo twice in TAM. If a health system is both a Tier 3A and a Tier 3B entity, classify at the most specific level (Tier 3B) with Tier 3A secondary.

**Economic buyer:** SVP/VP Enterprise Operations, VP Care Transformation, VP Population Health

**Clinical champion:** CMO, CMIO, physician executive for ambulatory strategy

**Operational owner:** Director of Care Transformation, Director of Population Health, enterprise care-management lead

**Technical gatekeeper:** CMIO, interoperability, enterprise applications, digital health

### Tier 3C — Regional Payers

**What counts:** Regional health plans, MA-heavy plans, regional Blues, Medicaid MCOs, payer-provider hybrids.

**Include if:** Regional health plan, MA-heavy plan, regional BCBS affiliate, Medicaid MCO, or payer-provider hybrid where mental health quality (Stars/HEDIS), risk adjustment, or care management programs create a fit with Kivira's diagnostic accuracy story.

**Exclude if:**
- National payer without a regional or market-specific program team (too diffuse for initial outreach — revisit post-Series A)
- Payer operates exclusively in commercial group without Medicare or Medicaid exposure (lower Kivira fit until CMS reimbursement codes exist)
- Behavioral health carve-out: payer uses a separate BH managed care org — tag the MCO instead

**Economic buyer:** VP Medical Management, VP Quality, VP Stars, VP Risk Adjustment, CFO

**Clinical champion:** CMO, behavioral health medical director, population health physician leader

**Operational owner:** Director of Quality, Director of Risk Adjustment, Director of Care Management, Director of Behavioral Health Programs

**Technical gatekeeper:** VP Data/Analytics, interoperability, product/program ops

**Why this lane matters:** Story shifts from PCP workflow to plan performance: quality, coding accuracy, medical cost, utilization, and network support.

---

## Outreach Sequence Logic

Apply across every subtier:

1. **Operator first** — Operational Owner with pain-specific message tied to the EDP. This person feels the problem daily and can champion internally.
2. **Clinical champion second** — Once operator is warm or has responded, loop in Clinical Champion. Clinical story needs clinical credibility.
3. **Economic buyer third** — Only engage Economic Buyer after pain is validated. Going to COO/CFO cold without internal champion creates price-only conversations.
4. **Technical gatekeeper parallel** — Route separate technical thread to EHR/informatics stakeholder in parallel with operator thread. Make them pre-informed ally, not blocker.

## Flag vs. Exclude Decision Tree

| Situation | Action |
|-----------|--------|
| Merger/acquisition pending | Flag, revisit in 90 days |
| Competitor tool deployed | Flag as competitive, track |
| No contact found yet | Flag for enrichment, don't exclude |
| Low payer mix fit | Exclude from Wave 1, may qualify for Wave 3 |
| Size below floor | Exclude unless exceptional signal |

## Related Concepts

- [[THREE_SEGMENT_ICP_FRAMEWORK]] — Strategic segment lens (three buckets vs nine subtiers)
- [[PAIN_SEGMENT_MATRIX]] — Segments ranked by EDP intensity
- [[SUBTIER_EXCLUSION_RULES]] — Detailed exclusion rules (canonical source; criteria inlined above for convenience)
- [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] — Title mapping per subtier
- [[COCM_ACCOUNT_PROFILE_SCHEMA]] — Account fields for list building

## Production Validation

### Wave 1 launch (2026-05-04)
- [[WEEKLY_MOC_2026_05_04]] — 9×5 structure exercised: 3 campaigns (1C Provider, 2A ACO, Baseline) with 1,219 leads loaded across the Wave 1 cohort
- [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]] — HeyReach campaign breakdown proving subtier / persona routing (Operational Owner 2A ACO, Clinical Champion 1C Provider, Baseline 9-subtier)

### Wave 1 production read (2026-05-11, after 7 days of send)

- **58 lifetime accepts across the 3 campaigns** (Baseline + OperationalOwner-2A + ClinicalChampion-1C).
- **10 in-scope to the 9-sub-tier structure (17%).** 48 noise (vendor / recruiter / off-industry — see [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns).
- **Sub-tier hit map** (in-scope accepts by sub-tier classification):

  | Sub-tier | In-scope accepts | Notes |
  |---|---:|---|
  | 1A — Mid-market provider groups | 1 | Robert Lystrup, MD @ Arizona Community Physicians |
  | 1B — PCP groups | 0 | Wave 1 didn't target; list build needed |
  | 1C — VBC provider groups | 3 | Yarly @ WellMed, Jason + Lynn @ Privia Health |
  | 2A — ACOs | 0 | OperationalOwner campaign produced *zero* direct 2A in-scope hits — investigate list quality |
  | 2B — VBC enablement | 2 | Kumar @ Optimum Healthcare IT, Scott Quinn @ EVOS Health (both borderline) |
  | 2C — Care management | 2 | Chris Oltmans @ NxtCare, Chris MacInnis @ Old Mission Wound Care |
  | 3A — Health systems standalone | 0 | Not on Wave 1 list |
  | 3B — IDNs | 0 | Not on Wave 1 list |
  | 3C — Regional payers / hybrids | 2 | Jeremy Wigginton @ Capital BCBS, Christa Thomas @ Optum (3C primary / 3A secondary) |

- **Persona-targeted lists beat baseline lists 4 to 1.** The Clinical Champion (1C) and OperationalOwner (2A) campaigns produced the cleaner accepts; the Baseline-9Subtier campaign produced most of the 48-noise noise. The "generic healthcare growth" LinkedIn slice is the main source of vendor / GTM-tool / recruiter accepts.
- **2A ACO campaign produced zero in-scope.** The list itself loaded 359 ACO-tagged leads but no Wave 1 accept-quality fit fell out. Either the title patterns from PERSONA_TITLE_DICTIONARY for 2A need tightening (the patterns may be capturing administrative shell roles instead of operating Population Health / Care Coordination leads), or the 7-day send window is too short for the ACO buying motion to surface. Both worth testing in Wave 2.
- **Operating wisdom:** HeyReach's `excludeInOtherCampaigns` flag is sticky across campaign-state changes. Pausing the holding campaign does not release leads from the exclusion check on dependent campaigns; the persistent fix is to toggle the flag off via UpdateSettings (which requires PAUSED status — Pause → UpdateSettings → Resume sequence). See `_system/agent_workflows/heyreach-cli-load-runbook.md` for the runbook.
- **Wave 1 follow-up artifact:** `00_foundation/_synthesis/josh-followup-2026-05-11/` — sub-tier-mapped accept list + individualized follow-ups (v7 preview, 2026-05-20). Evidence: `[[WEEKLY_HEYREACH_EVIDENCE_2026_05_20]]`.
- **Wave 2A synthesis (draft):** `00_foundation/_synthesis/wave2a-aco-heyreach-copy-2026-05-21/` — ACO sub-tier copy + build scripts; not promoted to messaging until human review.

### Wave 2 planning constraints (forward-looking)

Based on the above:

1. **List filters tighten BEFORE sub-tier match.** Apply [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns at list-build, not at outreach time.
2. **Sub-tiers with zero Wave 1 hits (1B / 2A / 3A / 3B) need targeted re-tests** with higher-intent persona matching, not just title pattern.
3. **Drop "generic healthcare growth" LinkedIn slices** from Baseline-equivalent campaigns. The signal-to-noise on that approach is below 20%.
4. **Ramp send volume in parallel** with list refinement — adding 2nd / 3rd LinkedIn senders to break the ~25/day cap. Volume increase × sharper list = compounding Wave 2 read.
