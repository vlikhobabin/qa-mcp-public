# Accept Readonly Corpus Probe Mappings

## Status
4.done

## Priority
P0 - immediate next step before package promotion or safe UI actions.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-02 review after `Expand Readonly Protocol Corpus Matrix`
- `docs/protocol-research/evidence/corpus-comparison/expanded-readonly-20260602-193802-vs-20260602-195407/corpus_comparison.md`
- `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/python_manager_probe_result.json`

## Summary
Close the current read-only corpus acceptance gap by connecting direct Python
manager probe evidence to reviewed corpus rows. The previous matrix proved the
pipeline and stable normalization for active window/form cases, but the
comparison still classifies them as `non_accepted` because direct probe status
is not promoted into corpus acceptance. Element-detail and typed-input rows are
also still `incomplete_hash` in the Vanessa-only path.

The goal is to turn the first supported read-only mappings into accepted,
repeatable dictionary entries without expanding into safe actions or writes.

## Acceptance
- `active-window-context` and `active-form-context` can be classified as
  stable accepted mappings when repeated normalized hashes are stable and
  direct replay/probe evidence is attached.
- `form-element-details` and `typed-input-field-readonly` either get reviewed
  request-frame evidence from the direct Python probe path or retain an
  explicit unresolved reason.
- Corpus rows can reference compact probe evidence and distinguish
  `accepted`, `pending`, `incomplete_hash`, `unsupported`, `partial` and
  `rejected` outcomes consistently.
- Repeatability comparison no longer treats proven direct-probe rows as merely
  pending.
- Accepted mappings retain capture id, frame range, request/response sizes,
  normalized hash, dynamic fields, operation token, response markers and
  replay/probe status.
- Raw capture/probe output remains under ignored `runtime/protocol-research/`;
  compact evidence remains under `docs/protocol-research/evidence/`.

## Change Set
- `openspec/changes/define-corpus-probe-acceptance-contract/`
- `openspec/changes/promote-probe-evidence-in-corpus-comparison/`

## Verify
- `bin\openspec.cmd validate define-corpus-probe-acceptance-contract --strict` passed
- `bin\openspec.cmd validate promote-probe-evidence-in-corpus-comparison --strict` passed
- `bin\openspec.cmd validate --all` passed
- `git diff --check -- openspec\changes\define-corpus-probe-acceptance-contract openspec\changes\promote-probe-evidence-in-corpus-comparison openspec\board` passed with CRLF warnings only
- `scripts\check.ps1` passed; pytest was not installed and was skipped
- `scripts\check-protocol-lab.ps1` passed
- `python -m py_compile tools\protocol-research\compare_corpus_runs.py tools\protocol-research\protocol_corpus_runner.py tests\test_compare_corpus_runs.py tests\test_protocol_corpus_runner.py` passed
- focused probe-promotion Python smoke passed
- probe-attached repeatability comparison passed with `stable: 2`,
  `incomplete_hash: 2`, `unsupported_gap: 6`

## Archive
- `openspec/changes/archive/2026-06-02-define-corpus-probe-acceptance-contract/`
- `openspec/changes/archive/2026-06-02-promote-probe-evidence-in-corpus-comparison/`

## Related
- `openspec/board/4.done/2026-06-02T16-14-18Z-expand-readonly-protocol-corpus-matrix.md`
- `openspec/board/4.done/2026-06-02T13-50-55Z-define-protocol-dictionary-strategy.md`
- `openspec/board/4.done/02-2026-06-02T12-46-00Z-promote-python-testmanager-core.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/compare_corpus_runs.py`
- `docs/protocol-research/evidence/corpus-comparison/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`
- `docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`
- `openspec/changes/archive/2026-06-02-define-corpus-probe-acceptance-contract/`
- `openspec/changes/archive/2026-06-02-promote-probe-evidence-in-corpus-comparison/`

## Result
Implemented and verified direct-probe acceptance for read-only corpus
mappings. The evidence contract now defines compact `probe_evidence` and
accepted-mapping rules. The runner can write probe evidence for future rows,
and the comparison tool can attach compact direct Python-manager evidence when
classifying repeated corpus rows.

The probe-attached comparison promoted `active-window-context` and
`active-form-context` to stable accepted mappings. `form-element-details` and
`typed-input-field-readonly` remain explicit `incomplete_hash` rows because
the Vanessa-only captures still lack reviewed request-frame hashes.

Published by `$opsx-pub` with protocol docs, compact evidence, archived
OpenSpec changes and board ordering in the final commit.

## Next
- completed by `$opsx-do openspec/board/4.done/02-2026-06-02T12-46-00Z-promote-python-testmanager-core.md`

## Change Plan Notes
Likely ordered changes:

1. Extend the corpus evidence model with explicit probe-evidence links and
   accepted direct-probe status rules.
2. Teach the comparison tool to promote repeated stable rows when probe
   evidence confirms the same operation.
3. Add focused tests for accepted, pending, incomplete and unsupported
   classifications.
4. Generate compact evidence for the first accepted read-only mappings and
   update the evidence index.

Verification expectations:

- `scripts\check.ps1`
- `scripts\check-protocol-lab.ps1`
- focused tests for corpus comparison and probe-status classification
- repeatability comparison over `20260602-193802` and `20260602-195407`
- at least one direct Python-manager probe evidence link in accepted rows
- `bin\openspec.cmd validate --all`
- `git diff --check`

## Change 1: `define-corpus-probe-acceptance-contract`

### Why
Stable normalized hashes are not enough to promote a mapping unless replay or
direct Python-manager proof is attached in a reviewed, reproducible way.

### Goal
Define the corpus row fields and acceptance rules for direct-probe evidence,
including explicit unresolved states for incomplete request-frame evidence.

### Scope
- Protocol evidence contract docs.
- Protocol corpus runner docs.
- `qa-mcp-protocol-lab` requirements for direct-probe links and accepted
  read-only mapping criteria.
- No tooling implementation.

### Acceptance
- Corpus rows can link compact direct-probe evidence without embedding raw
  probe output.
- Accepted read-only mappings require stable repeated normalized hashes plus
  accepted replay/probe evidence for the same operation.
- Direct-probe gaps remain visible as non-accepted states with unresolved
  reasons.

### Depends On
- none

### Related
- `openspec/changes/define-corpus-probe-acceptance-contract/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Change 2: `promote-probe-evidence-in-corpus-comparison`

### Why
The comparison tooling currently keeps stable active-window/form rows as
`non_accepted` when direct-probe confirmation is not represented in the row
status.

### Goal
Teach corpus/comparison tooling to consume compact probe evidence, promote
stable confirmed read-only rows, and preserve explicit unresolved rows.

### Scope
- Probe evidence ingestion or mapping in corpus/comparison tooling.
- Status promotion rules for accepted, pending, incomplete, unsupported and
  ambiguous rows.
- Focused tests and compact accepted-mapping/comparison evidence.
- No safe UI actions, writes, EDT dependency or package promotion.

### Acceptance
- Repeated stable rows with accepted probe/replay evidence are reported as
  stable accepted mappings.
- Rows without non-null request hashes or unambiguous probe joins remain
  non-accepted with reasons.
- Evidence output records accepted case ids, source captures, normalized
  hashes, probe evidence paths and unresolved rows.

### Depends On
- `define-corpus-probe-acceptance-contract`

### Related
- `openspec/changes/promote-probe-evidence-in-corpus-comparison/`

### Notes For `$openspec-ff-change`
- Artifacts are already prepared.

## Log
- 2026-06-02T18:01:06Z card created after reviewing the expanded read-only corpus result
- 2026-06-02T18:15:53Z decomposed into two OpenSpec changes and prepared artifacts
- 2026-06-02T18:45:02Z implemented, verified, synced specs and archived both changes
- 2026-06-02T22:37:10+03:00 published with docs, evidence, board ordering and archived changes
- 2026-06-03T06:45:37+03:00 downstream Python TestManager core card completed
