---
name: PAIN_SEGMENT_MATRIX
description: Five pain-based segments for Kivira GTM ranked by EDP intensity, conversion potential, and segment score.
domain: business
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - business
  - market-segmentation
  - tam-total-addressable-market
  - source-research-synthesis
topics:
  - market-segmentation
  - collaborative-care-cocm
  - value-based-care-vbc
  - gtm-motion
related_concepts:
  - "[[EDP_COCM_REVENUE_REALIZATION]]"
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[MARKET_ADOPTION_STAGE_2026]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# Pain-Based Segment Matrix

Segments ranked by Existential Data Point (CoCM Revenue Realization Rate) intensity and commercial potential.

[INFERRED: EDP framework applied to Kivira market segments; validate with pilot data]

## Segment Overview

| Segment | Pain Intensity | Conversion Rate | ACV Range | Segment Score |
|---------|---------------|-----------------|-----------|---------------|
| CoCM Cap-Maxed Health Systems | 0.95 | 15% | $75k–$150k | 92/100 |
| VBC Risk-Squeezed ACOs | 0.85 | 12% | $60k–$120k | 85/100 |
| Ambient AI Graduates | 0.70 | 10% | $40k–$80k | 78/100 |
| Staff-Starved FQHCs | 0.60 | 8% | $25k–$50k | 65/100 |
| Traditional FFS Groups | 0.30 | 3% | $15k–$30k | 40/100 |

---

## Segment 1: CoCM Cap-Maxed Health Systems (Priority 1)

**Profile:** Health systems that have deployed a Collaborative Care Model but are bottlenecked. Their behavioral health care managers are overwhelmed, and PCPs are failing to do the baseline structured screenings required to feed the registry.

**Pain Intensity:** 0.95 (Critical)

**Why they're hot:**
- Already did the hardest part: convinced leadership that integrated behavioral health matters
- Already hired care managers
- Know exactly how much CoCM revenue they're leaving on the table
- Definition of "early majority" buyers who want fast ROI and clinical outcomes

**TAM Estimate:** $1.5B

**Conversion Rate Potential:** 15%

**ACV Range:** $75k–$150k

**Sales Efficiency Factor:** 1.5 (High — they already understand the value)

**Value ARR Estimate:** $33M

**Segment Score:** 92/100

**Permissionless value prop:** Offer a "Lost Revenue Audit" — show exact dollar amount lost last quarter due to missing workflow.

---

## Segment 2: VBC Risk-Squeezed ACOs (Priority 2)

**Profile:** Accountable Care Organizations (ACO REACH, MSSP, PC Flex participants) holding downside risk. Desperate to identify high-risk mental health patients early to avoid costly downstream ED visits and specialist care.

**Pain Intensity:** 0.85 (High)

**Why they're hot:**
- Downside risk creates urgency
- Every missed severe depression case = cost they absorb
- Quality metrics tied to MH outcomes
- Population health infrastructure already exists

**TAM Estimate:** $1.2B

**Conversion Rate Potential:** 12%

**ACV Range:** $60k–$120k

**Sales Efficiency Factor:** 1.2

**Value ARR Estimate:** $17M

**Segment Score:** 85/100

**Permissionless value prop:** Run "Hidden Acuity" calculation — national averages of severe depression missed in 15-minute visits × expected ED utilization cost.

---

## Segment 3: Ambient AI Graduates

**Profile:** Health systems that recently deployed Abridge, DAX Copilot, or similar ambient documentation tools. They have solved the generic documentation problem but still lack structured diagnostic reasoning for mental health. They have SMART on FHIR infrastructure and AI governance already built.

**Pain Intensity:** 0.70 (Medium-High)

**Why they're hot:**
- AI governance infrastructure exists
- SMART on FHIR integration already working
- Proven they can deploy clinical AI at scale
- Next logical capability gap is diagnostic reasoning

**TAM Estimate:** $800M

**Conversion Rate Potential:** 10%

**ACV Range:** $40k–$80k

**Sales Efficiency Factor:** 1.8 (Fast technical integration)

**Value ARR Estimate:** $14M

**Segment Score:** 78/100

**Key message:** "You bought Ambient AI to save time; buy Kivira to drive clinical accuracy and revenue."

---

## Segment 4: Staff-Starved FQHCs

**Profile:** Federally Qualified Health Centers serving high-need populations with massive mental health burdens and zero access to psychiatric consultants.

**Pain Intensity:** 0.60 (Medium)

**Why they're challenging:**
- High clinical pain
- Low budget
- Complex procurement (HRSA requirements)
- But: HRSA grant funding may cover technology purchases

**TAM Estimate:** $400M

**Conversion Rate Potential:** 8%

**ACV Range:** $25k–$50k

**Sales Efficiency Factor:** 0.7 (Slower sales cycle, smaller ACV)

**Value ARR Estimate:** $2.5M

**Segment Score:** 65/100

**Consideration:** May be better suited for Phase 2 after case studies established with higher-ACV segments.

---

## Segment 5: Traditional Fee-For-Service Groups

**Profile:** Standard primary care groups relying on volume. Little financial incentive to spend time on complex mental health diagnoses unless it leads directly to an E&M upcode.

**Pain Intensity:** 0.30 (Low)

**Why they're cold:**
- No CoCM program means no billing rationale
- No quality contract means no outcomes pressure
- Volume-driven model deprioritizes complex MH cases

**TAM Estimate:** $2.0B

**Conversion Rate Potential:** 3%

**ACV Range:** $15k–$30k

**Sales Efficiency Factor:** 0.5

**Value ARR Estimate:** $1.8M

**Segment Score:** 40/100

**Strategy:** Deprioritize for outbound. May convert inbound if they're exploring CoCM launch.

---

## Bullseye Visualization

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │   ┌─────────────────────────────┐   │
                    │   │                             │   │
                    │   │   ┌─────────────────────┐   │   │
                    │   │   │                     │   │   │
                    │   │   │   ┌─────────────┐   │   │   │
                    │   │   │   │             │   │   │   │
                    │   │   │   │  CoCM Cap   │   │   │   │
                    │   │   │   │   Maxed     │   │   │   │
                    │   │   │   │   (0.95)    │   │   │   │
                    │   │   │   └─────────────┘   │   │   │
                    │   │   │    VBC ACOs (0.85)  │   │   │
                    │   │   └─────────────────────┘   │   │
                    │   │   Ambient Graduates (0.70)  │   │
                    │   └─────────────────────────────┘   │
                    │       FQHCs (0.60)                  │
                    └─────────────────────────────────────┘
                              FFS Groups (0.30)
```

## Segment Prioritization Logic

**Attack CoCM Cap-Maxed Health Systems first** because:
1. They have already convinced leadership that integrated behavioral health matters
2. They have hired care managers and built the infrastructure
3. Their exact pain is workflow friction and uncaptured billing
4. They are the "early majority" buyers who want fast ROI
5. Case studies from this segment unlock Segment 2 and 3

## Related Concepts

- [[EDP_COCM_REVENUE_REALIZATION]] — The metric that defines segment pain
- [[THREE_SEGMENT_ICP_FRAMEWORK]] — Strategic segment lens
- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — Operational tier structure
- [[MARKET_ADOPTION_STAGE_2026]] — Why these segments are ready now
