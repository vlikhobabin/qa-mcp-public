# Resolve Readonly Element Hash Gaps

## Status
4.done

## Execution Order
05

## Priority
P2 - close known read-only evidence gaps before broadening action coverage.

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- 2026-06-03 interim project status review
- `openspec/board/4.done/01-2026-06-02T18-01-06Z-accept-readonly-corpus-probe-mappings.md`
- `openspec/board/4.done/02-2026-06-02T12-46-00Z-promote-python-testmanager-core.md`
- `docs/protocol-research/python-protocol-package.md`

## Summary
Resolved the current `incomplete_hash` decision point for useful read-only
element probe paths by auditing existing evidence, extracting reviewed request
hash evidence where available, refining unresolved classification reasons and
publishing the final outcome.

The final outcome is unresolved for both target rows. No descriptor was
promoted to accepted, and no safe-action, click, input, write or business-data
mutation behavior was introduced.

## Acceptance
- Current `form-element-details` and `typed-input-field-readonly` evidence was
  audited against the corpus evidence contract.
- Reviewed request-frame hash evidence was extracted from existing compact
  evidence for the element request shape.
- Any remaining non-accepted row now has precise unresolved reasons and next
  blockers.
- `qa_mcp.protocol` descriptors continue to expose `incomplete_hash` for both
  target rows.
- Raw probe/capture output remains under ignored runtime paths; compact
  reviewed evidence remains under `docs/protocol-research/evidence/`.
- No safe-action, click, input, write or business-data mutation behavior was
  introduced by this card.

## Change Set
- `openspec/changes/archive/2026-06-03-audit-readonly-element-hash-evidence/`
- `openspec/changes/archive/2026-06-03-capture-readonly-element-request-hashes/`
- `openspec/changes/archive/2026-06-03-refine-readonly-element-gap-classification/`
- `openspec/changes/archive/2026-06-03-publish-readonly-element-hash-resolution/`

## Verify
- `scripts\check.ps1` passed; `pytest` is not installed and was skipped by the script.
- `scripts\check-protocol-lab.ps1` passed static checks; no manager or TestClient was started.
- Focused `compare_corpus_runs` test functions passed through the direct Python harness.
- Focused protocol contract and resolution smoke tests passed through the direct Python harness.
- `ConvertFrom-Json` parsed the generated request-hash and resolution JSON evidence.
- `bin\openspec.cmd validate <change> --strict` passed for all four changes.
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict` passed after spec sync.
- `bin\openspec.cmd validate --all` passed after each archive; final state has no active changes.
- `git diff --check` passed with line-ending warnings only.

## Archive
- `openspec/changes/archive/2026-06-03-audit-readonly-element-hash-evidence/`
- `openspec/changes/archive/2026-06-03-capture-readonly-element-request-hashes/`
- `openspec/changes/archive/2026-06-03-refine-readonly-element-gap-classification/`
- `openspec/changes/archive/2026-06-03-publish-readonly-element-hash-resolution/`

## Related
- Publish commit message: `feat(protocol): resolve readonly element hash gaps`
- `docs/protocol-research/evidence/readonly-element-hash-audit/current-element-hash-gaps/audit_summary.md`
- `docs/protocol-research/evidence/readonly-element-request-hashes/20260602-172319-expanded-extracted/request_hashes.json`
- `docs/protocol-research/evidence/corpus-comparison/readonly-element-hash-resolution-20260603-extracted/classification_summary.md`
- `docs/protocol-research/evidence/readonly-element-hash-resolution/20260603-incomplete-hash-with-extracted-request-evidence/resolution.json`
- `docs/protocol-research/evidence-index.md`
- `docs/protocol-research/python-protocol-package.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `src/qa_mcp/protocol/`
- `tools/protocol-research/compare_corpus_runs.py`
- `tests/test_compare_corpus_runs.py`
- `tests/test_protocol_contract.py`

## Result
All four OpenSpec changes were implemented, verified, synced to
`openspec/specs/qa-mcp-protocol-lab/spec.md` and archived.

The card was published by `$opsx-pub` with scoped protocol evidence,
documentation, tests, spec and archive changes. Runtime manifest, trace and
raw capture paths were excluded from the commit.

`form-element-details` remains `incomplete_hash` with
`accepted_reviewed_hash` and `missing_request_frames`.

`typed-input-field-readonly` remains `incomplete_hash` with
`accepted_reviewed_hash`, `ambiguous_operation_join` and
`missing_request_frames`.

Safe-action protocol capture remains blocked from promotion by the read-only
element boundary; this card intentionally did not add action, input or write
coverage.

## Next
- none

## Change Plan Notes
The card was delivered through four ordered OpenSpec changes:

1. `audit-readonly-element-hash-evidence`
2. `capture-readonly-element-request-hashes`
3. `refine-readonly-element-gap-classification`
4. `publish-readonly-element-hash-resolution`

## Log
- 2026-06-03T05:31:00Z card created after interim project status review
- 2026-06-03T09:43:52+03:00 decomposed into four OpenSpec changes and prepared artifacts
- 2026-06-03T09:53:01+03:00 validated all four changes and synced card for `$opsx-do`
- 2026-06-03T10:37:14+03:00 completed implementation, verification, spec sync and archive for all four changes
- 2026-06-03T12:42:16+03:00 published with scoped commit message `feat(protocol): resolve readonly element hash gaps`; final commit hash is reported by git history
