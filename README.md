# Kivira.Health — GTM Context OS

A healthcare-tuned implementation of the [Context OS](https://github.com/jacob-dietle/gtm-context-os-quickstart) pattern, wrapped around the outbound, list-building, and weekly-reporting motion that runs Kivira's go-to-market.

---

## What this is

This repo is not a generic codebase. It is a **live GTM operating system** with three things stacked on top of each other:

1. A **knowledge graph** of validated Kivira positioning, ICP, personas, TAM, billing rules, and clinical-safety language (Layer 1 in `knowledge_base/`).
2. **Operational documents** that compose from the graph — positioning, messaging, weekly MOCs to Josh and investors (Layer 2 in `00_foundation/`).
3. **Repo-local execution code** — a TAM builder, a 9-subtier GTM architecture, HeyReach/InboxKit/Linear pipelines, and agent workflow specs — that consumes the graph as policy and emits CSVs, briefs, and campaign loads.

The graph compounds across sessions so AI agents (Cursor, Claude Code, Codex) and humans (founder, GTM lead) navigate, write, and execute against the same source of truth.

**Current scale (per latest `_system/GRAPH_INDEX.md`):** 109 indexed nodes, 668 resolved wiki-links, 15 hub nodes, 1 broken link, tag-sprawl 33% (Warning band, tracked in `_system/GRAPH_HEALTH_REPORT.md`).

---

## Why this exists

Every new AI session forgets. Every spreadsheet drifts. Every founder restates the same TAM math three different ways depending on which document is open. Kivira sells into clinics and ACOs where claims discipline is non-negotiable — "autonomous diagnosis," made-up CPT codes, or numbers without provenance will torch credibility on the first call.

The Context OS pattern solves the AI-amnesia problem. Kivira's adaptation adds the constraints that healthcare GTM actually needs: evidence-tagged sources, CDS-not-diagnosis framing, write-locked positioning, and a weekly cadence where every claim that goes to investors links back to a node with a `source:` line.

---

## Relationship to Context OS (what's inherited)

The upstream framework is **Jacob Dietle's [`gtm-context-os-quickstart`](https://github.com/jacob-dietle/gtm-context-os-quickstart)**, vendored at `gtm-context-os-quickstart/` with its README and templates intact.

Inherited verbatim:

| Concept | Inherited mechanic | Where it lives |
|---|---|---|
| Two-layer architecture | `knowledge_base/` (atomic) + `00_foundation/` (operational) | Both root folders |
| Node lifecycle | `emergent` → `validated` → `canonical` (`archived`/`superseded` for retirement) | Frontmatter `status:` on every node |
| Graph structure | `[[wiki-links]]` in `related_concepts:` + body | All knowledge_base nodes |
| Node format | YAML frontmatter (`name`, `domain`, `node_type`, `status`, `tags`, `topics`, `source`, `related_concepts`) | `gtm-context-os-quickstart/templates/node_template.md` |
| AI navigation | `CLAUDE.md` at repo root as the canonical guide | `CLAUDE.md` |
| Operating loop | SENSE → ORIENT → ACT → DEPOSIT (stigmergic coordination) | `_system/CONTEXT_OS_OPERATING_RHYTHM.md` |
| Core commands | `/ingest`, `/graph-health` | `.claude/commands/` (Kivira fork) and `gtm-context-os-quickstart/.claude/commands/` (upstream) |
| Skill pattern | `.claude/skills/<name>/SKILL.md` referencing canonical specs | Kivira-local skills + upstream `context-os-basics`, `context-gap-analysis`, `epistemic-context-grounding` |

Explicitly **un-inherited** (v1 retired, see `CLAUDE.md` HARD RULE #8):

- `taxonomy.yaml` and `ontology.yaml` — moved to `_system/_archive/v1-ceremony/`. Tags now emerge from observed corpus heat. Do not reintroduce.

---

## Kivira-specific adaptations

What this repo adds on top of the upstream framework:

### 1. Healthcare evidence discipline

Every node distinguishes public/legal copy from third-party research from internal notes:

- Tags: `source-public-web`, `source-research-synthesis`, `source-internal-doc`.
- Body lines: `[VERIFIED: …]`, `[INFERRED: …]`, `[UNVERIFIABLE]`.
- Canonical reference: `knowledge_base/methodology/EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS.md`.

### 2. CDS-not-diagnosis guardrail

Product framing is anchored to clinical decision support, not autonomous diagnosis. Outbound copy, positioning, messaging, and weekly MOCs all route through `knowledge_base/technical/CDS_NOT_DIAGNOSIS_FRAMING.md` (20 inbound links). Agents must not break this; humans revert on sight.

### 3. Agent write-locks on Layer 2 strategic docs

`00_foundation/positioning/` and `00_foundation/messaging/` are human-authored. Agents compose from them — they do not rewrite them. Codified in `CLAUDE.md` "Agent Constraints" #1 and in `.cursorrules`.

### 4. Dual-layer weekly MOC ritual

Each Friday produces `00_foundation/weekly_updates/YYYY-MM-DD.md` with:

- **Section 1** — plain-English executive summary, forwardable to Josh / investors, **no** wiki-links, no jargon.
- **Section 2** — operator detail, uppercase `[[NODE]]` wiki-links, every number linked to an evidence node or marked `[UNVERIFIABLE]`.

Three evidence-node deposits seed the MOC each week:

- HeyReach → `knowledge_base/gtm_signals/heyreach/weekly-evidence-YYYY-MM-DD.md`
- Linear → `knowledge_base/execution/linear/weekly-shipped-YYYY-MM-DD.md`
- InboxKit → `knowledge_base/gtm_signals/inboxkit/weekly-health-YYYY-MM-DD.md`

Canonical procedure: `knowledge_base/methodology/WEEKLY_MOC_GRAPH_RITUAL.md`. Template: `00_foundation/weekly_updates/weekly-moc-template.md`.

### 5. Repo-local fast-lookup index (replaces the external CLI for navigation)

Upstream Context OS assumes a separate `context-os` CLI for heat / graph-exec / context queries. Kivira ships an in-repo equivalent:

```bash
python scripts/index_graph.py
```

Outputs:

- `_system/GRAPH_INDEX.md` — human-readable Path Map (one line per node, grep-able), Backlink Index, hub list, tag frequency, orphan list.
- `_system/GRAPH_INDEX.json` — machine-readable full index.

`CLAUDE.md` Fast Path explicitly says: read `_system/GRAPH_INDEX.md` before grepping. References to the external `context-os` CLI remain in `_system/CONTEXT_OS_OPERATING_RHYTHM.md` for heat queries, but the in-repo index is the day-to-day surface.

### 6. Repo-local TAM builder + 9-subtier GTM architecture

Not in upstream. Implemented as a Python package with a CLI:

- `tam_builder/` — normalize, estimate (CoCM opportunity), tier, route personas, generate briefs.
- `scripts/kivira_tam_builder.py` — thin entrypoint (`python -m tam_builder` equivalent).
- `tests/` — contract tests over fixtures.
- `fixtures/` — synthetic-first CSVs (no PHI committed).

Anchor policy nodes:

- `knowledge_base/methodology/GTM_TIER_ARCHITECTURE_9_SUBTIERS.md` (36 inbound)
- `knowledge_base/business/THREE_SEGMENT_ICP_FRAMEWORK.md` (23 inbound)
- `knowledge_base/methodology/PERSONA_TITLE_DICTIONARY_BY_SUBTIER.md` (23 inbound)

### 7. Canonical workflow specs that skills wrap

Skills under `.claude/skills/<name>/SKILL.md` are intentionally thin — they delegate to canonical workflow specs in `_system/agent_workflows/<name>.md`. Single source of truth, multiple wrappers.

### 8. Tool-scoped agents

Defined in `CLAUDE.md` and `_system/CONTEXT_OS_OPERATING_RHYTHM.md`:

| Tool | Owns | Cannot touch |
|---|---|---|
| Cursor (primary GTM agent) | `knowledge_base/gtm_signals/`, weekly MOCs, copy drafts | Layer 2 positioning/messaging, validated personas, TAM tier files |
| Claude Code (infra) | `knowledge_base/execution/`, graph health, ingestion | Weekly MOCs (Cursor owns the template) |
| Codex (Python/experiments) | `scripts/`, `tam_builder/`, `tests/`, branches `experiment/codex-YYYY-MM-DD/` | `main` directly |
| Obsidian | Read + navigate + Canvas | Never writes to tracked files via plugins |

### 9. Multi-client replication pattern

Documented (not yet exercised) in `_system/CONTEXT_OS_OPERATING_RHYTHM.md` under "Multi-Client Replication" — the structure forks cleanly into `~/gtm-vaults/<client>/`, with the upstream quickstart shared and the `knowledge_base/` per-client.

---

## Architecture

```
KIVIRA.HEALTH/
├── CLAUDE.md                       # Canonical AI navigation, agent constraints, tool scopes
├── .cursorrules                    # Cursor-specific enforcement; defers to CLAUDE.md
├── README.md                       # This file
│
├── knowledge_base/                 # LAYER 1 — atomic nodes (the graph)
│   ├── business/                   # ICP, personas, TAM, buyer model, market signals
│   ├── methodology/                # GTM motion, tiering, sequencing, evidence rules
│   ├── technical/                  # CDS framing, FHIR, HIPAA, CPT/BHI billing
│   ├── execution/                  # Linear weekly digests, founder follow-up packages
│   ├── gtm_signals/                # HeyReach + InboxKit weekly evidence
│   ├── _index/                     # heat-YYYY-MM-DD.md snapshots
│   ├── _archive/                   # Retired nodes (do not delete validated)
│   └── emergent/                   # New, not-yet-validated concepts
│
├── 00_foundation/                  # LAYER 2 — operational composition (human-authored)
│   ├── positioning/                # WRITE-LOCKED to agents
│   ├── messaging/                  # WRITE-LOCKED to agents (HeyReach copy lives here)
│   ├── _synthesis/                 # GTM plan, wave execution schedules, packaged copy
│   └── weekly_updates/             # Friday MOCs + investor email side-effects
│
├── _system/                        # Operating rhythm + index artifacts
│   ├── CONTEXT_OS_OPERATING_RHYTHM.md  # v2 weekly loop (Friday 45 min)
│   ├── GRAPH_INDEX.md / .json      # Generated; read before grepping
│   ├── GRAPH_HEALTH_REPORT.md      # Latest /graph-health output
│   ├── agent_workflows/            # Canonical workflow specs (source of truth)
│   └── _archive/v1-ceremony/       # Retired taxonomy.yaml / ontology.yaml
│
├── .claude/
│   ├── commands/                   # /ingest, /graph-health (Kivira fork)
│   ├── skills/                     # Thin SKILL.md wrappers → _system/agent_workflows/
│   └── settings.local.json
│
├── tam_builder/                    # Repo-local Python package
│   ├── cli.py                      # `normalize-accounts | estimate-cocm | tier-accounts | route-personas | generate-briefs`
│   ├── normalize.py · tiering.py · personas.py · estimation.py · briefing.py
│   ├── adapters.py                 # synthetic | live-public CoCM adapters
│   ├── aco_attack.py · aco_persona_rules.py · persona_rules.py · pilot_filters.py
│   └── josh_pilot/                 # ingest / filter / score / enrich / gate / export
│
├── scripts/                        # Thin CLI entrypoints (Codex territory)
│   ├── index_graph.py              # Refreshes _system/GRAPH_INDEX.md|.json
│   ├── kivira_tam_builder.py       # Thin entrypoint for tam_builder.cli
│   ├── run_josh_pilot_pipeline.py  # End-to-end Josh pilot motion
│   ├── build_aco_*.py              # Wave 2A ACO attack list builders
│   ├── build_list_*.py             # Wave 1A/1C/2A/2B/2C builders
│   ├── export_heyreach_leads.py    # CSV → HeyReach-ready
│   ├── heyreach_*.py · load_josh_heyreach_list.py · wire_josh_heyreach_campaigns.py
│   ├── heyreach_weekly_pull.py · heyreach_accepts_pull.py
│   ├── inboxkit_api_smoke.sh       # InboxKit POST /v1/api/mailboxes/list smoke
│   ├── linear_weekly_pull.py       # Linear → weekly evidence node draft
│   ├── spider_*.py · parallel_persona_extractor.py
│   ├── airtable_sync.py · clay_roundtrip.py
│   └── validate_pipeline_outputs.py
│
├── tests/                          # Contract + behavior tests over fixtures
├── fixtures/                       # Synthetic-first CSVs + run artifacts
│   └── josh_drs_group_2026/        # Active Josh pilot working set
│
├── raw-context/                    # Raw ingests (NOT the graph)
│   ├── MARKETANALYSIS.md           # Canonical market synthesis (the root copy is a pointer)
│   ├── kivira-public/              # Firecrawl + Jina exports of kivira.health
│   ├── kivira-internal/            # PDF→md conversions of internal decks, meeting notes
│   └── kivira-tam-docs/
│
└── gtm-context-os-quickstart/      # Upstream framework (vendored, do not edit)
    ├── CLAUDE.md · README.md
    ├── .claude/commands/{quickstart,ingest}.md
    ├── .claude/skills/{context-os-basics,context-gap-analysis,epistemic-context-grounding}/
    └── templates/{CLAUDE_MD_STARTER,node_template}.md
```

---

## How the system works

### The weekly loop (Fridays, 45 min — `_system/CONTEXT_OS_OPERATING_RHYTHM.md`)

```
SENSE   (10 min) → run python scripts/index_graph.py; read GRAPH_INDEX.md hub & heat
ORIENT  (10 min) → click through hubs, check infra risks in gtm_signals/inboxkit/
ACT     (20 min) → deposit HeyReach/Linear/InboxKit weekly evidence nodes;
                    compose weekly MOC from weekly-moc-template.md
DEPOSIT (5 min)  → git commit "weekly: YYYY-MM-DD — …"; copy Section 1 to email
```

### Daily / as-needed

- **HeyReach reply with signal** → new node under `knowledge_base/gtm_signals/heyreach/`, `status: emergent`.
- **InboxKit deliverability alert** → new node under `knowledge_base/gtm_signals/inboxkit/`.
- **Linear issue shipped** → new node under `knowledge_base/execution/linear/`.

### Monthly graph hygiene

- Run `/graph-health` (`.claude/commands/graph-health.md`) → updates `_system/GRAPH_HEALTH_REPORT.md`.
- Archive nodes with `heat: 0` and `status: emergent` for 30+ days **except** external-validation nodes (per `HEAT_EXCEPTION_EXTERNAL_VALIDATION`).
- Do **not** prune taxonomy or rewrite governance — v2 has none.

---

## Recommended operator workflow

You are a new operator. Do this in order.

1. **Read `CLAUDE.md` end-to-end.** This is the contract. Internalize the four Agent Constraints and the tool scopes.
2. **Refresh the index:**
   ```bash
   python scripts/index_graph.py
   ```
3. **Read `_system/GRAPH_INDEX.md`.** Skim the Path Map. Note the hub nodes (>10 inbound) — those are load-bearing.
4. **Read the rhythm doc:** `_system/CONTEXT_OS_OPERATING_RHYTHM.md`.
5. **Skim the four most-linked nodes** for current state:
   - `knowledge_base/business/PRIMARY_CARE_WEDGE_ICP.md`
   - `knowledge_base/methodology/GTM_TIER_ARCHITECTURE_9_SUBTIERS.md`
   - `knowledge_base/methodology/PERSONA_TITLE_DICTIONARY_BY_SUBTIER.md`
   - `knowledge_base/methodology/OUTREACH_BASELINE_METRICS.md`
6. **Read the latest weekly MOC** in `00_foundation/weekly_updates/` to see what good output looks like.
7. **Run a no-op TAM builder pass** to confirm Python env:
   ```bash
   python -m tam_builder normalize-accounts --input fixtures/raw_accounts.csv --output /tmp/normalized.csv
   ```
8. **Commit before doing anything substantive:**
   ```bash
   git add -A && git commit -m "pre-agent: <tool> <intent>"
   ```

---

## Knowledge ingestion

### Path A — Use the `/ingest` command (Claude Code or Cursor)

```
/ingest <path/to/raw-file.md>
/ingest this conversation
```

The command (`.claude/commands/ingest.md`) extracts concepts, generates frontmatter, and writes nodes to the matching domain. Status starts `emergent`. Reuses existing tags from the corpus by frequency.

### Path B — Manual node creation

1. Drop the raw source under `raw-context/kivira-internal/` (default: keep summary + transcript both).
2. Copy `gtm-context-os-quickstart/templates/node_template.md` into the right domain folder.
3. Fill complete frontmatter — at least 3 `related_concepts` wiki-links, valid `source:` block, first tag = domain.
4. Refresh the index: `python scripts/index_graph.py`.
5. Confirm the new node appears in `_system/GRAPH_INDEX.md` Path Map.

### Naming convention

- Node filename and frontmatter `name:` use `UPPER_SNAKE_CASE`.
- Weekly evidence nodes: `name: WEEKLY_HEYREACH_EVIDENCE_2026_05_20` (matches filename `weekly-evidence-2026-05-20.md`) — required for backlink resolution.
- See `WEEKLY_MOC_GRAPH_RITUAL` for the exact pattern.

### Meeting notes

Follow `_system/agent_workflows/meeting-notes-ingest.md`:

- Raw transcript → `raw-context/kivira-internal/<topic>-meeting-notes-YYYY-MM-DD.md`.
- Durable concepts → `knowledge_base/` as separate nodes; do not duplicate transcript text in the graph.

---

## Context retrieval and synthesis

### Fast path (90% of queries)

```bash
python scripts/index_graph.py
# then read _system/GRAPH_INDEX.md
```

- **Find a node:** grep the Path Map: `grep PRIMARY_CARE _system/GRAPH_INDEX.md`.
- **What links here?** Read the Backlink Index for that node.
- **What's hot?** Read the `## Hubs` and the most-recent `knowledge_base/_index/heat-*.md`.

### Slow path

- Start at `00_foundation/_synthesis/` for the latest GTM plan / wave plan.
- Drill into `knowledge_base/business/` (ICP, TAM), `methodology/` (motion), `technical/` (CDS, FHIR, HIPAA).
- Follow `[[wiki-links]]` between nodes.

### External `context-os` CLI

Referenced in `_system/CONTEXT_OS_OPERATING_RHYTHM.md` for heat / graph-exec / co-access queries (`context-os query heat --time 7d`). Not vendored in-repo. The repo-local `scripts/index_graph.py` covers the path-map, backlink, hub, and orphan needs that the day-to-day loop has. If you install the upstream CLI separately, scope it to Claude Code per `CLAUDE.md` tool scopes.

---

## Skills, agents, commands, automations

### Repo-local skills (`.claude/skills/`)

Each is a thin SKILL.md that points at a canonical spec under `_system/agent_workflows/`:

| Skill | Canonical spec | Purpose |
|---|---|---|
| `tam-account-intake` | `agent_workflows/tam-account-intake.md` | Normalize arbitrary list CSVs into the canonical account schema |
| `persona-router` | `agent_workflows/persona-router.md` | Route accounts to buying-committee personas |
| `tiered-outreach-planner` | `agent_workflows/tiered-outreach-planner.md` | Apply tier logic + outreach recommendations |
| `cocm-opportunity-estimate` | `agent_workflows/cocm-opportunity-estimate.md` | Repo-local CoCM modeled opportunity |
| `claims-safe-outbound` | `agent_workflows/claims-safe-outbound.md` | Grade-aware outbound briefs inside CDS guardrails |

### Repo-local commands (`.claude/commands/`)

- `/ingest` — process raw content into the graph.
- `/graph-health` — produce `_system/GRAPH_HEALTH_REPORT.md`.

### Operator-level workflows (not yet skills)

In `_system/agent_workflows/`:

- `heyreach-mcp-load-runbook.md` — MCP-driven HeyReach lead loads (intentionally not Python-scripted; see "Why MCP-driven, not scripted" inside).
- `heyreach-zero-budget-sourcing.md` — full sourcing process across 9 subtiers.
- `wave1-small-batch-iteration.md` — 20–30 lead batches per subtier.
- `aco-attack-list-build.md` — Wave 2A ACO motion.
- `josh-pilot-linkedin-enrichment.md` — Josh Drs Group pilot enrichment waterfall.
- `meeting-notes-ingest.md` — meeting → raw-context → graph.

### Upstream skills (`gtm-context-os-quickstart/.claude/skills/`)

- `context-os-basics` — foundational patterns (read first if you're new).
- `context-gap-analysis` — check what exists before building.
- `epistemic-context-grounding` — ground decisions in domain knowledge.

### TAM builder commands

```bash
python -m tam_builder normalize-accounts --input <raw.csv> --output <norm.csv>
python -m tam_builder estimate-cocm     --input <norm.csv> --output <est.csv> --artifact-dir artifacts/cocm --adapter synthetic
python -m tam_builder tier-accounts     --input <est.csv> --output <tier.csv>
python -m tam_builder route-personas    --input <tier.csv> --output <route.csv>
python -m tam_builder generate-briefs   --input <route.csv> --output <briefs.csv>
```

Adapters: `synthetic` (default, no external calls) or `live-public` (public-data adapters only — no PHI, no paid APIs).

### Josh pilot end-to-end

```bash
python scripts/run_josh_pilot_pipeline.py
```

Stages: `ingest → filter → merge → score → enrich → gate → export`. See `_system/agent_workflows/josh-pilot-linkedin-enrichment.md` and `fixtures/josh_drs_group_2026/README.md`.

---

## Setup and local usage

### Prerequisites

- Python 3.11+ (`.venv/` is committed locally, not to git).
- Claude Code CLI or Cursor with Claude Code extension (per upstream requirement).
- Cursor MCP config at `.cursor/mcp.json` for HeyReach (gitignored — see runbook).
- `.env.local` with secrets (gitignored).

### Bootstrap

```bash
git clone <this-repo> KIVIRA.HEALTH
cd KIVIRA.HEALTH
python3 -m venv .venv && source .venv/bin/activate
pip install -e .        # if pyproject is present; otherwise install per-script deps
python scripts/index_graph.py
pytest tests/
```

### Day-zero sanity check

```bash
python scripts/index_graph.py           # should write _system/GRAPH_INDEX.md|.json
pytest tests/ -q                         # contract tests over fixtures
python -m tam_builder normalize-accounts --input fixtures/raw_accounts.csv --output /tmp/out.csv
```

### Commit hygiene (enforced by `CLAUDE.md` HARD RULE #3)

```bash
git add -A && git commit -m "pre-agent: <tool-name> <intent>"
# … agent or operator work …
git add -A && git commit -m "post-agent: <description>"
```

---

## Maintenance and graph hygiene

Source of truth: `_system/CONTEXT_OS_OPERATING_RHYTHM.md` and `.claude/commands/graph-health.md`.

### Weekly

- Refresh `_system/GRAPH_INDEX.md` before the Friday MOC.
- Deposit the three evidence nodes (HeyReach, Linear, InboxKit).
- Wire the MOC hub via uppercase `[[NODE]]` links per `WEEKLY_MOC_GRAPH_RITUAL`.

### Monthly

- Run `/graph-health` → review `_system/GRAPH_HEALTH_REPORT.md`.
- Decide on each aging-emergent node: promote to `validated`, archive, or supersede.
- Consolidate single-use tags toward the load-bearing taxonomy (current targets in the health report).

### Hygiene rules

- **Never delete validated/canonical nodes.** Move to `knowledge_base/_archive/` and set `status: archived`.
- **When in doubt, create.** New node, link to old, mark old `superseded`. Never overwrite history.
- **Tag reuse first.** Use existing tags by frequency (`_system/GRAPH_INDEX.md` Tag Frequency); flag new tags for human review.
- **InboxKit API:** use `POST /v1/api/mailboxes/list` with the workspace header, or `scripts/inboxkit_api_smoke.sh`. **Not** `GET /v1/mailboxes` — that endpoint is broken from our account.

---

## Known gaps and assumptions

Documented honestly so you don't trip on them.

1. **Tag sprawl is in the Warning band (33%)** and has been for 9+ days. A consolidation pass (9 specific edits) drops it to ~18%. Open punch list in `_system/GRAPH_HEALTH_REPORT.md`.
2. **One aging emergent node:** `MEDICAL_SPEND_MODEL_ER_AVOIDANCE` (46 days at last health snapshot). Promote or archive this week.
3. **One broken wiki-link:** `HEAT_2026_05_11` → `[[GRAPH_HEALTH_REPORT]]`. 1-line edit to fix; the indexer correctly excludes `_system/` artifacts.
4. **External `context-os` CLI is referenced but not vendored.** `scripts/index_graph.py` covers the path-map and backlink needs. Heat queries currently rely on `knowledge_base/_index/heat-*.md` snapshots, not a live CLI.
5. **`.claude/skills/` are intentionally thin.** They delegate to `_system/agent_workflows/`. Do not move policy into SKILL.md files.
6. **Operator workflows under `agent_workflows/` are not all wrapped as skills yet** — e.g. HeyReach runbooks, meeting-notes ingest, Wave1 small-batch. They run as operator-followed checklists today.
7. **No HeyReach Python loader.** Deliberate. Loads happen via the HeyReach MCP from a Cursor chat. Rationale documented at the bottom of `_system/agent_workflows/heyreach-mcp-load-runbook.md`.
8. **PHI / payer data:** Never committed. NPPES bulk extracts, large CSVs, `output/`, `artifacts/`, `.env*`, and iMessage extracts are all gitignored. Audit `.gitignore` before adding new data sources.
9. **Repo root holds several historical artifacts** (`01_seed_accounts_by_state.py` through `08_campaign_export_and_handoff.py`, raw Drs Group CSV exports, a `.crdownload` file). These predate the `tam_builder/` package and the Context OS v2 reorg. They are not the source of truth; treat as reference until intentionally archived.
10. **Multi-client replication is documented, not exercised.** The fork pattern in `CONTEXT_OS_OPERATING_RHYTHM.md` is theoretical.

---

## Next improvements (sequenced)

These are *not* a roadmap commitment — they are the visible next steps the system itself surfaces.

1. **Resolve the open punch list in `_system/GRAPH_HEALTH_REPORT.md`** (promote/archive `MEDICAL_SPEND_MODEL_ER_AVOIDANCE`, fix the broken link, run the tag consolidation pass).
2. **Wrap remaining workflows as skills** (heyreach-load, wave1-iteration, aco-attack, meeting-notes-ingest) so Claude Code / Cursor can invoke them by name.
3. **Bake tag-reuse into `/ingest`** so new tags are surfaced as deltas against existing frequency.
4. **Quarantine the legacy `0?_*.py` scripts** at the repo root into `scripts/_legacy/` or delete after confirming `tam_builder/` covers their motion.
5. **Add a CI check** that runs `scripts/index_graph.py` and fails on broken wiki-links + new orphans, so the graph stays clean per commit.
6. **Promote the multi-vault replication pattern** from documentation to a working fork once a second client is real.

---

## Ownership and contribution

- **Founder / GTM lead:** owns Layer 2 (`00_foundation/positioning/`, `messaging/`). Agents do not write here.
- **Cursor:** owns weekly MOCs, signal nodes, copy drafts.
- **Claude Code:** owns ingestion, graph health, execution digests.
- **Codex:** owns `tam_builder/`, `scripts/`, `tests/`. PRs to `main` only; experiments on `experiment/codex-YYYY-MM-DD/` branches.

If an agent produces output that contradicts public legal copy, CDS framing, or an approved weekly MOC: **halt, revert the commit, flag in `#gtm-alerts`, human rewrites.** Per `CLAUDE.md` "Human Override".

Upstream framework changes belong in `gtm-context-os-quickstart/` (tracked as a vendored subtree). Local extensions belong in this repo's own `knowledge_base/`, `00_foundation/`, `_system/agent_workflows/`, `tam_builder/`, and `.claude/`.

---

**Pattern credit:** Context OS by Jacob Dietle — <https://github.com/jacob-dietle/gtm-context-os-quickstart>, <https://taste.systems>.
**This implementation:** Kivira.Health internal. Not open source.
**Last updated:** 2026-05-22 (mirrors `_system/GRAPH_INDEX.md` regeneration).
