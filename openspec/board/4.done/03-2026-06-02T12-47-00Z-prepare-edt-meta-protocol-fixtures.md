# Prepare EDT And Meta Protocol Fixtures

## Status
4.done

## Priority
P2 - support richer read-only fixture coverage and semantic mapping after the
core accepted mappings are stable.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-02 qa-mcp infrastructure discussion
- 2026-06-02 protocol dictionary strategy discussion
- 2026-06-02 expanded read-only corpus result review

## Summary
Prepare optional EDT/meta tooling for protocol research: an EDT workspace or
metadata snapshot for the demo configuration, plus mapping from forms/elements
to protocol evidence. This track should support corpus interpretation, but raw
protocol capture and replay must remain independent from EDT/meta services.
It should also unblock richer read-only fixture coverage for element families
that are currently explicit gaps in the corpus matrix.

## Acceptance
- The required EDT workspace/snapshot location is documented and kept outside
  git runtime data.
- `meta-mcp` can be used to inspect form and element metadata relevant to the
  current captures.
- `edt-mcp` usage is limited to controlled fixture authoring and validation.
- `help-mcp` platform help entities for the tested object model are recorded
  where they inform corpus case selection.
- Metadata mapping is linked to evidence rows without becoming required for TCP
  capture, normalization or replay.
- The fixture plan identifies or authors controlled coverage for `Button`,
  `Table`, `CommandBar`, `Page`, `Label` and `CheckBox`, or records why a
  family remains out of scope.
- Any generated EDT workspace, infobase export or raw fixture output remains
  outside git unless it is a small curated evidence artifact.

## Change Set
- `openspec/changes/archive/2026-06-03-document-edt-meta-semantic-sources/`
- `openspec/changes/archive/2026-06-03-link-protocol-corpus-semantic-mapping/`
- `openspec/changes/archive/2026-06-03-plan-controlled-readonly-fixtures/`

## Verify
- `$opsx-ff` strict validation passed for all planned changes.
- `scripts\check.ps1` passed; `pytest` is not installed and was skipped.
- `fixture_case_manifest.json` parsed as 6 pending read-only fixture cases.
- `bin\openspec.cmd validate document-edt-meta-semantic-sources --strict` passed.
- `bin\openspec.cmd validate link-protocol-corpus-semantic-mapping --strict` passed.
- `bin\openspec.cmd validate plan-controlled-readonly-fixtures --strict` passed.
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed.
- `bin\openspec.cmd validate --all` passed after archive.
- `git diff --check` passed; Git reported LF-to-CRLF warnings only.

## Archive
- `openspec/changes/archive/2026-06-03-document-edt-meta-semantic-sources/`
- `openspec/changes/archive/2026-06-03-link-protocol-corpus-semantic-mapping/`
- `openspec/changes/archive/2026-06-03-plan-controlled-readonly-fixtures/`

## Related
- `openspec/board/4.done/2026-06-02T13-50-55Z-define-protocol-dictionary-strategy.md`
- `openspec/board/4.done/2026-06-02T12-45-00Z-build-protocol-corpus-runner.md`
- `openspec/board/4.done/2026-06-02T16-14-18Z-expand-readonly-protocol-corpus-matrix.md`
- `openspec/board/4.done/01-2026-06-02T18-01-06Z-accept-readonly-corpus-probe-mappings.md`
- `openspec/board/4.done/02-2026-06-02T12-46-00Z-promote-python-testmanager-core.md`
- `docs/protocol-research/methodology.md`
- `docs/protocol-research/evidence/infrastructure-checks/20260602-161326/infra_check.md`
- `.mcp.json`
- `openspec/changes/archive/2026-06-03-document-edt-meta-semantic-sources/`
- `openspec/changes/archive/2026-06-03-link-protocol-corpus-semantic-mapping/`
- `openspec/changes/archive/2026-06-03-plan-controlled-readonly-fixtures/`
- `docs/protocol-research/semantic-source-inventory.md`
- `docs/protocol-research/evidence/semantic-sources/20260603-opsx-do-semantic-sources/source_readiness.md`
- `docs/protocol-research/evidence/semantic-mapping/20260603-opsx-do-semantic-mapping/semantic_map.md`
- `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_plan.md`
- `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`

## Result
Completed all three ordered changes. The delivery documents approved
help/meta/EDT semantic source boundaries, links current corpus rows to compact
semantic mapping evidence, and adds a controlled read-only fixture plan plus
pending manifest rows for `Button`, `Table`, `CommandBar`, `Page`, `Label` and
`CheckBox`. Published through a scoped `$opsx-pub` commit for this card.

## Next
- none for this card; future live fixture authoring and capture should use a new card

## Change 1: `document-edt-meta-semantic-sources`

### Why
The lab needs an explicit inventory of approved help/meta/EDT semantic sources
before those sources are used to label protocol corpus rows.

### Goal
Document provider owners, source builds or versions, external workspace and
snapshot boundaries, allowed uses and compact readiness or gap evidence.

### Scope
- Protocol research docs and compact evidence index links.
- Optional readiness/gap evidence for `help-mcp`, `meta-mcp` and `edt-mcp`.
- No change to raw capture, normalization, replay or Python-manager probing.

### Acceptance
- `docs/protocol-research/semantic-source-inventory.md` exists and names the
  approved source boundaries.
- Raw provider output, EDT workspaces and infobase exports remain outside git.
- Strict OpenSpec validation passes for the change.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-06-03-document-edt-meta-semantic-sources/`

### Notes For `$openspec-ff-change`
- Already apply-ready; preserve the 1C verification matrix in `tasks.md`.

## Change 2: `link-protocol-corpus-semantic-mapping`

### Why
Existing corpus evidence exposes read-only fixture gaps, but those gaps are
not yet mapped to demo configuration metadata, form elements or help topics.

### Goal
Create a compact semantic mapping artifact that links corpus case ids to
help/meta/EDT references while preserving primary wire evidence as the source
of protocol truth.

### Scope
- Compact semantic mapping evidence under `docs/protocol-research/evidence/`.
- Evidence index and methodology links.
- No historical corpus row rewrite unless a future implementation explicitly
  regenerates evidence under a new run id.

### Acceptance
- Mapping rows identify `case_id`, semantic target, provider source, mapping
  status, primary evidence path and unresolved reason when applicable.
- Unmapped or partial rows remain visible.
- Strict OpenSpec validation passes for the change.

### Depends On
- `document-edt-meta-semantic-sources`

### Related
- `openspec/changes/archive/2026-06-03-link-protocol-corpus-semantic-mapping/`

### Notes For `$openspec-ff-change`
- Already apply-ready; use sanitized provider summaries only.

## Change 3: `plan-controlled-readonly-fixtures`

### Why
`Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox` remain explicit
read-only fixture gaps and need a controlled coverage plan before acceptance.

### Goal
Define or author controlled read-only fixture coverage with case ids, expected
markers, safety class, provider owners and retained evidence paths.

### Scope
- Fixture coverage plan and optional corpus manifest or seeded matrix updates.
- Optional EDT validation and live corpus/probe evidence during delivery.
- No click, input, command execution, write/action semantics or raw output in
  git.

### Acceptance
- Each missing family is covered, blocked or out of scope with owner route and
  residual risk.
- Fixture-derived corpus cases remain explicit, read-only and evidence-backed.
- Strict OpenSpec validation passes for the change.

### Depends On
- `document-edt-meta-semantic-sources`
- `link-protocol-corpus-semantic-mapping`

### Related
- `openspec/changes/archive/2026-06-03-plan-controlled-readonly-fixtures/`

### Notes For `$openspec-ff-change`
- Already apply-ready; implementation may stop on provider gaps instead of
  inventing fixture paths.

## Log
- 2026-06-02T12:47:00Z card created
- 2026-06-02T13:50:55Z reprioritized as P2 support track for corpus semantics
- 2026-06-02T18:01:06Z ordered after package-core promotion and expanded to cover read-only fixture gaps
- 2026-06-03T06:45:37+03:00 unblocked by completed Python TestManager core promotion
- 2026-06-03T07:11:42+03:00 `$opsx-ff` created three apply-ready OpenSpec changes and moved card to `2.todo`
- 2026-06-03T07:41:37+03:00 `$opsx-do` implemented, verified, synced and archived all three changes; card moved to `4.done`
- 2026-06-03T07:51:00+03:00 `$opsx-pub` documentation pass reused protocol docs, evidence index and synced specs; no README or AGENTS update was needed
- 2026-06-03T07:52:58+03:00 `$opsx-pub` created the scoped publish commit and prepared it for push
