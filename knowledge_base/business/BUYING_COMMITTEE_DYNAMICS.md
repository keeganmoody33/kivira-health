---
name: BUYING_COMMITTEE_DYNAMICS
description: How the Clinical Champion, Technology Gatekeeper, and Operational Buyer interact during a Kivira deal—sequence, shared blockers, and triggers to yes.
domain: business
node_type: pattern
status: validated
last_updated: 2026-04-06
tags:
  - business
  - buyer-persona
  - b2b-health-system
  - source-research-synthesis
topics:
  - buyer-persona
  - gtm-motion
  - discovery-calls
  - workflow
related_concepts:
  - "[[BUYER_PERSONA_CLINICAL_CHAMPION]]"
  - "[[BUYER_PERSONA_TECHNOLOGY_GATEKEEPER]]"
  - "[[BUYER_PERSONA_OPERATIONAL_BUYER]]"
  - "[[GTM_MOTION_HYPOTHESIS]]"
  - "[[EDP_COCM_REVENUE_REALIZATION]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# Buying Committee Dynamics

No single persona can advance a Kivira purchase alone. Understanding how all three interact is essential to pipeline movement.

[VERIFIED: Pattern synthesized from PHTI 2025 purchasing survey (n=309), AHRQ adoption literature, health system procurement patterns]

## The Committee

| Archetype | Title Pattern | Primary Motivation | Deal Role | Veto Power |
|-----------|---------------|-------------------|-----------|------------|
| Clinical Champion | Medical Director, IBH | Clinical outcomes & patient safety | Initiates, evangelizes | Can slow deal |
| Technology Gatekeeper | CMIO / VP Clinical Informatics | Workflow integrity & EHR governance | Approves or blocks integration | Hard veto |
| Operational Buyer | Director BH Services / VP Pop Health | CoCM revenue capture & operational efficiency | Validates ROI, manages contract | Budget authority |

## Deal Movement Sequence

Deals at health systems typically follow this pattern:

### Stage 1: Champion Identification
Dr. Jennifer (Clinical Champion) identifies Kivira at a CFHA conference or through peer referral. She requests an internal demo and begins building a business case.

### Stage 2: Operational Validation
Alex (Operational Buyer) is brought in early because Dr. Jennifer knows that without CoCM billing alignment and care manager buy-in, the program will stall. Alex evaluates:
- Workflow compatibility
- Billing integration
- KPI alignment

### Stage 3: Technical Diligence
Dr. Marcus (Technology Gatekeeper) is engaged once clinical and operational case is established. His team conducts technical review; he can approve or delay on integration timelines and security grounds.

### Stage 4: Formal Procurement
Value Analysis Committee receives submission from all three stakeholders and evaluates against system procurement standards. This is not a persona but a structural reality.

## Shared Adoption Barriers

All three personas share three core blockers that Kivira GTM must address proactively:

| Barrier | How It Manifests | Mitigation Message |
|---------|------------------|-------------------|
| **AI trust gap** | "How do we know the model isn't biased?" | Transparent instrument references; published subgroup performance data; CDS framing |
| **Workflow burden** | "This will add steps, not remove them" | Pilot data on clinician time saved; EHR-native design; care manager completion time |
| **Proof gap** | "Show me a peer-reviewed study" | Pilot outcomes report; Wellstar reference case; IRB-ready evaluation template |

## What Moves Each Persona to Yes

| Trigger | Clinical Champion | Technology Gatekeeper | Operational Buyer |
|---------|-------------------|----------------------|-------------------|
| **Strongest proof point** | Peer reference call from family medicine director at live site | FHIR conformance statement + HITRUST cert + Epic sandbox access | ROI one-pager with CoCM billing math and care manager time savings |
| **Fastest path to champion** | Invite to co-author pilot outcomes paper | Provide pre-completed integration architecture docs at first technical call | Show how tool maps to her quarterly KPI report |
| **Most common deal-killer** | Safety workflow ambiguity | Integration timeline slippage or unresolved security review | No clear answer on CoCM billing compatibility |

## Multi-Threading Rules

**Operator first → Clinical champion second → Economic buyer once pain is validated.**

The sequence matters:
1. **Do not** go to the CFO/COO cold without an internal champion—creates price-only conversations and kills pilots
2. **Do not** lead with the C-suite at health systems—lead with the operator who owns ambulatory workflow and population health outcomes
3. **Do** route a separate technical-specific thread to EHR/informatics stakeholder in parallel with operator thread—make them a pre-informed ally before formal security review lands

## Buying Committee Velocity Factors

**Accelerators:**
- Health system has already deployed ambient documentation (AI governance infrastructure exists)
- Active CoCM program with documented billing gap
- Recent clinical quality miss on MH metrics
- CMIO personally experienced alert fatigue with current MH alerts

**Decelerators:**
- No CoCM program (no billing rationale)
- Epic release cycle freeze (6-month integration delay)
- Active vendor consolidation initiative
- Recent digital health pilot failure (trust damaged)

## Related Concepts

- [[BUYER_PERSONA_CLINICAL_CHAMPION]] — Dr. Jennifer R. archetype
- [[BUYER_PERSONA_TECHNOLOGY_GATEKEEPER]] — Dr. Marcus A. archetype
- [[BUYER_PERSONA_OPERATIONAL_BUYER]] — Alex M. archetype
- [[GTM_MOTION_HYPOTHESIS]] — Why multi-threading matters
- [[EDP_COCM_REVENUE_REALIZATION]] — The metric that creates urgency across all three
