# Context OS operating rhythm (Kivira)

**Purpose:** Lightweight schedule so the graph compounds (aligned with plan Phase 7).

## Weekly (30–45 min)

- Ingest **1–3** new artifacts (call notes, emails, deck snippets) into `raw-context/` then split into `knowledge_base/` nodes using the quickstart **`/ingest`** command or manual node template.
- Update `last_updated` on any node affected by new evidence.

## Monthly (20 min)

- Open [`GRAPH_HEALTH_REPORT.md`](GRAPH_HEALTH_REPORT.md) and refresh metrics (node counts, tag sprawl, broken links).
- Prune or merge tags if sprawl exceeds **40%** single-use.

## After marketing/legal site changes

- Re-run **Firecrawl `map`** on `https://www.kivira.health` and diff against `raw-context/kivira-public/_URL_MANIFEST.md`.
- Re-archive `www-home.md`, `legal-*.md`, and `instrument-overview.md` as needed.

## Before campaigns or major outbound pushes

- Run **`context-gap-analysis`** skill from `gtm-context-os-quickstart/.claude/skills/` (or read `SKILL.md` and execute checklist).
- Re-read **`epistemic-context-grounding`** before changing hero claims or competitive positioning.
