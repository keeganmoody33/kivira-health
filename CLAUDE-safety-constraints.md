# CLAUDE.md — Agent Safety Constraints (v2 Amendment)

**Append to existing `CLAUDE.md` in Kivira repo root.**

---

## AGENT CONSTRAINTS (Hard Rules — All Tools)

1. **NEVER modify files in `00_foundation/positioning/` or `00_foundation/messaging/` without explicit human approval.** These are Layer 2 strategic docs. Agents compose from them; they do not rewrite them.

2. **NEVER delete nodes with `status: validated` or `status: canonical`.** Archive by moving to `knowledge_base/_archive/` and updating frontmatter to `status: archived`.

3. **ALWAYS commit before and after agent sessions.**
   ```bash
   git add -A && git commit -m "pre-agent: [tool-name] session"
   # ... agent work ...
   git add -A && git commit -m "post-agent: [description]"
   ```

4. **NEVER write to branches other than `main` without explicit instruction.** Codex experiments use `experiment/codex-YYYY-MM-DD/` branches.

5. **When in doubt, create — do not overwrite.**
   - New insight → new node with `status: emergent`
   - Updated insight → new node + link to old node + mark old as `status: superseded`
   - Never edit a validated node's body to contradict its original evidence.

6. **Weekly MOC is read-only composition.** The agent creates `00_foundation/weekly_updates/YYYY-MM-DD.md` by **linking** to existing nodes. It does not invent signal data in the weekly.

7. **Evidence discipline enforced.**
   - Every claim in a weekly MOC must link to a node with `source:` frontmatter.
   - If no source node exists, the claim is flagged `[UNVERIFIABLE]` and the human decides.

8. **No taxonomy.yaml obedience.** Agents do not read `_system/knowledge_graph/taxonomy.yaml` or `ontology.yaml`. These are v1 artifacts. Agents use graph heat, inbound links, and co-access to navigate.

---

## TOOL-SPECIFIC SCOPES

### Cursor (Primary GTM Agent)
- **Can:** Create signal nodes, generate weekly MOCs, run graph queries, draft copy variants.
- **Cannot:** Edit positioning v1, delete validated personas, modify TAM tier files.

### Claude Code (Secondary / Infrastructure)
- **Can:** Ingest meeting notes, run `context-os` CLI, build execution nodes, audit graph health.
- **Cannot:** Generate weekly MOCs (Cursor owns template), edit HeyReach copy without human review.

### Codex (Experimental / Python)
- **Can:** Build scripts, run TAM builder, generate CSV fixtures, test automation.
- **Cannot:** Write to `main` branch directly. All code goes through PR review.

---

## HUMAN OVERRIDE

If any agent produces output that contradicts:
- Public legal copy (`raw-context/kivira-public/legal-*`)
- Clinical/regulatory framing (`CDS_NOT_DIAGNOSIS_FRAMING`)
- Investor-facing claims in approved weekly MOCs

**Immediate halt.** Revert commit. Flag in `#gtm-alerts` Slack channel. Human rewrites.

---

**Amended:** 2026-05-04  
**Applies to:** All AI agents operating on Kivira Context-OS
