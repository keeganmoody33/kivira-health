---
name: WEEKLY_HEYREACH_EVIDENCE_2026_05_10
description: HeyReach outbound metrics snapshot for Wave 1 week ending 2026-05-10 — surfaced a configuration stall blocking the two persona campaigns
domain: business
node_type: gtm_signal
status: emergent
date: "2026-05-10"
evidence_date: 2026-05-10
tags:
  - heyreach
  - weekly-evidence
  - outbound
  - wave1
  - gtm-tooling
topics:
  - gtm-motion
related_concepts:
  - "[[WEEKLY_MOC_2026_05_10]]"
  - "[[WEEKLY_MOC_GRAPH_RITUAL]]"
  - "[[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]]"
  - "[[wave1a_heyreach_copy]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[BUYER_PERSONA_OPERATIONAL_BUYER]]"
  - "[[BUYER_PERSONA_CLINICAL_CHAMPION]]"
source:
  type: tool_export
  system: heyreach-rest
  file: "scripts/heyreach_weekly_pull.py"
  endpoints: "POST /campaign/GetAll, POST /inbox/GetConversationsV2, POST /li_account/GetAll"
  date: "2026-05-10"
---

# HeyReach Week of May 4 – May 10

[VERIFIED: Pulled live via `scripts/heyreach_weekly_pull.py --since 2026-05-02` against `https://api.heyreach.io/api/public` on 2026-05-10 ~21:49 EDT. Sender: `keeganmoody33@gmail.com` (LinkedIn account id 192406, only sender attached).]

## Campaign Progress

| Campaign | Status | Loaded | InFlight | Pending | Finished | Failed | ExcludeInOther |
|----------|--------|--------|----------|---------|----------|--------|----------------|
| Wave1-Baseline-9Subtier-20260503 | IN_PROGRESS | 269 | **146** | 102 | **16** | 5 | False |
| Wave1-OperationalOwner | IN_PROGRESS | 359 | 35 | 324 | 0 | 0 | **True** |
| Wave1-ClinicalChampion | IN_PROGRESS | 590 | 35 | 555 | 0 | 0 | **True** |
| **TOTAL** | — | **1,218** | **216** | **981** | **16** | **5** | — |

Δ vs `[[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]]`:

- Loaded: 1,219 → 1,218 (essentially flat — 1 lead removed somewhere)
- InFlight: 104 → 216 (+112; entirely from Baseline)
- Finished sequences: 0 → 16 (Baseline only)
- Failed: 0 → 5 (Baseline only; ~2% failure rate)
- **Persona campaigns (OpOwner + ClinChamp): identical to 5/4 — zero movement in six days**

## Inbox (workspace-wide; per-campaign filter is broken upstream)

The `/inbox/GetConversationsV2` endpoint's `campaignIds` argument is silently ignored — confirmed by passing bogus IDs and observing identical `totalCount=58`. All inbox numbers below are workspace-wide; per-campaign attribution comes from the HeyReach autoTagger (sparsely populated).

| Metric | All-time | Post-launch (≥ 2026-05-02) |
|--------|----------|-----------------------------|
| Conversations (= accepts) | 58 | 23 |
| Replies (correspondent-last) | 27 | 8 |
| Multi-message threads | 32 | 6 |
| **Unread w/ reply (action needed)** | **7** | **7** |

## AutoTag Attribution

| Count | Campaign |
|-------|----------|
| 2 | 416629 — Wave1-Baseline-9Subtier-20260503 |
| 56 | (no autoTag — manual or pre-tagger conversation) |

Tag names in use: `{'Generic': 2}`. The AI tagger has barely classified anything; per-campaign attribution from autoTags is unreliable this week.

## Post-Launch Replies (Qualitative Read)

All 8 post-launch replies, qualitatively:

| Date (UTC) | Profile | Read |
|---|---|---|
| 5/10 | Vikas Mishra (Business Analyst, RPA) | "Hi Keegan," — opener, hasn't committed |
| 5/8 | Dan Funk | **IT recruiter pitch — not CoCM signal** |
| 5/7 | Vineet Mishra (`/in/vineet-mishra-healthcaresme`) | "It's my pleasure, Keegan" — polite; possibly warm |
| 5/6 | Laura Reidinger (Best Version Media) | **Media buying pitch — not signal** |
| 5/5 | Samy Fakkar | **LeadsForge.ai vendor pitch — not signal** |
| 5/4 | Antonio Lee | Joke about response rates — humor, not signal |
| 5/4 | Mohamed Sakeer | **LinkedIn outreach platform pitch — not signal** |
| 5/2 | Scott Lincoln | "No, not yet at least… if you have any recommendations…" — possibly warm |

**Read:** 2 of 8 replies (Vineet Mishra, Scott Lincoln) are possibly warm; the remaining 6 are counter-pitches/spam. **No reply has yet been attributed (by autoTag or by lead-list match) to OperationalOwner or ClinicalChampion — those campaigns have effectively sent zero connection requests since the stall began.**

## Stall Diagnosis (Headline Finding)

**Root cause of the OpOwner + ClinChamp freeze: configuration overlap with Baseline.**

1. All three Wave 1 campaigns share the **single LinkedIn sender** (id 192406, ~25/day free-tier cap split across all three).
2. OperationalOwner and ClinicalChampion have `excludeInOtherCampaigns: True`. Baseline has it `False`.
3. OpOwner + ClinChamp started 5/2; got the initial 35 connection requests out before Baseline existed.
4. **5/3 21:33 UTC — Baseline-9Subtier started.** Its lead list almost certainly overlaps with the 2A ACO and 1C Provider Group lists (the 9-subtier baseline includes those subtiers).
5. From that moment, every remaining lead in OpOwner's queue (324) and ClinChamp's queue (555) became "already in another active campaign" → **silently skipped by the exclusion rule.**
6. Result: the two persona-targeted campaigns have frozen at exactly 35 in flight for six days.

**Unblock action (Human Decision Required):** pause `Wave1-Baseline-9Subtier-20260503` in the HeyReach UI. Baseline is generating ~zero CoCM signal (every named reply was a counter-pitch); pausing it lets OpOwner + ClinChamp resume their natural ~25/day cadence against the right-targeted leads.

Alternative: toggle off `excludeInOtherCampaigns` on OpOwner + ClinChamp. Faster but means the same person can receive requests from Baseline AND a persona campaign from the same sender — spam risk.

## Interpretation

- Wave 1 is **not yet a copy experiment** — the persona-targeted campaigns haven't actually run. Any judgment on persona copy this week would be premature.
- Baseline's 8 post-launch replies skew heavily toward counter-pitches; the AI tagger hasn't classified them, but the qualitative read is clear: this is mostly noise, not buyer signal.
- 7 unread replies are waiting for human triage (Vineet Mishra and Scott Lincoln are the warmest).
- After pause: expect OpOwner + ClinChamp to start drawing from the ~25/day sender cap; first persona signal-read window shifts to **2026-05-17** (one week of real sending).

## What This Proves (Strategy Links)

This evidence validates / refines the following strategic nodes:

- [[OUTREACH_WAVE_STRUCTURE]] — Wave structure exercised; configuration interaction surfaced as a real failure mode
- [[BUYER_PERSONA_OPERATIONAL_BUYER]] — Still zero signal (campaign was effectively unrun)
- [[BUYER_PERSONA_CLINICAL_CHAMPION]] — Still zero signal (campaign was effectively unrun)
- [[wave1a_heyreach_copy]] — Copy untested in practice; signal-read window slips to 2026-05-17
- [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]] — HeyReach REST direct verified as a working CI-friendly path alongside the Cursor MCP
- [[WEEKLY_MOC_2026_05_10]] — Weekly hub citing this evidence
- [[WEEKLY_MOC_GRAPH_RITUAL]] — Ritual that produced this cohesion
- [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]] — Prior baseline for the Δ above
