---
name: CPT_BILLING_CODES_BHI
description: Key CPT codes for behavioral health integration billing that Kivira documentation supports
domain: technical
node_type: concept
status: validated
last_updated: 2026-05-11
tags:
  - technical
  - cpt-billing-codes
  - source-research-synthesis
topics:
  - cpt-billing-codes
  - fee-for-service-ffs
  - compliance
related_concepts:
  - "[[DIRECT_BILLING_MODEL_FFS]]"
  - "[[PRIMARY_CARE_WEDGE_ICP]]"
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
source:
  type: email
  file: "Josh Pappas email thread 2026-04-03"
  date: "2026-04-03"
---

# CPT Billing Codes for Behavioral Health Integration

Kivira enables reliable billing of behavioral health integration CPT codes by automating the documentation required to support these claims. This is the technical foundation of the [[DIRECT_BILLING_MODEL_FFS]].

[INFERRED: Gemini directional analysis - verify before external use]

## Key CPT Codes

### 96127 - Brief Emotional/Behavioral Assessment
- **Use:** Screening tool administration and scoring
- **Frequency:** Can bill multiple units per encounter (verify current limits)
- **Kivira fit:** Automated screening generates documentation for this code

### 99484 - General Behavioral Health Integration (BHI)
- **Use:** Monthly care management for BH conditions
- **Frequency:** Per patient per month
- **Kivira fit:** Ongoing monitoring and care coordination documentation

### G0444 - Annual Depression Screening
- **Use:** Annual screening for depression
- **Frequency:** Once per year
- **Kivira fit:** Annual screening workflow with proper documentation

## Documentation Requirements

Each code requires specific documentation:
1. Clinical indication for the service
2. Time spent (for some codes)
3. Clinical findings and plan
4. Patient consent where applicable

Kivira's clinical workflow generates this documentation automatically as part of the screening process.

## Revenue Potential

The directional logic:
- Clinics already seeing patients with BH needs
- Without proper documentation, these services go unbilled
- Kivira captures the documentation, enabling the billing
- Net new revenue stream from existing patient encounters

## Related Concepts

- [[DIRECT_BILLING_MODEL_FFS]] - Business model using these codes
- [[PRIMARY_CARE_WEDGE_ICP]] - Target practices for this capability
- [[CDS_NOT_DIAGNOSIS_FRAMING]] - How documentation aligns with regulatory positioning
