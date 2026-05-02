---
name: TAM_DEDUP_METHODOLOGY
description: CMS-based deduplication methodology for Kivira TAM - ensures no logo is counted twice
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-05
tags:
  - methodology
  - tam-total-addressable-market
  - market-segmentation
topics:
  - tam-total-addressable-market
  - market-segmentation
  - workflow
related_concepts:
  - "[[TAM_COMPLETE_698M_ALL_TIERS]]"
  - "[[TAM_TIER_1_PROVIDER_534M]]"
  - "[[TAM_TIER_3_ENTERPRISE_92M]]"
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
source:
  type: document
  file: "Kivira Complete TAM All Tiers.pdf"
  date: "2026-04-05"
---

# TAM Deduplication Methodology

[VERIFIED: CMS-validated bottoms-up methodology using federal data]

This methodology ensures every logo is counted exactly once across all 9 subtiers.

## The Cardinal Rule

**Never count the same organization as a primary logo in more than one subtier.**

Use `subtier_primary` for main classification and `subtier_secondary_tags` for overlap.

## Logo Count Waterfall

```
GROSS (before any dedup):
  1A: 5,758 + 1B: 2,873 + 1C: 3,200 + 2A: 608 + 2B: 100 + 2C: 180
  + 3A: 400 + 3B: 150 + 3C: 155
  = 13,424 gross logos

DEDUP REMOVALS:
  1A system-affiliated → 3A/3B: -1,788
  1A ambiguous → review: -119
  1B system-affiliated → 3A/3B: -535
  1A/1B upgraded to 1C: -2,100 (net, after 1C absorbs)
  2A exclusions (shells, hosp-only): -213
  3A collapsed into 3B: -60
  3A inpatient-only / CAH excluded: -90
  3B too small / collapsed into 3A: -70
  3C payer-provider → 3B: -15
  = -4,990 removals

NET DEDUPLICATED TAM: 8,435 unique logos
```

## Dedup Flow Diagram

```
TIER 1 (Provider Groups)
 ├── 1A: 3,851 independent groups → stand alone
 ├── 1B: 2,338 independent groups → stand alone
 ├── 1C: 3,200 VBC groups → stand alone (some upgraded from 1A/1B)
 └── REMOVED: 2,323 system-affiliated groups
     └── Map to Tier 3A/3B parents via parent_org_id
     └── Appear as subtier_secondary_tags on parent

TIER 2 (Enablers & Intermediaries)
 ├── 2A: 395 ACOs → ~158 share parent_org_id with Tier 3
 │   └── Tag subtier_secondary_tags: ["2A_aco"]
 │   └── Still counted as 2A logos (distinct decision-makers)
 ├── 2B: 100 VBC enablement → no overlap with Tier 3
 └── 2C: 180 care management → minimal overlap

TIER 3 (Enterprise)
 ├── 3A: Health Systems → absorb 2,323 child groups from Tier 1
 ├── 3B: IDNs → subset with distinct governance layer
 └── 3C: Regional Payers → independent entities
```

## Key Dedup Rules

### 1. System-Affiliation Classification

Use keyword matching on org names + size/geography heuristics:
- Name contains system keywords (HOSPITAL, HEALTH SYSTEM, PERMANENTE, etc.)
- `pcp_count > 200` (very large groups almost always system-employed)
- `site_count > 50 AND states > 3` (multi-state large footprint)

**System-affiliated groups get:**
- `subtier_secondary_tags: ["3A_health_system"]`
- `parent_org_id` links to health system parent
- Removed from Tier 1 count

### 2. VBC Upgrade Logic

Groups in 1A or 1B that ALSO appear as MSSP participants:
- Upgrade to `subtier_primary: 1C`
- Add secondary tag for original tier
- Higher ACV ($90K vs $75K/$40K)

### 3. 3A vs 3B Classification

An entity is 3B (not 3A) if it has:
- Centralized governance across multiple hospitals AND clinics
- Distinct enterprise VP roles
- Often a payer arm or risk-bearing contracts

**If both 3A and 3B apply:** Classify as 3B (most specific), tag 3A as secondary.

### 4. Payer-Provider Hybrids

Kaiser, UPMC, Geisinger, etc.:
- `subtier_primary: 3B`
- `subtier_secondary_tags: ["3C_payer"]`

## Secondary Tags (Counted Once, Tagged for Context)

| Entity | Primary Subtier | Secondary Tag | Count |
|--------|-----------------|---------------|-------|
| Health system ACOs | 3A or 3B | 2A_aco | ~158 |
| VBC groups in ACOs | 1C | 2A_aco_affiliated | ~1,500 |
| System child groups | 3A or 3B | 1A_physician_group | 2,323 |
| IDN health systems | 3B | 3A_health_system | 80 |

## CMS Data Sources

**Primary:**
- CMS DAC National File: `data.cms.gov/provider-data/dataset/mj5m-pzi6`
- 2,819,129 clinician records
- Key: `org_pac_id` (group practice identifier)

**Cross-Reference:**
- CMS MSSP ACO Participant TIN PUF
- ACO REACH PY2026 Participant PDF
- AHA Annual Survey (health systems)

## Repeatable Steps

1. Pull CMS DAC National File
2. Filter by PCP specialty (Internal Medicine, Family Practice, General Practice, Geriatric Medicine)
3. Group by `org_pac_id`, count PCPs and sites
4. Apply size floor (1A ≥5, 1B 3-4)
5. Classify independent vs system-affiliated (keyword matching)
6. Cross-reference against MSSP/ACO REACH participant TINs → upgrade to 1C
7. Link system-affiliated groups to Tier 3 parent via `parent_org_id`
8. Never count same logo in two subtier primary counts

## Related Concepts

- [[TAM_COMPLETE_698M_ALL_TIERS]] - Master TAM using this methodology
- [[TAM_TIER_1_PROVIDER_534M]] - Tier 1 dedup detail
- [[TAM_TIER_3_ENTERPRISE_92M]] - Parent entities absorbing children
- [[THREE_SEGMENT_ICP_FRAMEWORK]] - Strategic segmentation
