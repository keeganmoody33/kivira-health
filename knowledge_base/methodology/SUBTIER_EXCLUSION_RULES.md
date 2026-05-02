---
name: SUBTIER_EXCLUSION_RULES
description: Exclusion rules by subtier for Kivira TAM building - what to exclude before enrichment and outreach.
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
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[ACCOUNT_SCHEMA_EXTENDED]]"
  - "[[PUBLIC_DATA_SOURCES_TAM]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# Subtier Exclusion Rules

Apply these before enrichment and outreach to keep the list clean.

[INFERRED: Rules derived from ICP analysis and operational fit criteria]

---

## Universal Exclusions (All Subtiers)

Apply to every account regardless of subtier:

- Entity is currently a known Kivira customer
- Entity is a known direct competitor
- Entity is a solo-practitioner (single-physician, no ancillary staff)
- Entity operates exclusively as a telehealth-only direct-to-consumer platform (no PCP workflow)
- Entity is located outside the U.S.
- Entity is inactive, closed, or in bankruptcy
- No identifiable clinical decision-maker reachable via LinkedIn or phone

---

## Tier 1A — Mid-Market Provider Groups

**Include if:** Multi-site primary care–led or mixed primary care + specialty group. Typically 5–50+ clinicians, 2+ locations.

**Exclude if:**
- Single site, single-specialty (non-PCP), no primary care presence
- Fewer than 3 PCPs on staff or inferred
- Pure subspecialty (cardiology only, oncology only, etc.) with no primary care affiliate
- No EHR or EHR identified as outdated/non-interoperable (e.g., solo-custom legacy systems with no FHIR support)
- Revenue model is entirely fee-for-service with no quality contracts and no behavioral health services listed

**Size floor:** ≥5 PCPs or ≥2 clinic sites

---

## Tier 1B — PCP Groups

**Include if:** Independent PCP practice, family medicine group, internal medicine group, or FQHC-like primary care org where physician owner or practice administrator is identifiable and reachable.

**Exclude if:**
- Fewer than 3 PCPs (too small for Kivira's likely minimum ACV)
- Payer mix is entirely cash-pay or concierge without insurance billing
- No identifiable behavioral health burden (no depression/anxiety diagnoses in any public quality reporting)
- Practice administrator or physician owner is unreachable (no LinkedIn, no phone)
- Currently under acquisition or merger freeze (flag, don't exclude — revisit in 90 days)

**Important filter:** Set a payer mix floor. Practices billing >60% self-pay/concierge are low-fit. Target groups with commercial + Medicare/Medicaid mix where CoCM codes are billable.

**Size floor:** ≥3 PCPs, ≥1 identifiable decision-maker

---

## Tier 1C — VBC Provider Groups

**Include if:** Provider explicitly participating in MSSP, ACO REACH, PC Flex, downside-risk MA, or otherwise public VBC contract. CMS public use files are the primary source.

**Exclude if:**
- VBC participation is purely administrative/nominal (no financial accountability signal)
- Group is a subsidiary already captured under Tier 3A/3B parent (tag as secondary, don't duplicate)
- No PCP presence — VBC groups without primary care leads are not Kivira-ready
- Predominantly specialist-driven shared savings arrangement with no primary care workflow

---

## Tier 2A — ACOs

**Include if:** MSSP ACO, ACO REACH participant, or provider-led ACO with Medicare/Medicaid accountability. Pull from CMS MSSP and ACO REACH participant public use files.

**Exclude if:**
- ACO entity is a holding/administrative shell without direct clinical operations (tag parent org instead)
- ACO is hospital-only with no affiliated PCP network
- Covered lives <500 (too small for enterprise ACO-level outreach)
- Already counted as primary entity under Tier 1C — use `subtier_secondary_tags` instead

**Dedup rule:** If a provider group in Tier 1C is an ACO participant, the provider group is the primary entity (Tier 1C primary + 2A_aco_affiliated secondary tag). The ACO entity itself is Tier 2A only if it has distinct decision-makers and a separate contracting structure.

---

## Tier 2B — VBC Enablement Companies

**Include if:** Company sells analytics, risk adjustment, care orchestration, quality ops, navigation, or platform services to provider groups operating in VBC. Buyer may be VP Partnerships or VP Product who wants to embed Kivira into their platform.

**Exclude if:**
- Company is a pure data broker with no clinical workflow product
- Company is an EHR vendor (separate competitive/partnership analysis)
- Company has no clinical operations or care model — pure analytics without workflow
- Fewer than 50 employees (likely too early for a partnership deal to generate meaningful volume)

**Note:** Many Tier 2B accounts are better treated as channel partners or embedded distribution rather than direct end-customers. Flag `partnership_motion: true` for these.

---

## Tier 2C — Care Management Companies

**Include if:** Organization delivers care coordination, chronic care management, behavioral health integration, post-discharge follow-up, or outsourced population health services and employs care managers or behavioral health navigators who interact with primary care workflows.

**Exclude if:**
- Organization's care management is exclusively disease management for non-behavioral conditions (e.g., pure diabetes care management) with no mental health workflow
- Company is direct-to-consumer (no B2B provider/payer contracting)
- No licensed clinical staff — pure lay-navigation models without clinician oversight

---

## Tier 3A — Health Systems

**Include if:** Hospital system with employed PCP networks, ambulatory behavioral health services, or documented population health infrastructure. Wellstar is the reference archetype.

**Exclude if:**
- Purely inpatient with no ambulatory or employed PCP operations
- Critical Access Hospital (CAH) with no larger network affiliation — flag separately, lower priority
- Already captured as IDN parent under Tier 3B — use `subtier_secondary_tags`
- Active Epic/Oracle-native mental health CDS implementation underway (flag as high-risk competitive, not exclude — track)

**Size floor:** ≥50 employed PCPs or ≥3 primary care clinic sites

---

## Tier 3B — IDNs

**Include if:** Organization has centralized governance across hospitals + clinics + often a payer/risk arm, with distinct VP-level decision-makers for care transformation, population health, and enterprise applications.

**Exclude if:**
- Entity is already captured as a Tier 3A health system with no distinct IDN governance layer (collapse into Tier 3A)
- No primary care ambulatory footprint — inpatient-heavy with no meaningful PCP network

**Dedup rule:** Many IDNs will overlap with health-system entities. Use `parent_org_id` to link. Do not count the same logo twice in TAM. If a health system is both a Tier 3A and a Tier 3B entity, classify at the most specific level (Tier 3B) with Tier 3A secondary.

---

## Tier 3C — Regional Payers

**Include if:** Regional health plan, MA-heavy plan, regional BCBS affiliate, Medicaid MCO, or payer-provider hybrid where mental health quality (Stars/HEDIS), risk adjustment, or care management programs create a fit with Kivira's diagnostic accuracy story.

**Exclude if:**
- National payer without a regional or market-specific program team (too diffuse for initial outreach — revisit post-Series A)
- Payer operates exclusively in commercial group without Medicare or Medicaid exposure (lower Kivira fit until CMS reimbursement codes exist)
- Behavioral health carve-out: payer uses a separate BH managed care org — tag the MCO instead

---

## Flag vs. Exclude Decision Tree

| Situation | Action |
|-----------|--------|
| Merger/acquisition pending | Flag, revisit in 90 days |
| Competitor tool deployed | Flag as competitive, track |
| No contact found yet | Flag for enrichment, don't exclude |
| Low payer mix fit | Exclude from Wave 1, may qualify for Wave 3 |
| Size below floor | Exclude unless exceptional signal |

## Related Concepts

- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — Subtier definitions
- [[ACCOUNT_SCHEMA_EXTENDED]] — Fields for applying exclusions
- [[PUBLIC_DATA_SOURCES_TAM]] — Where to source data for exclusion checks
