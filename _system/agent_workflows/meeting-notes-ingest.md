# Meeting Notes Ingest Workflow (Gemini / Meet)

**Purpose:** Standardize how we ingest meeting notes into the Context OS so raw evidence is preserved and durable concepts are extracted into `knowledge_base/` without duplicating long content.

---

## Canonical destination (raw ingest)

- Store meeting exports in: `raw-context/kivira-internal/`
- **Default:** keep both the summary/bullets **and** the full transcript (unless exceptionally large).

### Filename convention

Use lower-kebab-case with date suffix:

`<participants-or-topic>-meeting-notes-YYYY-MM-DD.md`

Example:

`jp-km-outbound-strategy-meeting-notes-2026-04-07.md`

---

## Required structure (raw ingest file)

1) Title line (`# ...`)
2) Minimal metadata block:
   - Date
   - Participants (names/handles as recorded; no personal emails)
   - Source (e.g., “Google Meet Notes by Gemini export”)
3) Disclaimer blockquote:
   - Gemini transcripts are computer generated; treat as directional
4) Sections (in order):
   - `## Summary`
   - `## Details`
   - `## Suggested next steps`
   - `## Transcript`
5) Footer:
   - `**Ingested:** YYYY-MM-DD`
   - `**Status:** Raw reference material — atomic concepts extracted to knowledge_base/`

---

## PII redaction rules (required)

- Replace emails with `[REDACTED_EMAIL]`
- Replace phone numbers with `[REDACTED_PHONE]`
- Keep names/roles unless paired with sensitive identifiers.
- If a meeting includes PHI or patient identifiers, stop and move the ingest to a restricted internal location (do not store in this repo).

---

## Minimal atomic extraction (default)

From each meeting, extract **3 durable nodes** into `knowledge_base/`:

1) **Strategy / principle** (what we believe should be true operationally)
2) **Measurement spec** (what we track to validate/kill hypotheses)
3) **Tooling / workflow** (repeatable operational mechanism)

### Node requirements (per `CLAUDE.md`)

- YAML frontmatter must include:
  - `domain`, `node_type`, `status`, `tags`, `source`, `related_concepts`
- `related_concepts`: **≥ 3** wiki-links (prefer linking to existing frameworks first)
- Evidence lines:
  - `[VERIFIED: ...]` for externally checkable claims
  - `[INFERRED: ...]` for synthesized interpretation
  - `[UNVERIFIABLE]` for metrics/pricing/etc. that are volatile or unconfirmed
- Source attribution:
  - `source.type: research-synthesis`
  - `source.file: raw-context/kivira-internal/<raw-ingest-file>.md`

---

## When to split transcript vs keep in one file

- **Keep as one file** if transcript is reasonably sized (default).
- **Split** into two files only if the transcript is huge (e.g., >10k lines) or if you need faster diff/read cycles:
  - `...-meeting-notes-YYYY-MM-DD.md` (summary/details/next steps)
  - `...-transcript-YYYY-MM-DD.md` (transcript only)

---

## Wiring into existing nodes (required)

After creating the atomic nodes:

- Add wiki-links to relevant hubs/frameworks (often):
  - `knowledge_base/methodology/GTM_TIER_ARCHITECTURE_9_SUBTIERS.md`
  - `knowledge_base/methodology/PERSONA_TITLE_DICTIONARY_BY_SUBTIER.md`

Do **not** duplicate long meeting content into frameworks; link out to the extracted nodes.

