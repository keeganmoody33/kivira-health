---
name: TAM_TIER_3_ENTERPRISE_92M
description: Tier 3 TAM - Health Systems, IDNs, and Regional Payers ($91.8M, 470 logos)
domain: business
node_type: framework
status: validated
last_updated: 2026-04-05
tags:
  - business
  - tam-total-addressable-market
  - b2b-health-system
  - market-segmentation
topics:
  - tam-total-addressable-market
  - b2b-health-system
  - gtm-motion
related_concepts:
  - "[[TAM_COMPLETE_698M_ALL_TIERS]]"
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
  - "[[REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT]]"
  - "[[MEDICAL_SPEND_MODEL_ER_AVOIDANCE]]"
  - "[[TAM_DEDUP_METHODOLOGY]]"
source:
  type: document
  file: "Kivira Tier3 Complete Validated.pdf"
  date: "2026-04-05"
---

# TAM Tier 3: Enterprise ($91.8M)

[VERIFIED: Cross-validated between CMS DAC, AHA Annual Survey, and Definitive HC]

Tier 3 includes health systems, IDNs, and regional payers. Enterprise sales motion with longer cycles.

## Tier 3 Summary

| Subtier | Description | Logos | ACV | Dollar TAM | Contacts |
|---------|-------------|-------|-----|------------|----------|
| 3A | Health Systems | 250 | $175K | $43.8M | 1,000 |
| 3B | IDNs | 80 | $250K | $20.0M | 320 |
| 3C | Regional Payers | 140 | $200K | $28.0M | 420 |
| **Total** | | **470** | | **$91.8M** | **1,740** |

## Dedup Architecture

Tier 3 entities are the PARENTS that Tier 1 and Tier 2 entities roll up to.

- 2,323 system-affiliated groups from Tier 1 map to 3A/3B parents
- ~158 ACOs (2A) share parent_org_id with Tier 3A/3B
- Payer-provider hybrids classified as 3B primary, 3C secondary

**Cardinal rule:** Never count the same organization as primary logo in more than one subtier.

## 3A: Health Systems

**Definition:** Hospital system with employed PCP networks, ambulatory BH services, or population health infrastructure. Floor: ≥50 employed PCPs or ≥3 primary care clinic sites.

**Validated Count:** 250 (from ~400 AHA health systems after filters)

### Exclusions Applied
- Purely inpatient (no ambulatory PCP ops): ~60
- CAH without network affiliation: ~30
- Already captured as 3B IDN: ~60

### Kivira Sweet Spot
Mid-size systems (50-199 PCPs) with ambulatory BH services but no AI CDS deployed. Large enough for pop health team, small enough to move without enterprise RFP.

### State Distribution (Top 10)
FL (~28), TX (~25), NY (~20), CA (~19), PA (~18), MI (~17), OH (~17), VA (~16), NC (~15), CO (~14)

### Expandable TAM Signal
Each 3A parent has child groups representing expansion potential:
- Total child groups: 2,323
- Average per system: ~9
- **Pilot → expand:** Win 1 group → expand to siblings

## 3B: IDNs

**Definition:** Organization with centralized governance across hospitals + clinics + often a payer/risk arm. Has distinct VP-level decision-makers for care transformation.

**Validated Count:** 80 (distinct from 3A)

### 3B vs 3A Classification
An entity is 3B (not 3A) if it has:
- Centralized governance across multiple hospitals AND clinics
- Distinct enterprise VP roles (VP Care Transformation, VP Enterprise Apps)
- Often a payer arm or risk-bearing contracts at system level

### Top IDNs
HCA Healthcare, CommonSpirit Health, Kaiser Permanente, Ascension, Providence, Trinity Health, Advocate Health, Intermountain, Northwell, UPMC

## 3C: Regional Payers

**Definition:** Regional health plan, MA-heavy plan, regional BCBS affiliate, Medicaid MCO, or payer-provider hybrid where mental health quality creates Kivira fit.

**Validated Count:** 140

### Payer Universe
- Independent BCBS affiliates: ~30
- Regional MA plans (non-national): ~50
- Medicaid MCOs (unique parent orgs): ~45
- Payer-provider hybrids: ~15

### Kivira Fit Signals
- MA Stars rating pressure (3.0-3.5 stars on BH measures)
- HEDIS BH measures underperformance
- Risk adjustment V28 transition
- Medicaid BH carve-in states
- D-SNP enrollment growth

## Outreach Contacts

| Subtier | Personas | Contact/Acct | Key Roles |
|---------|----------|--------------|-----------|
| 3A | 4 | 4 | VP Pop Health, CMO, CMIO, VP Ambulatory |
| 3B | 4 | 4 | VP Care Transformation, CMO, VP Enterprise Apps |
| 3C | 3 | 3 | VP Medical Mgmt, CMO, VP Stars |

**Critical:** Do NOT lead with C-suite at health systems. Lead with ambulatory/pop health operator.

## Related Concepts

- [[TAM_COMPLETE_698M_ALL_TIERS]] - Full TAM context
- [[TAM_DEDUP_METHODOLOGY]] - How parent-child dedup works
- [[REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT]] - Primary value prop
- [[MEDICAL_SPEND_MODEL_ER_AVOIDANCE]] - Secondary value prop
- [[THREE_SEGMENT_ICP_FRAMEWORK]] - Segment 3 strategy
