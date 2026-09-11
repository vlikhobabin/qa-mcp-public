# Capture Controlled Readonly Fixture Evidence

## Status
4.done

## Execution Order
04

## Priority
P2 - immediate follow-up after fixture planning and before safe UI actions.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-03 interim project status review
- `openspec/board/4.done/03-2026-06-02T12-47-00Z-prepare-edt-meta-protocol-fixtures.md`
- `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_plan.md`
- `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`

## Summary
Turn the controlled read-only fixture plan into live, reviewed protocol
evidence. The current expanded read-only corpus accepts active window and
active form mappings, but `Button`, `Table`, `CommandBar`, `Page`, `Label` and
`CheckBox` remain planned fixture rows with `pending` availability.

This card authored the reviewed source-readiness evidence, ran Windows-native
fixture capture/probe tooling, classified all six planned families, and
published the evidence lineage without accepting unsupported mappings.

## Acceptance
- A controlled read-only fixture source or external EDT workspace boundary is
  documented, validated or explicitly blocked.
- Fixture cases exist for `fixture-button-readonly`,
  `fixture-table-readonly`, `fixture-commandbar-readonly`,
  `fixture-page-readonly`, `fixture-label-readonly` and
  `fixture-checkbox-readonly`.
- Each fixture family records capture id, frame range, request/response sizes,
  normalized hash, dynamic fields, operation token, response markers and
  replay or direct Python-manager status, or an explicit unresolved reason.
- The generated compact evidence links back to the fixture plan and primary
  wire evidence; raw captures remain under ignored `runtime/protocol-research/`.
- No click, checkbox toggle, table edit, command execution, text input or
  persisted business-data mutation is performed.
- Unsupported or blocked fixture families remain visible as `unsupported`,
  `pending`, `partial`, `timeout` or `rejected`, not accepted.
- The evidence index, corpus comparison or accepted-mapping docs are updated
  only for rows that have reviewed evidence.

## Change Set
- `openspec/changes/archive/2026-06-03-prepare-controlled-readonly-fixture-source/`
- `openspec/changes/archive/2026-06-03-run-readonly-fixture-capture-probes/`
- `openspec/changes/archive/2026-06-03-classify-readonly-fixture-evidence/`
- `openspec/changes/archive/2026-06-03-publish-readonly-fixture-mappings/`

## Verify
- `scripts\check.ps1` passed; pytest was not installed, so the pytest step was
  skipped by the script.
- `scripts\check-protocol-lab.ps1` passed for protocol-lab static checks.
- `bin\openspec.cmd validate prepare-controlled-readonly-fixture-source --strict` passed before archive.
- `bin\openspec.cmd validate run-readonly-fixture-capture-probes --strict` passed before archive.
- `bin\openspec.cmd validate classify-readonly-fixture-evidence --strict` passed before archive.
- `bin\openspec.cmd validate publish-readonly-fixture-mappings --strict` passed before archive.
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed after spec sync.
- `bin\openspec.cmd validate --all` passed after all four changes were archived.
- `git diff --check -- openspec\changes openspec\specs openspec\board docs\protocol-research` passed with only Git LF-to-CRLF conversion warnings.

## Archive
- `openspec/changes/archive/2026-06-03-prepare-controlled-readonly-fixture-source/`
- `openspec/changes/archive/2026-06-03-run-readonly-fixture-capture-probes/`
- `openspec/changes/archive/2026-06-03-classify-readonly-fixture-evidence/`
- `openspec/changes/archive/2026-06-03-publish-readonly-fixture-mappings/`

## Related
- `openspec/board/4.done/03-2026-06-02T12-47-00Z-prepare-edt-meta-protocol-fixtures.md`
- `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_plan.md`
- `docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`
- `docs/protocol-research/evidence/fixture-sources/20260603-opsx-do-readonly-fixture-source/source_summary.md`
- `docs/protocol-research/evidence/fixture-sources/20260603-opsx-do-readonly-fixture-source/source_scan.json`
- `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/capture_probe_summary.md`
- `docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/capture_summary.json`
- `docs/protocol-research/evidence/python-manager-probe/fixture-20260603-085618/probe_summary.md`
- `docs/protocol-research/evidence/python-manager-probe/fixture-20260603-085618/python_manager_probe_result.json`
- `docs/protocol-research/evidence/corpus-comparison/fixture-readonly-20260603-085618/classification_summary.md`
- `docs/protocol-research/evidence/corpus-comparison/fixture-readonly-20260603-085618/corpus_comparison.json`
- `docs/protocol-research/evidence/accepted-mappings/fixture-readonly-20260603-085618/accepted_mappings.md`
- `docs/protocol-research/evidence/accepted-mappings/fixture-readonly-20260603-085618/accepted_mappings.json`
- `docs/protocol-research/evidence-index.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/semantic-source-inventory.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/python_manager_probe.py`
- `runtime/protocol-research/captures/20260603-085618/`
- `runtime/protocol-research/python-manager-probe/fixture-20260603-085618/`

## Result
Four ordered OpenSpec changes were implemented, synced into
`qa-mcp-protocol-lab`, verified and archived. The external EDT source scan
found source candidates containing `Button`, `Table`, `CommandBar`, `Page`,
`Label` and `CheckBox`, then the live capture run
`20260603-085618-fixture-readonly` and direct probe
`fixture-20260603-085618` were retained as compact evidence.

All six fixture families remain non-accepted: corpus rows are `pending`, the
analyzer classification is `incomplete_hash`, and accepted mapping output has
no accepted case ids. The unresolved reason is fixture targeting: current
runner/probe tooling can load the manifest but cannot open or select the
source-candidate fixture form, so no fixture request frames, repeated hashes or
operation tokens were captured for those families. No click, checkbox toggle,
table edit, command execution, text input or persisted business-data mutation
was performed.

## Next
- none; fixture targeting remains tracked by the follow-up backlog card

## Change 1: `prepare-controlled-readonly-fixture-source`

### Why
The fixture plan remains pending until the external source or controlled form
that exposes the six element families is validated or explicitly blocked.

### Goal
Document the fixture source boundary and family readiness without committing
generated EDT output, provider payloads or runtime logs.

### Scope
- Compact fixture-source evidence under `docs/protocol-research/evidence/`.
- External EDT/source boundary under ignored `.artifacts/` or another
  documented non-git location.
- Provider/lab gap records for unavailable families.
- No live corpus capture, accepted mapping promotion or action/write behavior.

### Acceptance
- Every planned fixture case has source readiness, unresolved status or blocker.
- Generated source and provider output remain outside reviewed git changes.
- Strict OpenSpec validation passes for the change.

### Depends On
- `openspec/changes/archive/2026-06-03-plan-controlled-readonly-fixtures/`

### Related
- `openspec/changes/archive/2026-06-03-prepare-controlled-readonly-fixture-source/`

## Change 2: `run-readonly-fixture-capture-probes`

### Why
The fixture rows need native wire evidence and direct Python-manager or replay
status before they can be classified.

### Goal
Run Windows-native fixture capture/probe tooling and retain compact evidence
or unresolved reasons for all six planned fixture families.

### Scope
- `protocol_corpus_runner.py` live capture with the planned fixture manifest.
- `python_manager_probe.py` direct read-only probe evidence when supported.
- Compact corpus/probe evidence under `docs/protocol-research/evidence/`.
- Raw captures and runtime output under ignored `runtime/protocol-research/`.
- No clicks, input, checkbox toggles, table edits, command execution or writes.

### Acceptance
- Available families record capture id, frame range, sizes, hash, dynamic
  fields, operation token, response markers and probe/replay status.
- Unavailable families remain visible with explicit status and reason.
- Strict OpenSpec validation passes for the change.

### Depends On
- `prepare-controlled-readonly-fixture-source`

### Related
- `openspec/changes/archive/2026-06-03-run-readonly-fixture-capture-probes/`

## Change 3: `classify-readonly-fixture-evidence`

### Why
Captured fixture output must be classified against the evidence contract before
docs or accepted mappings imply new protocol knowledge.

### Goal
Compare and classify fixture evidence as accepted, partial, pending,
unsupported, timeout, rejected or blocked, preserving unresolved rows.

### Scope
- Compact comparison/classification evidence.
- Optional accepted-mapping output only for rows with stable wire evidence and
  replay/direct-probe support.
- No historical evidence rewrite and no action/write semantics.

### Acceptance
- Every planned family has a classification and evidence path or unresolved
  reason.
- Accepted rows meet the repeated-hash plus replay/probe evidence contract.
- Strict OpenSpec validation passes for the change.

### Depends On
- `run-readonly-fixture-capture-probes`

### Related
- `openspec/changes/archive/2026-06-03-classify-readonly-fixture-evidence/`

## Change 4: `publish-readonly-fixture-mappings`

### Why
Reviewed fixture evidence must be discoverable, but only accepted rows should
change mapping documentation.

### Goal
Publish evidence-index, corpus and accepted-mapping documentation updates that
preserve source/corpus/probe/classification lineage and unresolved statuses.

### Scope
- `docs/protocol-research/evidence-index.md` and related corpus/mapping docs.
- Accepted-mapping docs only for classification-backed rows.
- Unresolved status and owner route for non-accepted families.
- No new live capture during publication.

### Acceptance
- Published docs link compact reviewed evidence, not raw runtime output.
- Accepted fixture mappings link capture ids, frame ranges, hashes, dynamic
  fields, operation tokens, response markers and replay/probe status.
- Strict OpenSpec validation passes for the change.

### Depends On
- `classify-readonly-fixture-evidence`

### Related
- `openspec/changes/archive/2026-06-03-publish-readonly-fixture-mappings/`

## Log
- 2026-06-03T05:30:00Z card created after interim project status review
- 2026-06-03T08:41:25+03:00 `$opsx-ff` created four apply-ready OpenSpec changes and moved card to `2.todo`
- 2026-06-03T09:07:42+03:00 `$opsx-do` implemented, verified, synced and archived four ordered changes; fixture families remain non-accepted pending/incomplete-hash
- 2026-06-03T09:13:17+03:00 `$opsx-pub` documentation pass reused protocol docs, evidence index and synced specs; no README or AGENTS update was needed
- 2026-06-03T09:15:46+03:00 `$opsx-pub` created the scoped publish commit and prepared it for push
