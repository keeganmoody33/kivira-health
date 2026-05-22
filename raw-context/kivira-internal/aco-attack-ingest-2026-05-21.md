# ACO attack — session ingest source (2026-05-21)

**Type:** Cursor agent session (plan implementation + taxonomy/TAM Q&A)  
**Ingested to graph:** 2026-05-21

## Summary

User asked where ACOs sit in Kivira GTM taxonomy and 2A-specific TAM. Plan implemented:

- **Subtier 2A**, Tier 2, ICP Segment 2, pain segment VBC Risk-Squeezed ACOs (0.85).
- **Operational TAM:** 395 logos / $47.4M @ $120K ACV ([[TAM_TIER_2_ACO_VBC_73M]]).
- **Primary motion:** 2A entity; 1C `2A_aco_affiliated` secondary ([[ACO_ATTACK_MOTION_2A_PRIMARY]]).
- **CMS PY2026 Organizations CSV** as list spine ([[CMS_MSSP_ORGANIZATIONS_PY2026_2A_LIST_SPINE]]).
- **Artifacts:** `fixtures/aco_attack/*`, `scripts/build_aco_attack_lists.py`.
- **LinkedIn filter:** anti-persona + persona tiers ([[ACO_2A_HEYREACH_PERSONA_FILTER]]); `heyreach_leads_2a_persona_v2.json` (408 leads).

## Pain-segment TAM (do not merge with logo TAM)

[[PAIN_SEGMENT_MATRIX]] segment TAM $1.2B / value ARR $17M — market-level model, not list sizing.

## Wave 1 evidence

359 OperationalOwner-2A LinkedIn leads → 0 in-scope accepts → sync-first blitz hypothesis.
