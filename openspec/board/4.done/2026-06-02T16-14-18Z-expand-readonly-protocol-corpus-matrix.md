# Expand Readonly Protocol Corpus Matrix

## Status
4.done

## Priority
P0 - next protocol research implementation track after the first corpus runner.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-02 follow-up after `Build Protocol Corpus Runner`
- `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`

## Summary
Expand the read-only protocol corpus from the first active-window/form/element
smoke cases into a broader, repeated and normalized dictionary for common 1C
testing API read operations. The work should prioritize more element types,
repeatability across captures and stronger automatic dynamic-field detection.

This card covers the next three research steps:

1. Expand the read-only dictionary by form element type.
2. Compare repeated captures for the same case.
3. Improve the normalizer for newly discovered dynamic ranges.

## Acceptance
- The corpus matrix covers additional read-only element families such as
  `Button`, `Table`, `CommandBar`, `Page`, `Label`, `CheckBox` and typed input
  fields where the current test form exposes them.
- Each new case produces reviewed rows with `case_id`, `api_call`,
  `ui_target`, `frame_range`, `normalized_hash`, dynamic fields,
  `operation_token`, `response_markers` and `replay_status`.
- At least two fresh captures are compared for the same case set.
- Repeated cases classify stable hashes separately from newly discovered
  dynamic fields.
- Normalizer changes are backed by compact evidence that shows replacement
  ranges, before/after hash behavior and residual ambiguity.
- Raw capture streams remain under `runtime/protocol-research/`; compact
  evidence remains under `docs/protocol-research/evidence/`.

## Change Set
- `openspec/changes/expand-readonly-corpus-case-matrix/`
- `openspec/changes/add-corpus-repeatability-comparison/`
- `openspec/changes/improve-corpus-dynamic-normalizer/`

## Verify
- `bin\openspec.cmd validate expand-readonly-corpus-case-matrix --strict` passed
- `bin\openspec.cmd validate add-corpus-repeatability-comparison --strict` passed
- `bin\openspec.cmd validate improve-corpus-dynamic-normalizer --strict` passed
- `scripts\check.ps1` passed; pytest was not installed and was skipped
- `scripts\check-protocol-lab.ps1` passed
- two fresh Windows Vanessa attach-running captures passed:
  `20260602-193802` and `20260602-195407`
- direct Python-manager probe passed for supported `EditField`/typed input
  family: `expanded-20260602-193802`
- repeatability comparison passed:
  `expanded-readonly-20260602-193802-vs-20260602-195407`
- normalizer evidence generated with before/after hash sets and preserved
  `operation_token`
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed
- `bin\openspec.cmd validate --all` passed after archive
- `git diff --check` passed with only CRLF warnings

## Archive
- `openspec/changes/archive/2026-06-02-expand-readonly-corpus-case-matrix/`
- `openspec/changes/archive/2026-06-02-add-corpus-repeatability-comparison/`
- `openspec/changes/archive/2026-06-02-improve-corpus-dynamic-normalizer/`

## Related
- `openspec/board/4.done/2026-06-02T12-45-00Z-build-protocol-corpus-runner.md`
- `openspec/board/4.done/2026-06-02T13-50-55Z-define-protocol-dictionary-strategy.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`
- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/analyze_request_series.py`
- `openspec/changes/expand-readonly-corpus-case-matrix/`
- `openspec/changes/add-corpus-repeatability-comparison/`
- `openspec/changes/improve-corpus-dynamic-normalizer/`

## Result
Implemented and verified the expanded read-only corpus matrix. The runner now
emits family labels, availability statuses, expected markers, explicit
unsupported fixture gaps and normalizer before/after hash metadata.

Added repeatability comparison over reviewed `corpus_cases.jsonl` inputs and
normalizer evidence output. Two fresh Vanessa captures showed stable
active-window/form normalized hashes but kept rows non-accepted without direct
probe status; element-detail frames remained explicit incomplete hashes in the
Vanessa-only path. Direct Python-manager probing confirmed the supported
`EditField`/typed input family without a 1C TestManager instance.

Published via scoped OPSX commit `feat(protocol): expand readonly corpus
matrix`; final commit hash is recorded by git after the card-sync amend.

## Next
- none

## Change Plan Notes
Proposed ordered changes:

1. Add a read-only case manifest for additional element families and expected
   response markers.
2. Extend the corpus runner or companion analyzer to compare repeated captures
   and report stable versus dynamic byte ranges.
3. Improve normalizer rules for newly discovered GUIDs, counters, nonces,
   object references and operation-token echoes.
4. Retain compact evidence for each accepted mapping and update
   `docs/protocol-research/evidence-index.md`.

Verification expectations:

- `scripts\check.ps1`
- `scripts\check-protocol-lab.ps1`
- at least two short Vanessa attach-running captures for the expanded matrix
- at least one direct Python-manager probe for a supported new case family
- `bin\openspec.cmd validate --all`
- `git diff --check`

## Change 1: `expand-readonly-corpus-case-matrix`

### Why
The current corpus proves only the first active-window, active-form and
form-element detail smoke cases. The protocol dictionary needs a wider
read-only element-family matrix before action/write cases are attempted.

### Goal
Define and implement an expanded read-only corpus matrix for common 1C form
element families with explicit support and gap reporting.

### Scope
- Corpus case manifest and seeded read-only case definitions.
- Runner or companion manifest behavior for family labels and expected
  response markers.
- Compact reviewed evidence for supported families.
- No safe-action, click, input or write semantics.

### Acceptance
- Supported element families generate reviewed corpus rows.
- Unavailable families are marked `unsupported` or `pending` with a reason.
- The matrix remains read-only and keeps raw captures under `runtime/`.

### Depends On
- none

### Related
- `openspec/changes/expand-readonly-corpus-case-matrix/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 2: `add-corpus-repeatability-comparison`

### Why
A single capture cannot prove that a normalized request shape is stable. The
same case set must be compared across repeated captures before mappings become
stable dictionary entries.

### Goal
Add repeated-capture comparison for reviewed corpus rows, including stable
hashes, divergent hashes, missing cases and suspected dynamic fields.

### Scope
- Corpus comparison tool or runner companion behavior.
- Compact repeatability reports under `docs/protocol-research/evidence/`.
- At least two short captures for the same expanded case set during delivery.
- No broad raw-payload commits.

### Acceptance
- Comparison groups rows by `case_id` across capture ids.
- Stable and divergent values are reported separately.
- Missing cases and non-accepted replay statuses remain visible.

### Depends On
- `expand-readonly-corpus-case-matrix`

### Related
- `openspec/changes/add-corpus-repeatability-comparison/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 3: `improve-corpus-dynamic-normalizer`

### Why
Expanded repeated captures will expose dynamic fields beyond the initial ACK
GUID, sequence, nonce and operation-token ranges. New replacements must be
evidence-backed so normalization does not hide semantic protocol bytes.

### Goal
Improve dynamic-field detection and normalizer reporting with before/after
hash evidence and ambiguity handling.

### Scope
- Normalizer logic under `tools/protocol-research/`.
- Focused tests for replacement behavior.
- Compact normalizer evidence under `docs/protocol-research/evidence/`.
- No normalization of whole request bodies without proof.

### Acceptance
- New dynamic ranges include source class, locator, length, replacement label
  and observed values.
- Before/after hash behavior is retained in compact evidence.
- Ambiguous ranges remain visible and do not promote stable accepted mappings.

### Depends On
- `add-corpus-repeatability-comparison`

### Related
- `openspec/changes/improve-corpus-dynamic-normalizer/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Log
- 2026-06-02T16:14:18Z card created after publishing the first corpus runner
- 2026-06-02T16:20:00Z decomposed into three OpenSpec changes and prepared artifacts
- 2026-06-02T16:40:26Z generated fresh expanded Vanessa corpus evidence from capture `20260602-193802`
- 2026-06-02T16:43:12Z confirmed supported `EditField`/typed input family with direct Python-manager probe
- 2026-06-02T16:55:41Z generated second fresh expanded Vanessa corpus evidence from capture `20260602-195407`
- 2026-06-02T17:04:20Z generated repeatability and normalizer evidence for the two fresh captures
- 2026-06-02T17:10:00Z archived all three OpenSpec changes and validated workspace
- 2026-06-02T20:22:22+03:00 published scoped OPSX commit and prepared push to origin
