---
name: WAVE_1_SCORING_FRAMEWORK
description: Pilot feasibility and buyer complexity scoring for Wave 1 account prioritization
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-05
tags:
  - methodology
  - gtm-motion
  - execution-cadence
  - tam-total-addressable-market
topics:
  - gtm-motion
  - execution-cadence
  - workflow
  - discovery-calls
related_concepts:
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[TAM_TIER_1_PROVIDER_534M]]"
  - "[[GTM_30_60_90_EXECUTION_CADENCE]]"
  - "[[PRIMARY_CARE_WEDGE_ICP]]"
  - "[[DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER]]"
source:
  type: document
  file: "Kivira Tier1 Complete Validated.pdf"
  date: "2026-04-05"
---

# Wave 1 Scoring Framework

[VERIFIED: Framework from CMS TAM analysis - requires enrichment data to score]

Wave 1 accounts must score high on pilot feasibility and low on buyer complexity.

## Wave 1 Selection Criteria

```
Wave 1 = pilot_feasibility_score ≥ 7
         AND buyer_complexity_score ≤ 5
         AND identified_contact = true
```

## Pilot Feasibility Score (0-10)

Higher is better. Score each factor and calculate weighted average.

| Factor | Weight | Data Source | Scoring |
|--------|--------|-------------|---------|
| EHR fit | 25% | Definitive HC | Epic/athena = 10; eCW/Greenway = 7; NextGen = 5; unknown = 3 |
| VBC participation | 20% | CMS MSSP/ACO REACH PUFs | ENHANCED track = 10; BASIC = 7; None = 3 |
| BH readiness signal | 20% | NCQA BHI, CoCM billing data | BHI distinction = 10; CoCM billing = 8; PCMH only = 5; none = 2 |
| Org size (PCP count) | 15% | CMS DAC (validated) | 10-30 PCPs = 10; 5-9 = 7; 31-50 = 6; 50+ = 4 |
| Payer mix | 10% | Definitive HC / claims data | Medicare+Commercial mix = 10; MA-heavy = 8; Medicaid-dominant = 5; FFS-only = 2 |
| Ambient AI deployed | 10% | LinkedIn/press/Definitive HC | Yes = 10; Unknown = 5; No = 3 |

### Factor Details

**EHR Fit (25%)**
- Epic/athena = best integration path
- eCW/Greenway = good fit, common in mid-market
- NextGen = acceptable
- Unknown = risky but discoverable

**VBC Participation (20%)**
- ENHANCED track = financially accountable, highest urgency
- BASIC track = growing but less immediate pain
- None = FFS-only, lower CoCM code relevance

**BH Readiness Signal (20%)**
- NCQA BHI distinction = already invested in BH integration
- CoCM billing (99492/99493/99494) = actively billing, knows the workflow
- PCMH only = foundation exists
- None = greenfield but also harder to sell

**Org Size (15%)**
- 10-30 PCPs = sweet spot for pilot
- 5-9 = smaller, easier to close
- 31-50 = larger but more complexity
- 50+ = complexity rises, longer cycle

**Payer Mix (10%)**
- Medicare+Commercial mix = optimal for CoCM billing
- MA-heavy = good but risk adjustment focus
- Medicaid-dominant = lower reimbursement
- FFS-only = hardest to monetize CoCM

**Ambient AI Deployed (10%)**
- Yes = technology-forward, integration story strong
- Unknown = neutral
- No = may need more education

## Buyer Complexity Score (0-10)

Lower is better. Higher complexity = longer cycle.

| Factor | Weight | Data Source | Scoring |
|--------|--------|-------------|---------|
| Decision-maker count | 30% | Org chart / LinkedIn | 1-2 = 2; 3-4 = 5; 5+ = 8 |
| Org size (total staff) | 25% | Definitive HC | <50 = 2; 50-200 = 4; 200-500 = 6; 500+ = 8 |
| System affiliation | 20% | Definitive HC parent org | Independent = 2; Loose affiliation = 5; System-employed = 9 |
| Procurement process | 15% | Inferred from size + type | Physician-owner decides = 2; Committee = 6; Enterprise RFP = 9 |
| Active competitor deployed | 10% | Enrichment | None known = 2; Basic EHR alert = 4; AI CDS competitor = 8 |

### Factor Details

**Decision-Maker Count (30%)**
- 1-2 decision-makers = fast close possible
- 3-4 = manageable multi-thread
- 5+ = enterprise complexity

**Org Size (25%)**
- <50 staff = lean, fast decisions
- 50-200 = some process
- 200-500 = definite process
- 500+ = enterprise procurement

**System Affiliation (20%)**
- Independent = physician-owner can decide
- Loose affiliation = some influence but local autonomy
- System-employed = must go through parent (move to Tier 3)

**Procurement Process (15%)**
- Physician-owner decides = handshake deal possible
- Committee = multiple meetings, demo requests
- Enterprise RFP = formal process, much longer

**Active Competitor (10%)**
- None known = greenfield
- Basic EHR alert = low switching cost
- AI CDS competitor = must displace

## Expected Wave 1 Yield by Subtier

| Subtier | Total Logos | Est. Wave 1 % | Est. Wave 1 Logos |
|---------|-------------|---------------|-------------------|
| 1C (VBC groups) | 3,200 | 15-20% | 480-640 |
| 1A (mid-market) | 2,350 | 10-12% | 235-282 |
| 1B (small PCP) | 1,740 | 8-10% | 139-174 |
| 2A (ACOs) | 395 | 25-35% | 100-135 |
| **Tier 1+2A Wave 1** | | | **~950-1,230** |

**Wave 1 dollar opportunity:** 950-1,230 logos × blended $70K ACV = **$66.5M-$86.1M** addressable in first outbound wave.

## Data Required for Scoring (Enrichment Checklist)

| Field | Available from CMS? | Requires Definitive HC? | Requires Other? |
|-------|---------------------|-------------------------|-----------------|
| PCP count | Yes (validated) | Confirms | - |
| Site count | Yes (partial) | Better data | - |
| VBC participation | Yes (MSSP PUFs) | - | ACO REACH PUF |
| EHR platform | No | Yes (critical) | - |
| BHI/PCMH recognition | No | - | NCQA directory |
| CoCM billing activity | No | - | CMS Part B Utilization PUF |
| Payer mix | No | Yes | - |
| Ambient AI deployment | No | No | LinkedIn/press research |
| Decision-maker contact | No | No | ZoomInfo/Apollo/LinkedIn |
| Parent org/system affiliation | Partial (name-based) | Yes (definitive) | - |

## Scoring Implementation

1. **Start with CMS-validated data** (PCP count, VBC participation)
2. **Layer enrichment** (Definitive HC for EHR, payer mix, parent org)
3. **Calculate weighted scores** for each account
4. **Filter:** feasibility ≥ 7 AND complexity ≤ 5
5. **Sort by net score** (feasibility - complexity)
6. **Validate contact data** exists

## Related Concepts

- [[OUTREACH_WAVE_STRUCTURE]] - How waves are structured
- [[TAM_TIER_1_PROVIDER_534M]] - Tier 1 accounts to score
- [[GTM_30_60_90_EXECUTION_CADENCE]] - When to execute
- [[PRIMARY_CARE_WEDGE_ICP]] - Ideal buyer profile
- [[DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER]] - Discovery after outreach
