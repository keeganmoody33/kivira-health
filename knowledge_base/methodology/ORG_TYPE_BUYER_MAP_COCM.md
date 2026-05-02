---
name: ORG_TYPE_BUYER_MAP_COCM
description: Internal buyer-routing map that changes champion order, title matching, and lead angle by org type for the CoCM wedge.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - methodology
  - buyer-diligence
  - gtm-motion
  - source-internal-doc
topics:
  - buyer-diligence
  - workflow
  - gtm-motion
related_concepts:
  - "[[COCM_ACCOUNT_PROFILE_SCHEMA]]"
  - "[[COCM_OUTREACH_SEQUENCING]]"
  - "[[THREE_SEGMENT_ICP_FRAMEWORK]]"
  - "[[GTM_MOTION_HYPOTHESIS]]"
source:
  type: document
  file: "raw-context/kivira-internal/kivira-deployment-guide-cocm-2026-04-05.md"
  date: "2026-04-05"
---

# Org-Type Buyer Map for CoCM

The deployment guide is explicit that the same signal should be routed differently depending on organization structure. This is not generic persona templating; buyer order and lead angle shift materially by org type.

## Routing logic

- `solo_practice`: clinician-owner first; workflow before revenue.
- `independent_group`: medical director first; admin/COO second.
- `health_system_medical_group`: clinical leader first, finance second, CMIO third.
- `aco_parent`: population health first, finance supporting, BH ops when present.

## Title mapping

The guide also standardizes how persona tokens should match real titles:

- `medical_director` maps to medical director / VP primary care / service line leader / managing partner.
- `cfo` maps to CFO / COO / VP revenue cycle / practice administrator / VP finance.
- `cmio` maps to CMIO / VP clinical informatics, with CIO secondary.
- `pop_health` maps to VP population health / VP quality / care management / transformation leaders.
- `bh_ops` maps to BH integration and BH-focused care management operators.

## Practical implication

Repo-local persona routing should output both the abstract persona sequence and the real-world title variants, so list building and outreach prep stay connected.

## Related Concepts

- [[COCM_ACCOUNT_PROFILE_SCHEMA]] - Supplies `org_type` and persona priorities
- [[COCM_OUTREACH_SEQUENCING]] - Uses this buyer order by tier
- [[THREE_SEGMENT_ICP_FRAMEWORK]] - Connects the wedge to the larger GTM map
- [[GTM_MOTION_HYPOTHESIS]] - Explains why multi-threading matters
