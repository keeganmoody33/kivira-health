---
title: "Investor email — Week of May 11, 2026 (copy-paste)"
date: 2026-05-11
status: draft
type: investor-email
derived_from:
  - "[[WEEKLY_MOC_2026_05_10]]"
  - "[[WEEKLY_HEYREACH_EVIDENCE_2026_05_10]]"
  - "[[WEEKLY_LINEAR_SHIPPED_2026_05_10]]"
---

# Weekly Email (Copy-Paste Ready)

**Subject:** [kivira.health] Week of May 11 — Stall diagnosed, unblock in progress

---

## 1. The One Thing

Last Monday we launched three LinkedIn campaigns with 1,219 prospects. **For six days, two of the three campaigns — the persona-targeted ones (Operational Owner and Clinical Champion) — silently sent zero new outreach** because of a configuration interaction with our third campaign (Baseline). We caught it Sunday night, paused the Baseline campaign, and confirmed Monday morning that the persona campaigns are still blocked by a persistent exclusion flag. **Full unblock is one toggle away** (`excludeInOtherCampaigns: false` on both campaigns). The original signal-read window (Thursday May 8) was the wrong calendar — we now expect first persona-attributable reply data by **Saturday May 17**, one full week after the unblock.

The good news: the issue is configuration, not copy, sender health, or infrastructure. The bad news: this is a week of calendar we don't get back. The honest news: we now have a persistent diagnostic script (`scripts/heyreach_weekly_pull.py`) that would have caught this stall on Day 2 if we had been running it.

## 2. What We Shipped This Week

This was a listening-and-learning week, not a build-and-deploy week. **Zero issues shipped or created in our Linear team between 5/4 and 5/10** — confirmed via the Linear pull tool we built (see [[WEEKLY_LINEAR_SHIPPED_2026_05_10]]). The Wave 1A parent thread (LEC-32) remains In Progress; three GTM backlog items (LEC-40 1C grind, LEC-43 monitoring, LEC-44 wave templates) are queued for post-unblock.

The week's real output sits outside Linear, in the knowledge graph itself:

| Output | Significance |
|--------|--------------|
| `scripts/heyreach_weekly_pull.py` | Persistent REST puller for HeyReach campaign + inbox metrics — surfaced the stall |
| `scripts/linear_weekly_pull.py` | Same pattern for Linear; this email's Section 2 is auto-generated from it |
| Context-OS v2 maintenance pass | 5 commits, 17 emergent nodes promoted to validated, 3 archived, tag sprawl 46% → 30%, indexer cleaned of v1 cruft |
| `KIVIRA_COMPANY_PROFILE_2026_05_11` | First canonical "what Kivira is" synthesis node; pulls from public web + legal corpus; sets the refresh-cadence rhythm |
| `KIVIRA_BACKER_COPY_SHIFT_2026_05` | Tracked a positioning change in Kivira's own footer between 4/6 and 5/11 (from "Backed by Y Combinator & Antler" to "Backed by Antler & major healthcare systems") — internal signal that the public narrative shifted |
| `HEAT_EXCEPTION_EXTERNAL_VALIDATION` | Methodology rule preventing the graph from auto-archiving publicity/third-party-press nodes (would have killed POLSKY profile auto-archive) |

## 3. Signal Flow (Search → Capture → Validate)

| Persona | Search (Loaded) | Capture (In Progress) | Validate (Replies / Demos) |
|---------|------------------|------------------------|-----------------------------|
| Operational Owner (2A ACO) | 359 | **35 frozen** (no movement since 5/3) | 0 attributable |
| Clinical Champion (1C Provider) | 590 | **35 frozen** (no movement since 5/3) | 0 attributable |
| Baseline 9-Subtier | 269 | 146 in flight; 16 sequences finished; now PAUSED | 8 post-launch replies; 2 possibly warm, 6 counter-pitches |
| **Total** | **1,218** | **216 active** | **8 replies workspace-wide; 0 persona-attributable** |

Two replies worth a personal response this week:

- **Vineet Mishra** (`/in/vineet-mishra-healthcaresme`) — healthcare contact; replied with "It's my pleasure, Keegan" — warmest of the eight
- **Scott Lincoln** (`/in/scottmlincoln`) — "No, not yet at least… if you have any recommendations" — open-ended; opportunity to reciprocate

The other six post-launch replies are counter-pitches from other sales tools (LeadsForge, Best Version Media, Mohamed Sakeer's outreach platform, etc.). Spam, not signal.

Source: [[WEEKLY_HEYREACH_EVIDENCE_2026_05_10]], [[WEEKLY_LINEAR_SHIPPED_2026_05_10]].

## 4. Infrastructure Pulse

| System | Health | Notes |
|--------|--------|-------|
| HeyReach | 🟡 Yellow | 3 campaigns IN_PROGRESS but Baseline now PAUSED; persona campaigns frozen pending exclusion-flag toggle. Single LinkedIn sender at ~25/day cap. |
| InboxKit | ⚪ Not measured | `INBOXKIT_API_KEY` not in `.env.local`; the existing screenshot capture from 5/4 still partial source of truth. Will wire next cycle. |
| Linear | 🟡 Yellow | 0 shipped / 0 created this week; LEC-32 in progress. Honest read of low Linear activity = work happened in the graph. |
| List Building | 🟢 Green | 9-subtier × 5-persona structure intact; 1,218 leads loaded; no further sourcing this week. |
| Graph index | 🟢 Green | 81 nodes, 496 resolved links, 0 orphans. v1 indexer false-positive emissions retired. |

## 5. Experiment Velocity

| Experiment | Hypothesis | Result | Decision |
|------------|------------|--------|----------|
| Persona-targeted Wave 1A copy (Operational Owner / Clinical Champion) | Targeted persona copy outperforms generic | **Effectively non-run** — campaigns starved by config; cannot evaluate copy | Re-baseline after unblock; signal-read window 5/17 |
| HeyReach REST direct (no MCP dependency) | Can pull weekly metrics without Cursor MCP | Yes — `scripts/heyreach_weekly_pull.py` works in CI / any agent | Canonical |
| Linear REST direct | Same hypothesis, Linear team | Yes — `scripts/linear_weekly_pull.py` works | Canonical |
| Context-OS v2 ritual catches gaps | Weekly graph-pull surfaces problems that daily inbox checks miss | Confirmed — the stall was invisible to "check the inbox each morning" but obvious in the 5-min REST pull | Ritual lives |

## 6. 30 / 60 / 90 Progress

| Horizon | Target | Current Status | Gap |
|---------|--------|----------------|-----|
| 30d | Claims matrix; discovery bank; CRM tagging | Discovery questions in [[DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER]]; CRM evaluation **not started** (5/15 deadline 4 days out) | CRM is the at-risk item |
| 60d | 10+ discovery calls logged | 0 formal calls; 2 possibly warm replies await triage; signal-read pushed to 5/17 | Reply-to-meeting conversion deferred one week |
| 90d | 1–2 written pilots / LOIs | Pre-launch; first measurable persona-reply data window 5/17 | On track if unblock happens today and reply rates land in expected band |

## 7. What We Learned

- **HeyReach's `excludeInOtherCampaigns` flag is sticky across campaign-state changes.** Pausing the holding campaign doesn't release its leads from the exclusion check. The persistent fix is to toggle the flag off on the campaigns being starved — not pause the campaign doing the holding. This is non-obvious; the platform docs don't surface it.
- **REST-direct discipline catches stalls daily-inbox-checks won't.** The persona campaigns showed "active" in the HeyReach UI and the inbox felt quiet. The five-minute REST pull is what made the silent skip visible. We now run this every Friday automatically.
- **Graph heat undercounts importance for external-press nodes.** During the maintenance pass, the default v2 archive rule (emergent + 30 days + ≤1 inbound → archive) would have auto-deleted the Polsky / UChicago profile node — a strategically core publicity asset. We added a methodology rule ([[HEAT_EXCEPTION_EXTERNAL_VALIDATION]]) so future maintenance preserves these. Worth knowing for anyone designing similar evidence systems.
- **Kivira's public positioning is moving in real time.** The site footer changed between April and May from "Backed by Y Combinator & Antler" to "Backed by Antler & major healthcare systems" — caught by the Spider Cloud freshness check. Logged as [[KIVIRA_BACKER_COPY_SHIFT_2026_05]] for follow-up.

## 8. Next Week (May 12–18)

1. **Unblock the persona campaigns** — toggle `excludeInOtherCampaigns: false` on Operational Owner (id 416316) and Clinical Champion (id 416299). Either via HeyReach UI (one click each) or via API (requires explicit approval — see §9). This is the critical path item; everything else this week is downstream.
2. **First persona signal-read window: Saturday May 17.** One week of unblocked sending → first measurable reply rate on persona-targeted copy.
3. **Triage Vineet Mishra + Scott Lincoln replies** — two warm threads this week deserve personalized follow-ups.
4. **CRM evaluation by May 15** — slipped from last week; 4-day runway. HubSpot vs Salesforce vs continuing with "Book a Demo" form-only.
5. **Wire InboxKit REST** — add `INBOXKIT_API_KEY` to `.env.local`; same pattern as the Linear puller just built. Closes the last evidence gap.

## 9. Human Decision Required

- [ ] **Authorize HeyReach API toggle on the persona campaigns** — OR confirm you'll do the UI toggle yourself. One click per campaign, 30 seconds total in browser. The API path is faster but I need your go-ahead before each production write (see [[WEEKLY_HEYREACH_EVIDENCE_2026_05_10]] for the prior pause action precedent).
- [ ] **CRM choice by May 15** — HubSpot / Salesforce / hold on "Book a Demo" form for another sprint?
- [ ] **Confirm weekly email cadence** — this is the second instance of the Monday-morning recap. Continue weekly, or shift to Slack/Notion, or daily-pulse format?

---

## Thursday 7pm ritual (reference)

| Time | Action |
|------|--------|
| Monday 9am | Review Linear + run `scripts/linear_weekly_pull.py` and `scripts/heyreach_weekly_pull.py` |
| Mon–Wed | Execute; deposit evidence daily |
| Thursday 4pm | Fresh evidence pull on all three surfaces |
| Thursday 5pm | Author / refresh evidence nodes |
| Thursday 6pm | Generate weekly MOC + investor email |
| Thursday 7pm | Send to Josh + investors |
| Thursday 7:15pm | `git commit` weekly MOC + email |

---

*Numbers in this email match `WEEKLY_HEYREACH_EVIDENCE_2026_05_10` and `WEEKLY_LINEAR_SHIPPED_2026_05_10`; if more than 6 hours have passed since draft time, re-run the pullers before send.*
