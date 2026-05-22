---
name: JOSH_PILOT_LIST_MOTION_2026
description: LinkedIn-first HeyReach pilot motion from Josh Drs Group lists plus TAM fixtures — filter, score, enrich, gate, export.
domain: methodology
node_type: pattern
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - execution-cadence
  - heyreach
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - buyer-diligence
related_concepts:
  - "[[JOSH_DRS_GROUP_LIST_INGEST_2026]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
source:
  type: internal-doc
  file: "fixtures/josh_drs_group_2026/README.md"
  date: "2026-05-22"
---

# Josh pilot list motion (HeyReach, LinkedIn-first)

[INFERRED: Operational pattern for Q2 2026 pilot; validate with HeyReach accept/reply signal]

## Goal

~90+ high-fit pilot contacts across nine subtiers for HeyReach, expandable when LinkedIn profile quality is strong. **v1 does not export email or phone.**

## Message lane (export metadata only)

| Lane | When |
|------|------|
| clinical | BH/CoCM/integration/CMO signals |
| roi | Revenue, VBC, risk, HEDIS, CFO framing |
| ops | Practice manager, operations, care management |

Classifier: `tam_builder/josh_pilot/message_lane.py`

**HeyReach first DM:** use [[KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK]] **5 clusters (A–E)**, not message_lane. Router: `tam_builder/josh_pilot/first_touch_cluster.py`.

## Sourcing

- **1A/1B:** Filtered Josh exec export (not full 161k pass)
- **2A–3C:** `fixtures/wave1_runs/*/Q*_raw_urls.json` + ACO fixtures
- PCP seed list force-included for human review

## Hard HeyReach gate

`linkedin_profile_url` + non-empty `linkedin_headline` + `has_profile_photo=true`

## Pipeline

```bash
python3 scripts/run_josh_pilot_pipeline.py
```

Workflow spec: `_system/agent_workflows/josh-pilot-linkedin-enrichment.md`

## Claims discipline

CDS-aligned copy in `notes`; no revenue guarantees. See claims-safe outbound workflow.
