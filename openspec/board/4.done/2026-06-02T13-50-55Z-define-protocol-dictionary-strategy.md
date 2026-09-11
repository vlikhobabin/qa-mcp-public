# Define Protocol Dictionary Strategy

## Status
4.done

## Priority
P0 - completed strategy baseline; retained as a planning reference.

## Owner
unassigned

## OpenSpec Stage
reference

## Source
- 2026-06-02 protocol research strategy discussion
- `docs/protocol-research/evidence/infrastructure-checks/20260602-161326/infra_check.md`

## Summary
Adopt a hybrid protocol dictionary strategy: keep the TCP proxy as the
byte-level source of truth, execute many short marked 1C testing API cases,
normalize their request/response evidence, and confirm each useful mapping by
Python replay against a live TestClient without a 1C TestManager instance.

This should produce a practical dictionary:

```text
1C testing API call -> frame range -> normalized request shape -> dynamic fields -> response markers -> replay status
```

The strategy explicitly avoids one large unsegmented command run. A minimal
reference 1C runner may be added, but only as a controlled source of marked
cases; the protocol evidence remains the captured TCP traffic and replay
results.

## Acceptance
- The next implementation cards follow the priority order defined here.
- The corpus evidence contract is documented before broad command capture:
  `case_id`, `api_call`, `ui_target`, `expected_state`, `frame_range`,
  request/response sizes, `normalized_hash`, dynamic fields,
  `operation_token`, `response_markers` and `replay_status`.
- The first corpus scope is limited to read-only `TestedApplication`,
  `TestedForm`, window and form-element properties/methods.
- Replay/probe confirmation is required before a protocol mapping is treated as
  working knowledge.
- Raw captures remain in `runtime/`; compact evidence is kept under
  `docs/protocol-research/evidence/`.

## Change Set
- none yet

## Verify
- Strategy is reflected by completed cards:
  `Build Protocol Corpus Runner` and `Expand Readonly Protocol Corpus Matrix`.
- The corpus evidence contract exists in
  `docs/protocol-research/corpus-evidence-contract.md`.
- Compact evidence is indexed under
  `docs/protocol-research/evidence-index.md`.

## Archive
- N/A - planning/reference card; implementation shipped through the completed
  corpus runner and expanded matrix cards.

## Related
- `docs/protocol-research/methodology.md`
- `docs/protocol-research/evidence-index.md`
- `docs/protocol-research/evidence/infrastructure-checks/20260602-161326/infra_check.md`
- `openspec/board/4.done/2026-06-02T12-45-00Z-build-protocol-corpus-runner.md`
- `openspec/board/4.done/2026-06-02T16-14-18Z-expand-readonly-protocol-corpus-matrix.md`
- `openspec/board/4.done/01-2026-06-02T18-01-06Z-accept-readonly-corpus-probe-mappings.md`
- `openspec/board/4.done/02-2026-06-02T12-46-00Z-promote-python-testmanager-core.md`
- `openspec/board/4.done/03-2026-06-02T12-47-00Z-prepare-edt-meta-protocol-fixtures.md`
- `openspec/board/1.backlog/04-2026-06-03T05-30-00Z-capture-controlled-readonly-fixture-evidence.md`
- `openspec/board/1.backlog/05-2026-06-03T05-31-00Z-resolve-readonly-element-hash-gaps.md`
- `openspec/board/1.backlog/06-2026-06-02T16-15-00Z-capture-safe-ui-action-protocol-cases.md`

## Result
The hybrid dictionary strategy has been adopted. The lab now uses short marked
read-only cases, normalized evidence rows, repeated captures, dynamic-field
normalization and direct Python replay/probe confirmation as the acceptance
path for protocol mappings.

The read-only direct probe evidence has been promoted into accepted corpus rows
and the stable Python TestManager primitives have been moved into `src/qa_mcp`.
The remaining near-term gaps are controlled read-only fixture evidence for
unresolved element families and reviewed request-frame hashes for useful
element probe paths before safe action protocol cases are expanded.

## Next
- none; execute the indexed backlog from
  `openspec/board/4.done/01-2026-06-02T18-01-06Z-accept-readonly-corpus-probe-mappings.md`

## Change Plan Notes
Current execution order:

1. `Accept Readonly Corpus Probe Mappings` - close the accepted-mapping gap
   by joining direct Python probe evidence to repeated corpus rows.
2. `Promote Python TestManager Core` - move stable protocol primitives into
   `src/qa_mcp` after the accepted mapping model is proven.
3. `Prepare EDT And Meta Protocol Fixtures` - support richer fixture and
   metadata mapping for read-only element families.
4. `Capture Controlled Readonly Fixture Evidence` - turn planned fixture rows
   for missing read-only families into reviewed corpus/probe evidence.
5. `Resolve Readonly Element Hash Gaps` - close or sharpen the
   `form-element-details` and `typed-input-field-readonly` `incomplete_hash`
   status.
6. `Capture Safe UI Action Protocol Cases` - start the first non-mutating
   action layer after read-only acceptance is stable.

Initial corpus design:

- Use current Vanessa attach-running flow first because it is already verified.
- Add case markers around one API call or one property group at a time.
- Repeat each case across runs to separate dynamic session fields from command
  semantics.
- Add a minimal 1C reference runner only if Vanessa noise blocks clean
  segmentation or if direct platform API calls are needed for coverage.
- Keep write/action commands out of scope until read-only evidence is stable.

## Log
- 2026-06-02T13:50:55Z card created
- 2026-06-02T18:01:06Z closed as completed strategy reference after corpus runner and expanded matrix delivery
- 2026-06-03T06:45:37+03:00 updated after accepted corpus mappings and Python TestManager core promotion
