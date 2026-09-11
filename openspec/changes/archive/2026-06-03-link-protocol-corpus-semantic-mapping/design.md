## Context

The expanded read-only corpus currently records accepted rows for active
window/form families and explicit fixture gaps for `Button`, `Table`,
`CommandBar`, `Page`, `Label` and `CheckBox`. The evidence contract already
has an optional `semantic_sources` field, but there is no curated artifact
that maps reviewed case ids to demo configuration metadata, platform help
terms or EDT form elements.

This change should build on the semantic-source inventory. It should consume
compact provider evidence and existing corpus rows, then produce a reviewed
semantic map that helps the next capture or fixture pass target specific
forms and element families.

## Goals / Non-Goals

**Goals:**

- Add a compact semantic mapping artifact under
  `docs/protocol-research/evidence/` or a documented adjacent protocol
  research path.
- Link each mapping row to primary corpus or accepted-mapping evidence using
  stable case ids and repository-relative evidence paths.
- Distinguish mapped, partial and unresolved rows so missing GUIDs, names or
  element families are visible.
- Record help/meta/EDT references as supporting context only.

**Non-Goals:**

- Do not regenerate or rewrite historical corpus evidence.
- Do not require EDT mutation, live TestClient execution or Vanessa scenarios.
- Do not infer protocol request hashes, operation tokens or replay status from
  metadata.
- Do not embed full metadata dumps, help pages, screenshots, raw captures or
  local provider logs.

## Decisions

- Use a separate semantic-map artifact rather than mutating all existing
  `corpus_cases.jsonl` rows. Existing evidence stays stable, while future
  corpus rows can link the map or copy compact `semantic_sources` labels when
  regenerated. Alternative: rewrite historical corpus rows. That would blur
  evidence provenance.
- Store mapping status per case id. A row can be `mapped`, `partial`,
  `unresolved` or `not_applicable`, with an explicit reason when not mapped.
  Alternative: omit unknown rows. That would hide the fixture gaps this card is
  meant to clarify.
- Keep provider-specific identifiers summarized. The artifact should include
  stable object names, element family, provider id and compact source reference
  when available, but not raw provider payloads.

## Risks / Trade-offs

- Current captures may expose only captions or transliterated names. Mitigation:
  mark those rows partial and require a later fixture/source pass before using
  them as stable targets.
- Metadata and live form state may disagree. Mitigation: keep wire evidence as
  primary and record mismatches in mapping notes.
- Provider output can be too large or sensitive. Mitigation: keep full output
  in ignored runtime paths and commit only curated summaries.

## Migration Plan

No migration is required for current evidence. Implementation should add the
mapping artifact, link it from `docs/protocol-research/evidence-index.md`, and
optionally reference it from protocol methodology docs. Later corpus generation
can adopt the mapping as optional semantic enrichment.

## Open Questions

- Whether `meta-mcp` exposes stable element GUIDs for all current form
  controls must be discovered during implementation and recorded as mapped or
  unresolved.
