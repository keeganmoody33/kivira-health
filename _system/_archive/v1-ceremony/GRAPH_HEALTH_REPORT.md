# Context OS Health Report

**Generated:** 2026-05-01
**Scope:** `/Users/keeganmoody/KIVIRA.HEALTH/knowledge_base` (excludes `gtm-context-os-quickstart/` upstream clone)
**Prior report:** 2026-04-08

---

## Summary

**Overall Health:** **Warning**

Structurally clean — no orphans, no broken links, no hubs. But tag sprawl is unchanged at 38.5%, three nodes still carry a `draft` status that isn't in the blessed `status_values`, and 21 of 22 emergent nodes are 25–28 days old. Within ~1 week the entire emergent cohort will cross the 30-day aging threshold and trigger a lifecycle warning unless validated, archived, or refreshed.

No new content has landed in `knowledge_base/` since the last health check; this is a maintenance-debt report, not a growth report.

---

## Inventory

**Total Nodes:** 56

**By Domain:**

| Domain | Count |
| -------- | ------: |
| business | 24 |
| methodology | 23 |
| technical | 9 |

**By Status:**

| Status | Count |
| -------- | ------: |
| validated | 31 |
| emergent | 22 |
| draft | 3 |

**By Node Type:**

| Type | Count |
| ------ | ------: |
| framework | 31 |
| concept | 14 |
| pattern | 8 |
| case-study | 1 |
| principle | 1 |
| workflow | 1 |

> `principle` and `workflow` are not in the blessed `node_types` list (`concept`, `pattern`, `case-study`, `framework`). Decide whether to bless them or remap.

---

## Tag Health

- **Unique tags in use:** 39
- **Single-use tags:** 15
- **Tag sprawl (single-use / unique):** **38.5%** — **Warning** (healthy <20%, warning 20–40%)

Sprawl is essentially unchanged from the 2026-04-08 report (38.46%). No new ad-hoc tags have been introduced, but no consolidation has happened either.

### Tags not in `taxonomy.yaml` (7)

The previous report listed 4. Three additional unblessed tags surfaced this run because they're domain names being reused as topic tags:

| Unblessed tag | Used in (count) | Issue |
| --- | ---: | --- |
| `business` | 24 | Domain-as-tag — duplicates folder/frontmatter `domain` |
| `methodology` | 23 | Domain-as-tag — duplicates folder/frontmatter `domain` |
| `technical` | 9 | Domain-as-tag — duplicates folder/frontmatter `domain` |
| `outbound` | 3 | Operational tag candidate — bless or merge into `gtm-motion` |
| `data-enrichment` | 1 | Single-use; merge into `tooling` or `gtm-motion` |
| `metrics` | 1 | Single-use; bless or merge into `execution-cadence` |
| `tooling` | 1 | Single-use; bless if multiple "stack" nodes are coming, otherwise merge |

### Single-use tags (15 — consolidation candidates)

`account-schema`, `data-enrichment`, `discovery-calls`, `ehr-integration`, `fee-for-service-ffs`, `funding-signals`, `hcc-hierarchical-condition-categories`, `metrics`, `risk-adjustment-raf`, `safety-risk-notification`, `smart-on-fhir`, `third-party-press`, `tier-architecture`, `tooling`, `v28-model-cms`

Most of these *are* in `taxonomy.yaml` — they're blessed but only attached to one node each. The fix is usage discipline (apply them where relevant), not deletion.

---

## Link Health

- **Orphan nodes (< 3 links):** None
- **Hub nodes (> 10 links):** None
- **Broken links:** None

Healthy. Every node satisfies the `minimum_links: 3` requirement from `ontology.yaml`.

---

## Lifecycle Health

- **Aging emergent nodes (> 30 days):** **0** today
- **Approaching aging threshold (25–30 days):** **21 of 22 emergent nodes**

Today no node breaches the 30-day rule, but the cohort is bunched at the cliff:

| Age (days) | Count | Will breach on |
| ---: | ---: | --- |
| 28 | 7 | 2026-05-03 |
| 26 | 12 | 2026-05-05 |
| 25 | 2 | 2026-05-06 |

**Action window:** by **2026-05-08** the entire emergent cohort will be aging. Either run a validation pass this week or accept that the next health check will flip lifecycle to Warning.

### Status drift: `draft` is not blessed

Three nodes use `status: draft`, which is not in `status_values.blessed` (`emergent`, `validated`, `canonical`). This was flagged in the prior report and has not been resolved:

- `DEMO_FIRST_OUTBOUND_STRATEGY` (methodology)
- `OUTREACH_BASELINE_METRICS` (methodology)
- `LIST_BUILDING_STACK_CLAY_ENRICHMENT` (technical)

All three also have empty `last_updated` fields, so their lifecycle age cannot be measured.

---

## Recommendations

1. **Validate or archive the emergent cohort this week.** 21 nodes will cross the 30-day aging threshold by 2026-05-08. Sweep through, promote ready ones to `validated`, and refresh `last_updated` on the rest with a short note on what's still pending.
2. **Resolve the `draft` status drift.** Either add `draft` to `status_values.blessed` in `taxonomy.yaml` (and document its meaning in `ontology.yaml`) or convert the three drafts to `emergent` and stamp `last_updated`. Same one-line fix for `principle` and `workflow` in `node_types`.
3. **Stop using domain names as tags.** Strip `business`, `methodology`, `technical` from frontmatter `tags:` lists — the domain is already encoded via folder + `domain:` field. This single sweep drops unblessed tag count from 7 to 4 and removes the largest source of redundant noise.
4. **Decide on the four operational tags** (`outbound`, `tooling`, `metrics`, `data-enrichment`). Either bless them in `taxonomy.yaml` under `methodology`/`technical`, or merge into existing blessed tags. Don't leave them unblessed for a third health check.

---

## Diff vs 2026-04-08

| Metric | 2026-04-08 | 2026-05-01 | Δ |
| --- | ---: | ---: | --- |
| Total nodes | 56 | 56 | 0 |
| Tag sprawl % | 38.46 | 38.5 | ~0 |
| Unblessed tags | 4 | 7 | +3 (domain-as-tag, previously missed) |
| Aging emergent | 0 | 0 | 0 (but 21 within 5 days of breach) |
| Draft-status nodes | 3 | 3 | 0 (unresolved) |

No new nodes, no consolidation, no validation moves — the graph has been static for ~3 weeks. The report itself is the only thing that has changed.

---

## Weekly Operating Rhythm

See [`CONTEXT_OS_OPERATING_RHYTHM.md`](CONTEXT_OS_OPERATING_RHYTHM.md).
