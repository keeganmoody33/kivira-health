---
name: COCM_CONFIDENCE_GRADE_RULES
description: Internal confidence-grade model for deciding how hard Kivira can lean on public CoCM opportunity estimates in outreach and ranking.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - methodology
  - evidence-discipline
  - workflow
  - source-internal-doc
topics:
  - workflow
  - evidence-discipline
  - gtm-motion
related_concepts:
  - "[[COCM_PUBLIC_ESTIMATE_ENGINE_V2]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[COCM_OUTREACH_SEQUENCING]]"
source:
  type: document
  file: "raw-context/kivira-internal/kivira-cocm-estimate-engine-v2-2026-04-05.md; raw-context/kivira-internal/kivira-deployment-guide-cocm-2026-04-05.md"
  date: "2026-04-05"
---

# CoCM Confidence Grade Rules

The CoCM workflow does not treat all estimates equally. It explicitly grades trust based on the quality of public signals and the strength of organization matching.

## Inputs

- high-confidence clinician matches
- medium-confidence clinician matches
- G0444 screening volume
- organization identity quality
- CoCM public visibility
- optional blended-denominator penalty

## Thresholds

- `A`: strongest public footing; numeric range can lead with caveats
- `B`: good enough to support a workflow-first pitch with range as support
- `C`: category story only in written outbound
- `D`: no public-signal-led outbound

## Commercial meaning

This grade is both a ranking tool and a claims-governance tool. It should directly control whether a rep can put modeled numbers into email or only discuss them verbally after interest exists.

## Related Concepts

- [[COCM_PUBLIC_ESTIMATE_ENGINE_V2]] - Source scoring model
- [[WAVE_1_SCORING_FRAMEWORK]] - Similar prioritization logic in the broader TAM system
- [[OUTREACH_WAVE_STRUCTURE]] - Grade feeds sequencing choices
- [[COCM_OUTREACH_SEQUENCING]] - Grade changes messaging mode
