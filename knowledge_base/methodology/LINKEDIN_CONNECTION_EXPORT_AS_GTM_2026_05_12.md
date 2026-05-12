---
name: LINKEDIN_CONNECTION_EXPORT_AS_GTM_2026_05_12
description: GTM tactic of asking Kivira team / advisors / board / tightly-affiliated to export their LinkedIn connections (Settings → Data Privacy → Get a copy of your data → Connections) so we can triage for in-scope prospects hiding in plain sight.
domain: methodology
node_type: pattern
status: emergent
last_updated: 2026-05-12
tags:
  - methodology
  - gtm-motion
  - outbound
  - workflow
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - market-segmentation
related_concepts:
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[KIVIRA_COMPANY_PROFILE_2026_05_11]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
source:
  type: notes
  file: "Session conversation 2026-05-12 (investor email §6 — 'one small assist')"
  date: "2026-05-12"
---

# LinkedIn connection export as a GTM tactic (2026-05-12)

Ask Kivira-adjacent people (founder + team + advisors + board + tightly-affiliated investors) to export their LinkedIn connections and send us the CSV. Run the file through the 9-sub-tier persona dictionary + anti-persona filter. Surface only the in-scope rows. Result: a pool of warm-introducible prospects that cold list-build cannot produce.

[INFERRED: Tactic added to the 2026-05-11 weekly investor email §6 as "one small assist." Not yet run; sized estimates below are pre-execution.]

## The ask (verbatim from the investor email)

> If you're on the Kivira team, an advisor, a board member, or tightly affiliated, would you be willing to export your LinkedIn connections and send the file our way? LinkedIn lets you do this in a few clicks (*Settings → Data Privacy → Get a copy of your data → Connections* — they email you the CSV within 24 hours). The connections of Kivira-adjacent people are almost certainly the highest-fit prospects we have, and they're hiding in plain sight inside your networks. We'll triage them against our sub-tier structure and surface only the in-scope ones; the file stays with us, no second use. Even one or two exports from people close to the company would likely outperform a month of cold list-building.

## The mechanics (LinkedIn export flow)

The asker walks through:

1. **LinkedIn web** → click your profile picture → **Settings & Privacy**.
2. **Data Privacy** (left nav) → **Get a copy of your data**.
3. Select **Want something in particular?** → check only **Connections** (don't request the full archive — that takes 24-48h vs. 10 min).
4. Click **Request archive**.
5. LinkedIn emails the CSV to the account's primary email within ~10 minutes for the Connections-only download (24h for the full archive).
6. Send us the CSV.

**File format:** UTF-8 CSV. Columns: `First Name`, `Last Name`, `URL` (LinkedIn profile), `Email Address` (only populated if the connection shared their email with this user), `Company`, `Position`, `Connected On` (date).

Most users have ~500-3,000 connections. Senior executives typically have ~3,000-15,000.

## Why this is high-yield

Three reasons cold list-build can't match this:

1. **Already filtered by trust.** The connector implicitly vouched for these people by connecting in the first place. Selection bias works in our favor.
2. **Already filtered by social graph.** Healthcare-executive connectors have connection lists weighted toward healthcare; tech connectors toward tech. The graph self-segments to our wedge.
3. **Already a warm intro path.** Any prospect on this list can be reached with "I noticed you're connected to [connector] at Kivira — would you be open to..." which has a fundamentally different reply rate than cold outbound.

## Triage motion once a file arrives

Cross-reference each row against the existing graph filters:

1. **First pass:** apply [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns to exclude vendor / recruiter / off-industry / wrong-wedge rows. Expected: removes 50-70% of rows for a typical executive's connections.
2. **Second pass:** match remaining rows against the include-persona patterns per sub-tier. Tag each in-scope row with its sub-tier classification.
3. **Third pass:** rank by `Connected On` (more recent = warmer relationship), title seniority, and company size.
4. **Output:** a ranked CSV of in-scope rows handed back to the connector with explicit "would you be willing to make a warm intro to these N people?" — never use the export as a cold-outbound list.

**Privacy posture:** the file stays with us, not shared with enrichment vendors, not pushed to Clay / Apollo, not used for any purpose beyond the triage. After the triage, the raw file is archived under `raw-context/kivira-internal/li-exports/[connector-name-or-pseudonym]-YYYY-MM-DD.csv` with restricted access.

## Expected yield estimate (pre-execution)

| Connector type | Connections (typical) | After anti-persona filter | After in-scope filter | Warm-introducible final list |
|---|---:|---:|---:|---:|
| Mid-career executive (advisor, exec) | 3,000 | 1,500 | 150-300 (5-10%) | 75-150 (after relationship-recency rank) |
| Senior healthcare executive | 8,000 | 5,000 | 500-1,000 (10-15%) | 250-500 |
| Highly-networked founder / investor | 15,000 | 9,000 | 700-1,400 (8-12%) | 350-700 |

**Comparison anchor:** Wave 1 cold list-build (1,219 leads via CMS / Clay / synthetic enrichment) produced **10 in-scope after 7 days of LinkedIn outreach** (0.8% of total). A single mid-career executive connection export should produce **5-15× as many in-scope prospects** in a single triage run.

## Anti-patterns

- **Don't use the export as a cold-outbound list.** That breaks the implicit trust the connector extended and contaminates the warm-intro path. The export is a *targeting* layer, not an *outreach* layer.
- **Don't enrich the file with third-party data vendors.** This was a connector's private contact list; respecting that informs whether they'll share next time.
- **Don't merge multiple exports into a single pool without per-connector attribution.** Each in-scope row belongs to the connector who shared it; warm intros happen through them.
- **Don't ask before you have the triage motion ready.** If a connector hands over a file and we sit on it for two weeks, they'll think we don't take it seriously.

## Execution checklist

- [ ] Confirm the 2026-05-11 investor email landed with the ask included.
- [ ] Set up `raw-context/kivira-internal/li-exports/` directory with .gitignore on the raw files (they're PII).
- [ ] Build a small triage script: `scripts/li_export_triage.py` that takes a CSV and emits a sub-tier-mapped output similar to `accepts-subtier-mapped.csv`.
- [ ] When the first file arrives, run the triage end-to-end within 48 hours and return the ranked list to the connector with specific intro asks.
- [ ] Track yield: actual in-scope ratio per export, actual intros produced, actual conversations booked. This data feeds the yield-estimate refinement above.

## Refresh cadence

This pattern is run-once-per-connector. If the first 2-3 exports validate the expected yield, this becomes a standing motion in the GTM playbook. If they fall significantly below estimate, revisit the triage rules (likely anti-persona filter too aggressive, or the in-scope criteria too narrow for warm-intro paths).
