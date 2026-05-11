---
name: HCC_V28_CODING_OPPORTUNITY
description: Technical explanation of CMS V28 HCC model and behavioral health coding opportunity
domain: technical
node_type: concept
status: archived
last_updated: 2026-05-11
tags:
  - technical
  - hcc-hierarchical-condition-categories
  - v28-model-cms
  - source-research-synthesis
topics:
  - hcc-hierarchical-condition-categories
  - v28-model-cms
  - risk-adjustment-raf
  - compliance
related_concepts:
  - "[[REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT]]"
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
  - "[[PRIMARY_CARE_WEDGE_ICP]]"
source:
  type: email
  file: "Josh Pappas email thread 2026-04-03"
  date: "2026-04-03"
---

# HCC V28 Coding Opportunity

CMS uses Hierarchical Condition Categories (HCCs) to risk-adjust payments to Medicare Advantage plans. The V28 model, fully phased in for 2026, represents a significant shift that makes behavioral health coding accuracy more financially material.

[INFERRED: Gemini directional analysis - verify before external use]

## Key Points

- **V28 shift:** Prioritizes severity of illness over sheer number of codes
- **BH relevance:** Distinguishing between "Depression NOS" and "Major Depressive Disorder, Severe" directly impacts reimbursement
- **Kivira role:** CDS tool that helps clinicians accurately assess and document severity

## Relevant HCC Codes (Behavioral Health)

Key codes where severity accuracy matters:
- **HCC 243** - Major Depressive Disorder, Severe
- **HCC 241** - Bipolar Disorder

The value difference between accurate vs. under-coded diagnoses is significant at the per-member level.

## Why Severity Matters Under V28

The V28 model rewards diagnostic precision:
1. Simply having "a depression code" is not enough
2. Accurate severity assessment = accurate risk adjustment
3. PCPs often under-code due to time pressure or uncertainty
4. Kivira provides clinical decision support to assess severity correctly

## Compliance Consideration

This is not "upcoding" - it's accuracy:
- Kivira helps identify patients who genuinely meet criteria for severe diagnoses
- Documentation supports the clinical finding
- Aligns with [[CDS_NOT_DIAGNOSIS_FRAMING]] - tool supports clinician decision, doesn't replace it

## Related Concepts

- [[REVENUE_ACCURACY_MODEL_RISK_ADJUSTMENT]] - Business model built on this technical foundation
- [[CDS_NOT_DIAGNOSIS_FRAMING]] - Regulatory positioning
- [[CPT_BILLING_CODES_BHI]] - Related billing mechanism
