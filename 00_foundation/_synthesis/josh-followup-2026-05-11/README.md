# Wave 1 follow-up package — for Josh

**Date:** 2026-05-11
**For:** Josh Pappas

## What's in this folder

1. **`accepts-subtier-mapped.md`** — All 58 LinkedIn connection accepts from our Wave 1 outreach (Baseline + OperationalOwner + ClinicalChampion campaigns), with each person's account classified into our sub-tier structure. The honest signal: **10 are in-scope buyer targets**, the other 48 are mostly GTM-tool vendors / recruiters / off-industry connectors that came through despite our list filters.
2. **`followup-message-template.md`** — **Ten individualized messages**, one per in-scope accept. Each is tailored to the person's role, company, sub-tier, and how Kivira would land on their day-to-day. Uses real social proof (Antler + major healthcare systems + named medical-board members like Charles Nemeroff and Teddy Akiki). Offers two paths in every message: a call with them, OR a warm intro to the right person at their org if their week is packed.
3. **`accepts-subtier-mapped.csv`** — The same accept list as raw spreadsheet data (one row per person, with sub-tier + confidence + notes columns).

## How to use this

Skim `accepts-subtier-mapped.md` first — the table view is sorted by sub-tier and shows everyone with a confidence flag. Anyone marked **H** (high confidence) is ready to message; anyone marked **L** (low confidence) needs a 30-second LinkedIn / company-site check before you send.

For the message itself, open `followup-message-template.md` and use the worked examples as a model. The four examples cover four different sub-tiers (1A, 1C, 2C, 3C) — they show how the value-prop sentence shifts based on what kind of org the person works at.

There's a suggested send order at the bottom of the template — top of the list is Yarly Fassih-Nia at WellMed, who's the closest profile match to our actual buyer persona on this whole list.

## What this isn't

- **Not** the ACO blitz prep — that's a separate piece, I'll have it ready when you're back from your meeting.
- **Not** a list of new prospects — this is only people who *already accepted* our connection request, so the LinkedIn conversation is already open.
- **Not** an auto-send setup — these need to go from your account, manually. The existing HeyReach connect-request copy stays untouched (separate review process).

## Numbers to know

- 58 total accepts across the three Wave 1 campaigns
- 10 in-scope (17% accept-to-fit rate — Wave 2 list filter needs to get tighter on the Baseline campaign side, that's where most of the noise came from)
- 2 previously-flagged warm replies (Vineet Mishra, Scott Lincoln) called out separately — they're connectors / strategic conversations, not buyers, so they don't go through the main follow-up message
- Source data: pulled live this morning from HeyReach REST via `scripts/heyreach_accepts_pull.py`
