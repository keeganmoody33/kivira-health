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

**Subject:** [kivira.health] Week of May 11 — Wave 1 unblocked, accept-quality triaged, asking for a small assist

---

## 1. The One Thing

Two of our three LinkedIn campaigns had been silently sending zero new outreach since 5/3 because of a configuration interaction with the third campaign. Diagnosed it Sunday, toggled the fix yesterday, and confirmed live this morning that leads are flowing again (Clinical Champion campaign jumped from 35 frozen to 60 in flight in under 24 hours). **First persona-attributable signal-read window is now Saturday May 17.** Net effect of the week is one week of lost calendar against a sender that's day-cap capped anyway — recoverable.

In parallel we triaged the 58 LinkedIn accepts we *did* generate before the stall, and the accept-quality picture has its own signal in it (Section 3).

## 2. Campaign Results — fresh numbers (pulled live this morning)

| Campaign | Loaded | In flight | Status | Excludes others |
|---|---:|---:|---|---|
| Baseline-9Subtier | 269 | 146 | PAUSED (intentional, holds the persona campaigns' lane open) | False |
| OperationalOwner (2A ACO) | 359 | 35 | IN_PROGRESS | False |
| ClinicalChampion (1C VBC) | 590 | 60 | IN_PROGRESS (up from 35 in 24h — proves the unblock) | False |
| **Total** | **1,218** | **241** | | |

**Lifetime: 58 accepts, 27 replies, 7 unread reply threads needing action this week.**

## 3. What's promising vs. what's noise

We triaged all 58 accepts into our 9-sub-tier buyer structure today. The honest read:

- **10 of 58 (17%) are real in-scope targets.** The strongest accepts: Yarly Fassih-Nia (Sr Dir Quality + Risk Adjustment at WellMed Medical Management — UnitedHealth-affiliated VBC PCP group, perfect Operational Owner profile), Jeremy Wigginton MD (CMO Capital Blue Cross — regional payer, classic 3C Clinical Champion), Chris Oltmans (CPHO at NxtCare — population-health platform), Robert Lystrup MD (Medical Director at Arizona Community Physicians — large multi-site 1A primary-care group), and Christa Thomas (VP Clinical Compliance Ops at Optum). All getting personalized follow-ups this week from a curious-tone template, not a pitch.
- **48 of 58 (83%) are noise** — mostly GTM-tooling vendors auto-prospecting us (HeyReach, Salesforge, Premium Inboxes, WarmLeads, etc.), recruiters, agencies, and off-industry sales reps (one electrical-distribution salesman, one youth soccer coach). They came through despite our list filters because the Baseline 9-Subtier campaign over-indexed on generic "healthcare growth" LinkedIn slices.

Implication for Wave 2: tighten the Baseline list to exclude vendor/tool-side titles before they hit outreach. The 1C and 2A persona-targeted lists were materially cleaner — most of the in-scope 10 came from those two campaigns.

## 4. What we're correcting

- **HeyReach `excludeInOtherCampaigns` is sticky across campaign-state changes.** Pausing the holding campaign doesn't release leads from the exclusion. Persistent fix is to toggle the flag itself, which now lives in our runbook.
- **Five-minute REST pull on Fridays catches stalls that "check the inbox each morning" doesn't.** The persona-campaign stall was invisible in the HeyReach UI; the script (`scripts/heyreach_weekly_pull.py`) is now part of the Friday ritual and saved us from drifting another week.
- **Wave 2 list filter needs vendor/tool-title exclusion rules** — drafted, not yet in code.

## 5. Next Week (May 12–18)

1. Send curious-tone follow-ups to the 10 in-scope accepts (top of the list: Yarly @ WellMed).
2. Saturday 5/17 — first measurable persona reply-rate read.
3. ACO blitz prep with Josh (separate from the LinkedIn campaigns — manual email + phone, focus list).
4. CRM evaluation decision by 5/15 (HubSpot vs Salesforce vs continuing with "Book a Demo").
5. Tighten Wave 2 list-filter rules (exclude vendor/tool titles) before any new campaign launches.

## 6. Asks

- **Confirm weekly email cadence works** — this is the second weekly recap. Continue weekly?
- **CRM call by 5/15** — HubSpot / Salesforce / hold another sprint?
- **NEW — LinkedIn connection exports (the small assist):** if you're on the Kivira team, an advisor, a board member, or tightly affiliated, would you be willing to export your LinkedIn connections and send the file our way? LinkedIn lets you do this in a few clicks (*Settings → Data Privacy → Get a copy of your data → Connections* — they email you the CSV within 24 hours). The connections of Kivira-adjacent people are almost certainly the highest-fit prospects we have, and they're hiding in plain sight inside your networks. We'll mine them against our sub-tier structure and surface the in-scope ones; the file stays with us, no second use. Even one or two of these from people close to the company would likely outperform a month of cold list-building.

---

*Numbers pulled live 2026-05-11 via `scripts/heyreach_weekly_pull.py`. Source nodes: [[WEEKLY_HEYREACH_EVIDENCE_2026_05_10]], [[WEEKLY_LINEAR_SHIPPED_2026_05_10]]. Accept triage: `00_foundation/_synthesis/josh-followup-2026-05-11/accepts-subtier-mapped.md`.*
