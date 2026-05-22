---
name: KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK
description: Canonical first DM after LinkedIn accept — v6 voice, 5-cluster decision tree, hard writing rules, Maria demo CTA. Not connection requests or email.
domain: methodology
node_type: pattern
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - outbound
  - linkedin-outreach
  - heyreach
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - discovery-calls
related_concepts:
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]]"
  - "[[JOSH_PILOT_LIST_MOTION_2026]]"
  - "[[COCM_OUTREACH_SEQUENCING]]"
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
source:
  type: internal-doc
  file: "knowledge_base/methodology/KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK.md"
  date: "2026-05-22"
---

# Kivira First-Touch LinkedIn Playbook

**What this is:** The canonical reference for the first message we send **after a LinkedIn connection is accepted**. Voice rules, message skeleton, 5-cluster decision tree, working templates (v6), per-person calibration for the first 10 accepts, and open threads.

**What this is NOT:** Cold connection request, email sequence, or multi-touch follow-up cadence. Single first DM after accept.

**Goal:** Book 4 to 6 demos in 90 days. Every message exists to get the person (or referral) into a **15-minute demo with Maria**.

**Status:** v6 voice locked.

---

## 1. Hard writing rules (non-negotiable)

- No em dashes and no en dashes. Use commas, periods, "or", or parentheses.
- Never open with "Hi" or use "Hi" as a greeting. Use `{{first_name}},`, `Dr. {{lastname}},`, or no greeting word.
- Never use "folks." Use "people," "team," "leaders," role names, or rephrase.
- No buzzwords: "holistic," "whole-person," "comprehensive," "synergy," "leverage" (verb), "solutions" (noun-blob).
- No lecturing recipients about their job (e.g. do not tell physicians PCPs are the front line of mental health). Report what peers have said instead.

---

## 2. Voice and tone

- Keegan's voice, not corporate sales.
- "w/" reads natural ("working w/", "spoken w/").
- Honest disclaimers: "I can only imagine" is the signature move.
- Observation in their words: "The physicians I've spoken w/ say..."
- Declarative close: "Our founder Maria will demo. We'd benefit from your feedback."
- Short: roughly 5 to 7 sentences.

---

## 3. Message skeleton

1. **Address** — `{{first_name}},` or `Dr. {{lastname}},` (comma, no greeting word).
2. **Position line** — "I'm working w/ Kivira.health, a mental-health clinical decision support tool for primary care, backed by Antler and Wellstar Catalyst." (Load-bearing: Keegan's profile may not list Kivira yet.)
3. **Observation in their role's words** — "The [role] I've spoken w/ say [tension]."
4. **Empathy disclaimer** — "I can only imagine..."
5. **What Kivira does** — role-specific impact.
6. **CTA with escape hatch** — "Would you be open to jumping on a call, letting us demo, and telling us where you can imagine this fitting into your day-to-day, **and where it just wouldn't work?**"
7. **Maria close** — "Our founder Maria will demo. We'd benefit from your feedback."

**Never drop the escape hatch** to save length.

---

## 4. Titling rule (Dr. vs first name)

| Credential | Address |
|------------|---------|
| MD, DO, MD/MBA, MD/MPH, etc. | `Dr. Lastname` |
| PA, NP, RN, non-physician clinical | First name |
| Everyone else | First name |

---

## 5. Five-cluster decision tree

**Persona axis > subtier axis** (Wave 1: persona-targeted lists beat baseline 4:1). Pin first touch to **role**, not subtier alone.

| Cluster | Title cues | Org / subtier | Observation phrase |
|---------|------------|---------------|-------------------|
| **A** Provider workflow | MD, DO, Medical Director, CMO, NP, PA at provider | 1A, 1B, 3A | "The physicians I've spoken w/" |
| **B** VBC / risk | VP/Dir Quality, Risk, Stars, HEDIS, RAF | 1C, 2A, 3C | "The quality and risk leaders I've spoken w/" |
| **C** Care coordination | VP/Dir Care Mgmt, Pop Health, BH Navigation | 2C | "The care management leaders I've spoken w/" |
| **D** Partnership / channel | VP Partnerships, Product, GM, Growth at enablement/network | 2B, network | "The partnership and product leaders I've spoken w/" |
| **E** Founder / peer / unclear | Founder, ambiguous org | unclear | "The founders I've spoken w/" |

**Exceptions:** Active posters (hand-built opener); off-axis titles (same skeleton, tailored middle).

Repo classifier: `tam_builder/josh_pilot/first_touch_cluster.py`

---

## 6. Working templates (v6)

See **`fixtures/josh_drs_group_2026/heyreach_first_touch_v6_templates.md`** for paste-ready HeyReach sequence bodies (clusters A through E). Swap `{{first_name_or_dr}}` and `{{company}}`.

---

## 7. Per-person calibration (first 10 accepts)

Send order and tailored tails documented in `00_foundation/_synthesis/josh-followup-2026-05-11/messages-josh-preview.md`. Site-check required for accepts 8, 9, 10 before send.

---

## 8. Deliberately OUT of first touch

- CoCM codes (99492-94), V28, HCC 243/241 in clusters A, C, D, E (B only: RAF, HEDIS, Stars language).
- "FTE add" / cost-saving framing (CFO frame).
- "0% CoCM realization rate" hard claim in feedback-ask touch.
- Customer logos beyond Antler + Wellstar Catalyst.
- Indiana Medicaid wedge until verified with Josh.

---

## 9. Wave 1 data (why this structure)

[VERIFIED: `knowledge_base/gtm_signals/heyreach/weekly-evidence-2026-05-11.md` and accept triage synthesis]

- Persona-targeted campaigns beat generic baseline ~4:1.
- 2A ACO campaign: zero in-scope accepts on 359 leads (title/shell hypothesis).
- Drop generic "healthcare growth" slices at list-build time.

---

## 10. Open threads

- Active-poster hand track.
- 2A ACO title diagnostic before re-spin.
- Indiana Medicaid wedge confirmation.
- Drs Group sheet pollution before email burst.
- Optional: one line on Keegan LinkedIn About for Kivira.

---

## 11. Versioning

- v6 (current): Keegan voice, escape-hatch CTA, observation-in-their-words.
- Supersedes lane-based Josh copy (`heyreach_lane_copy.md` deprecated 2026-05-22).

**HeyReach wiring:** `_system/agent_workflows/josh-pilot-heyreach-campaign-wiring.md` — five **PAUSED** campaigns (A through E), go-live gated.
