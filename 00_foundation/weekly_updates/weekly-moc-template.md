---
# When saving the dated file, set: name: WEEKLY_MOC_YYYY_MM_DD (underscores) — required for graph backlinks
title: "Kivira GTM Weekly — {{date:YYYY-MM-DD}}"
date: {{date:YYYY-MM-DD}}
status: draft
type: weekly-moc
recipients: ["Josh Pop", "Kivira Investors"]
---

# Week of {{date:MMMM D, YYYY}}

> **Purpose:** Decision document, not vanity metrics. **Section 1** = forwardable story; **Section 2** = evidence for the graph.
> **Length budget:** Aim **≤ ~500 words** in the full document (trim Section 2 tables if needed).
> **How to read:** Executive Summary = business translation for investors / founder. Operator Detail = internal verification with wiki-links.

---

## Evidence This Week (Section 2 hub)

Wire the weekly evidence files first, then paste **uppercase** `[[NODE]]` tokens here so `scripts/index_graph.py` registers backlinks (methodology: `knowledge_base/methodology/WEEKLY_MOC_GRAPH_RITUAL.md`).

- **HeyReach:** create `knowledge_base/gtm_signals/heyreach/weekly-evidence-{{date:YYYY-MM-DD}}.md`, set YAML `name:` to the ALL_CAPS id, then add one wikilink on this line.
- **Linear:** `knowledge_base/execution/linear/weekly-shipped-{{date:YYYY-MM-DD}}.md` — same.
- **InboxKit:** `knowledge_base/gtm_signals/inboxkit/weekly-health-{{date:YYYY-MM-DD}}.md` — same.
- **Heat (optional):** `knowledge_base/_index/heat-{{date:YYYY-MM-DD}}.md` with `name: HEAT_YYYY_MM_DD` — link here when published.

**Ritual pointer (indexed):** [[WEEKLY_MOC_GRAPH_RITUAL]]

---

# SECTION 1 — EXECUTIVE SUMMARY

> **Audience:** Founder, investors, advisors. **Plain English only. No `[[wiki-links]]`. No LEC- IDs. No tool acronyms unless unavoidable.** Josh should be able to forward Section 1 without editing.

## What Happened This Week

[2–3 bullets max. Translate operator work into business language.]

- Example: We built and activated the complete outbound system: 3 LinkedIn campaigns, 1,200+ targeted prospects, 16 warmed email inboxes. First sends went live Monday.
- Example: Resolved the final pre-launch infrastructure blocker (LinkedIn free-tier limits mapped and worked around).
- Example: 10 execution milestones shipped including list-building automation, campaign loading, and persona sequencing.

## What This Means for Kivira

[3–4 bullets. Value, risk, capital efficiency, strategic position.]

- **Pipeline generation is now systematic, not manual.** We can load 1,000+ prospects per week with zero manual research.
- **Capital efficiency:** This stack runs on a lean tooling budget versus hiring an outbound FTE.
- **De-risked targeting:** We validated the segment structure against real public data before spending sender reputation.
- **Next proof point:** By next Thursday we expect persona-level reply signal; that informs Q2 allocation.

## Key Metrics (Plain English)

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Prospects loaded | — | — | — |
| Outreach sends in flight | — | — | — |
| Replies / connection accepts | — | — | — |
| Demos booked | — | — | — |
| Infrastructure blockers resolved | — | — | — |

## Decisions Needed

- [ ] [Business-level decision with deadline, e.g., approve 2× volume if reply rate above threshold]
- [ ] [Strategic decision, e.g., CRM evaluation deadline]
- [ ] [Investor comms cadence, if any]

---

# SECTION 2 — OPERATOR DETAIL

> **Audience:** Josh (technical partner), internal team, future you. **Evidence-based.** Every number traces to an evidence node or is marked not yet measured. **Graph-native** wikilinks below.

## 1. The One Thing

> The single validated signal that should change our allocation this week.

**Claim:** [Write the validated insight here — e.g., Subtier 1A Operational Owner persona produced higher reply rate than Clinical Champion on workflow-themed copy]

**Evidence:**

- [[PAIN_SEGMENT_MATRIX]] — Segment priority alignment
- [[OUTREACH_BASELINE_METRICS]] — Reply/signal/meeting ratios
- [[WAVE_1_SCORING_FRAMEWORK]] — Pilot feasibility confirmation

**Decision required:** [Specific yes/no with deadline]

## 2. TAM Penetration Signal

> Which tiers did we touch? Are we still wedge-first?

```dataview
TABLE subtier, accounts_targeted, contacts_attempted, signals_generated, demos_booked
FROM "knowledge_base/methodology"
WHERE file.name contains "WAVE" OR file.name contains "OUTREACH"
SORT file.name ASC
```

| Tier | Subtier | Accounts Touched | Signals | Demos Booked | Status |
|------|---------|------------------|---------|--------------|--------|
| Tier 1 — Provider Wedge | 1A Mid-market | — | — | — | 🔲 |
| | 1B PCP Groups | — | — | — | 🔲 |
| | 1C VBC Providers | — | — | — | 🔲 |
| Tier 2 — Risk Bearing | 2A ACOs | — | — | — | 🔲 |
| | 2B VBC Enablers | — | — | — | 🔲 |
| | 2C Care Mgmt | — | — | — | 🔲 |
| Tier 3 — Enterprise | 3A Health Systems | — | — | — | 🔲 |
| | 3B IDNs | — | — | — | 🔲 |
| | 3C Regional Payers | — | — | — | 🔲 |

**Narrative:** [Are we still wedge-first on Tier 1? Did any Tier 2/3 signal surprise us?]

## 3. Signal Flow by Persona (SCV)

> Search → Capture → Validate. Which persona-message pair proved real?

| Persona | Message Theme | Search (Sent) | Capture (Reply/Accept) | Validate (Demo/Intro) |
|---------|---------------|---------------|------------------------|----------------------|
| [[BUYER_PERSONA_OPERATIONAL_BUYER\|Operational Owner]] | Workflow / ops | — | — | — |
| [[BUYER_PERSONA_CLINICAL_CHAMPION\|Clinical Champion]] | Outcomes / safety | — | — | — |
| [[BUYER_PERSONA_TECHNOLOGY_GATEKEEPER\|Tech Gatekeeper]] | Integration / security | — | — | — |
| Economic Buyer | ROI / revenue | — | — | — |
| BH / Quality Influencer | Quality / compliance | — | — | — |

**Validated pair:** [Which persona + message theme generated a booked demo or warm intro?]

**Kill list:** [Which persona + message theme produced zero signals after N touches?]

## 4. Infrastructure Pulse

> If the pipes break, nothing else matters.

| System | Health | Notes | Agent Action |
|--------|--------|-------|--------------|
| InboxKit — 16 mailboxes | 🟢 / 🟡 / 🔴 | [Domain health, warmup status] | [Auto-rotate? Pause? Alert?] |
| HeyReach — sender rotation | 🟢 / 🟡 / 🔴 | [Connection limits, reply routing] | [Auto-pause campaign?] |
| Linear — execution tracking | 🟢 / 🟡 / 🔴 | [Issues shipped this week] | [Update graph nodes] |
| Book a Demo — website | 🟢 / 🟡 / 🔴 | [Form submissions, routing] | [N/A until CRM] |

## 5. Experiment Velocity

> What did we ship? What did we learn?

| Experiment | Hypothesis | Result | Decision | Node |
|------------|------------|--------|----------|------|
| [e.g., Wave 1A Operational Owner v1] | Workflow copy outperforms clinical copy | [Reply rate, meeting rate] | 🟢 Scale / 🟡 Iterate / 🔴 Kill | [[wave1a_heyreach_copy]] |
| | | | | |

**New nodes created this week:** [List emergent nodes that reached validated status]

**Orphans killed this week:** [Nodes with 0 heat that were archived]

## 6. 30 / 60 / 90 Progress

> Where are we on the execution cadence?

| Horizon | Target | Current | Gap | Graph Evidence |
|---------|--------|---------|-----|----------------|
| **30d** | Claims matrix; discovery question bank; CRM tagging | — | — | [[GTM_30_60_90_EXECUTION_CADENCE]] |
| **60d** | 10+ discovery calls logged; security packet aligned | — | — | [[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]] |
| **90d** | 1–2 written pilots / LOIs | — | — | [[PILOT_SITE_ACQUISITION_PRIORITY]] |

## 7. Graph Health Snapshot

> Self-governance: what's alive, what's dead, what's validated.

```dataview
TABLE domain, status, length(file.inlinks) as "Inbound"
FROM "knowledge_base"
WHERE status = "validated" OR status = "emergent"
SORT length(file.inlinks) DESC
LIMIT 15
```

- **Total validated nodes:** [From GRAPH_INDEX]
- **New emergent nodes this week:** [Count]
- **Nodes promoted to validated:** [Count — requires 2+ citations]
- **Orphans flagged for archive:** [Count — 0 inbound, 0 heat]
- **Broken wiki-links:** [Count — from graph health check]

## 8. Human Decision Required

> The agent proposes. The human decides.

- [ ] **Decision 1:** [Specific, with context from above]
- [ ] **Decision 2:** [Specific, with deadline]
- [ ] **Decision 3:** [Specific, with owner]

## 9. Next Week's Focus

> Based on validated signal, what do we hunt?

1. [Subtier/persona priority]
2. [Message theme to test]
3. [Infrastructure fix or scale action]

---

## What This Proves (Strategy Links)

This weekly validates the following strategic nodes (Section 2 only; keep Section 1 plain English):

- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — 9×5 structure exercised
- [[OUTREACH_WAVE_STRUCTURE]] — Wave execution live
- [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]] — End-to-end operational
- [[GTM_30_60_90_EXECUTION_CADENCE]] — Milestones on track
- [[PRIMARY_CARE_WEDGE_ICP]] — Wedge targeting active
- [[WEEKLY_MOC_GRAPH_RITUAL]] — Ritual that produced this cohesion

---

*Context OS — dual-layer weekly MOC v2. Navigation: [CLAUDE.md](CLAUDE.md) · graph ritual in `knowledge_base/methodology/WEEKLY_MOC_GRAPH_RITUAL.md`*
