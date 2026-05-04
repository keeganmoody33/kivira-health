---
title: "Investor email — Week of May 4, 2026 (copy-paste)"
date: 2026-05-04
status: draft
type: investor-email
derived_from:
  - "[[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]]"
  - "[[WEEKLY_LINEAR_SHIPPED_2026_05_04]]"
  - "[[WEEKLY_INBOXKIT_HEALTH_2026_05_04]]"
---

# Weekly Email (Copy-Paste Ready)

**Subject:** [kivira.health] Week of May 4 — Machine built. 1,219 leads loaded. Signal generation starts now.

---

## 1. The One Thing

We resolved the final infrastructure blockers (LEC-39 LinkedIn cap, LEC-42 campaign activation) and launched 3 HeyReach campaigns Monday morning with 1,219 leads across the 9-subtier × 5-persona structure. The machine is live. We expect first signal data (replies, accepts) by Thursday.

## 2. What We Shipped (10 Linear issues → Done)

| Issue | Deliverable | Evidence |
|-------|-------------|----------|
| LEC-33 | CMS MSSP pipeline built and validated | `build_list_1a.py` exercises real public data |
| LEC-34 | HeyReach zero-budget sourcing canonical | `_system/agent_workflows/heyreach-zero-budget-sourcing.md` |
| LEC-35 | MCP load runbook shipped | Agent can load HeyReach via MCP autonomously |
| LEC-36 | 14-day execution plan for Josh | `00_foundation/_synthesis/wave-1a-execution-schedule-2026-05-01.md` |
| LEC-37 | Platform limits, sequence, MCP schema verified | Context7 research ingested |
| LEC-38 | Export scripts + persona rules shipped | `scripts/export_heyreach_leads.py` |
| LEC-39 | BLOCKER resolved: LinkedIn personalized-note cap | Free-tier constraint mapped; sequence adjusted |
| LEC-41 | 1A wedge taxonomy filter + NPPES proxy | `build_list_1a.py` filters by org-size |
| LEC-42 | HeyReach account activation + campaigns finalized | 3 campaigns live, 1 draft |
| LEC-45 | Cross-subtier baseline + 9×5 adoption | Canonical structure validated across tiers |

Canonical evidence rollup: [[WEEKLY_LINEAR_SHIPPED_2026_05_04]].

## 3. Signal Flow (Search → Capture → Validate)

| Persona | Search (Leads Loaded) | Capture (In Progress) | Validate (Replies/Demos) |
|---------|------------------------|------------------------|---------------------------|
| Operational Owner (2A ACO) | 359 | 35 connection requests | Day 1 — pending |
| Clinical Champion (1C Provider) | 590 | 34 connection requests | Day 1 — pending |
| Baseline 9-Subtier | 270 | 35 connection requests | Day 1 — pending |
| **Total** | **1,219** | **104** active | **0** (expected) |

Manual conversations (non-campaign): 4 total, 1 positive signal, 3 neutral. These predate formal launch.

Source: [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]].

## 4. Infrastructure Pulse

| System | Health | Evidence |
|--------|--------|----------|
| HeyReach | Green — 3 campaigns active, 1 draft | Sender healthy, 104 connections in flight — [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]] |
| InboxKit | Yellow-green — 16 mailboxes warming; sequencer next | 6 KPI-active domains; cached warmup day ~8 and health score ~98.4; UI “Low Activity” on 7d analytics (bounce 0%) — [[WEEKLY_INBOXKIT_HEALTH_2026_05_04]] |
| Linear | Green — 10/14 shipped | LEC-32 in progress (parent launch thread) — [[WEEKLY_LINEAR_SHIPPED_2026_05_04]] |
| List Building | Green — Canonical | 9-subtier × 5-persona structure exercised — [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] |

### Pulling InboxKit data (no bad path)

Do **not** use `GET /v1/mailboxes` (not a valid route). Use **`POST /v1/api/mailboxes/list`** with `Authorization: Bearer …` and `X-Workspace-Id`, or run the repo sweep:

```bash
export INBOXKIT_API_KEY='…'
bash scripts/inboxkit_api_smoke.sh
```

MCP (OAuth, no REST key): `https://mcp.inboxkit.com/mcp` — see [[WEEKLY_INBOXKIT_HEALTH_2026_05_04]].

## 5. Experiment Velocity

| Experiment | Hypothesis | Result | Decision |
|------------|------------|--------|----------|
| 9×5 list-building pipeline | Can we build targeted lists at scale | Scripts run; 1,219 leads loaded — [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]] | Canonical |
| HeyReach MCP integration | Can agent load campaigns autonomously | Runbook shipped; LEC-35 done — [[WEEKLY_LINEAR_SHIPPED_2026_05_04]] | Operational |
| Wave 1A copy (3 variants) | Operational/Clinical/Baseline angles | 104 sends in flight — [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]] | Measure by May 8 |
| LinkedIn free-tier sequencing | Personal note cap workaround | Blocker resolved; sequence adjusted — LEC-39 | Shipped |

## 6. 30 / 60 / 90 Progress

| Horizon | Target | Current | Gap |
|---------|--------|---------|-----|
| 30d | Claims matrix; discovery bank; CRM tagging | Discovery questions in [[DISCOVERY_QUESTIONS_PRIMARY_CARE_BUYER]] | CRM still “Book a Demo” |
| 60d | 10+ discovery calls logged | 0 formal calls; 1 positive manual signal — [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]] | Reply-to-meeting conversion |
| 90d | 1–2 written pilots / LOIs | Pre-launch | First signal expected May 8 |

## 7. What We Learned

- The 9-subtier taxonomy holds at scale — `build_list_1a.py` filtered 1,219 leads with zero manual intervention — [[WEEKLY_LINEAR_SHIPPED_2026_05_04]] (LEC-41, LEC-45), [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]].
- HeyReach MCP path works — agent load path documented; LEC-35 shipped — [[WEEKLY_LINEAR_SHIPPED_2026_05_04]].
- LinkedIn free-tier personalized notes have a hard cap — sequence adjusted — LEC-39 — [[WEEKLY_LINEAR_SHIPPED_2026_05_04]].
- 1,219 leads is the right batch size for Wave 1 — not too small to learn, not oversized for reputation — operator judgment aligned with [[WEEKLY_HEYREACH_EVIDENCE_2026_05_04]].

## 8. Next Week (May 5–11)

1. Monitor HeyReach reply/accept rates by persona (target: first signal by Thursday).
2. Complete 1C grind (LEC-40: ~500 URLs remaining) — [[WEEKLY_LINEAR_SHIPPED_2026_05_04]].
3. Pull InboxKit deliverability data daily — flag domain health drops — [[WEEKLY_INBOXKIT_HEALTH_2026_05_04]].
4. If Operational Owner angle hits >5% reply rate, draft 2× volume expansion — **pending measurement**.

## 9. Human Decision Required

- [ ] Approve 2× volume on winning persona — pending signal data (decision by May 8).
- [ ] CRM evaluation — HubSpot/Salesforce for pipeline tracking vs “Book a Demo” (target: May 15).
- [ ] Investor update frequency — Weekly email sufficient, or add brief Slack/Notion surface?

---

## Thursday 7pm ritual (reference)

| Time | Action |
|------|--------|
| Monday 9am | Review Linear — pick 2–3 issues for the week |
| Mon–Wed | Execute; deposit evidence daily |
| Thursday 4pm | Evidence pull: HeyReach + Linear + InboxKit |
| Thursday 5pm | Deposit into graph nodes |
| Thursday 6pm | Generate weekly in Cursor |
| Thursday 6:30pm | Review, edit Human Decisions |
| Thursday 7:00pm | Send to Josh + investors |
| Thursday 7:15pm | `git commit` weekly MOC |

---

*Numbers in this email match evidence nodes dated 2026-05-04; refresh before send if more than 24h stale.*
