---
# Set name when saving the dated file, e.g. name: WEEKLY_MOC_2026_05_04 — required for graph backlinks
title: "Kivira GTM Weekly — {{date:YYYY-MM-DD}}"
date: {{date:YYYY-MM-DD}}
status: draft
type: weekly-moc
recipients: ["Josh Pop", "Kivira Investors"]
---

# Week of {{date:MMMM D, YYYY}}

## Evidence This Week

**Graph hub** — Create the three weekly evidence files, set each file’s YAML `name:` to the ALL_CAPS id, then paste one wikilink line per surface here (see [[WEEKLY_MOC_GRAPH_RITUAL]]). Optionally mirror those three ids under an `evidence_nodes:` list in *this* file’s frontmatter.

- **HeyReach:** create `knowledge_base/gtm_signals/heyreach/weekly-evidence-{{date:YYYY-MM-DD}}.md`, set YAML `name:` to the ALL_CAPS id, then paste the matching wikilink on this line.
- **Linear:** `knowledge_base/execution/linear/weekly-shipped-{{date:YYYY-MM-DD}}.md` — same pattern.
- **InboxKit:** `knowledge_base/gtm_signals/inboxkit/weekly-health-{{date:YYYY-MM-DD}}.md` — same pattern.

---

> **Purpose:** Decision document, not status report. Every claim links to a validated graph node (✅) or is flagged as emergent (🌱). The investor email is optional; **this file is the citation hub.**

---

## 1. The One Thing

> The single validated signal that should change our allocation this week.

**Claim:** [Write the validated insight here — e.g., "Subtier 1A Operational Owner persona produced 3x reply rate vs Clinical Champion on workflow-themed copy"]

**Evidence:**
- [[PAIN_SEGMENT_MATRIX]] — Segment priority alignment
- [[OUTREACH_BASELINE_METRICS]] — Reply/signal/meeting ratios
- [[WAVE_1_SCORING_FRAMEWORK]] — Pilot feasibility confirmation

**Decision required:** [Specific yes/no with deadline, e.g., "Approve 2x volume on 1A Operational Owner by EOD Friday"]

---

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

---

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

---

## 4. Infrastructure Pulse

> If the pipes break, nothing else matters.

| System | Health | Notes | Agent Action |
|--------|--------|-------|--------------|
| InboxKit — 16 mailboxes | 🟢 / 🟡 / 🔴 | [Domain health, warmup status] | [Auto-rotate? Pause? Alert?] |
| HeyReach — sender rotation | 🟢 / 🟡 / 🔴 | [Connection limits, reply routing] | [Auto-pause campaign?] |
| Linear — execution tracking | 🟢 / 🟡 / 🔴 | [Issues shipped this week] | [Update graph nodes] |
| Book a Demo — website | 🟢 / 🟡 / 🔴 | [Form submissions, routing] | [N/A until CRM] |

---

## 5. Experiment Velocity

> What did we ship? What did we learn?

| Experiment | Hypothesis | Result | Decision | Node |
|------------|------------|--------|----------|------|
| [e.g., Wave 1A Operational Owner v1] | Workflow copy outperforms clinical copy | [Reply rate, meeting rate] | 🟢 Scale / 🟡 Iterate / 🔴 Kill | [[wave1a_heyreach_copy]] |
| | | | | |

**New nodes created this week:** [List emergent nodes that reached validated status]
**Orphans killed this week:** [Nodes with 0 heat that were archived]

---

## 6. 30 / 60 / 90 Progress

> Where are we on the execution cadence?

| Horizon | Target | Current | Gap | Graph Evidence |
|---------|--------|---------|-----|----------------|
| **30d** | Claims matrix; discovery question bank; CRM tagging | — | — | [[GTM_30_60_90_EXECUTION_CADENCE]] |
| **60d** | 10+ discovery calls logged; security packet aligned | — | — | [[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]] |
| **90d** | 1–2 written pilots / LOIs | — | — | [[PILOT_SITE_ACQUISITION_PRIORITY]] |

---

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

---

## 8. Human Decision Required

> The agent proposes. The human decides.

- [ ] **Decision 1:** [Specific, with context from above]
- [ ] **Decision 2:** [Specific, with deadline]
- [ ] **Decision 3:** [Specific, with owner]

---

## 9. Next Week's Focus

> Based on validated signal, what do we hunt?

1. [Subtier/persona priority]
2. [Message theme to test]
3. [Infrastructure fix or scale action]

---

*Generated from Kivira Context-OS v2 — [[CLAUDE.md]] · [[CONTEXT_OS_OPERATING_RHYTHM]]*
