# Bind Direct-Execute Receipt Foundation

## Status
4.done

## Owner
unassigned

## Series
oss-06-s6

## Order Index
405.9

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Add one dormant internal typed receipt boundary between the published Go
hidden-direct-execute chain and Python. Bind every admitted receipt to an
immutable, opaque current-run cleanup identity and a single-use stop lease,
while leaving every public capability, tool and profile route disabled.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Acceptance
- Added production LOC is `<=300` across isolated portable Go and Python
  boundary files; published S1-R1 through S5-R1 source/test files remain
  byte-identical to `3a0e0f6899e75c05c33ba762d3c89873bf610b81`.
- Go binds only schema-valid successful S4/S5 typed receipts to the exact
  S1/S2 run, token, desktop, port and worker/child/listener identity. Python
  admits only the exact immutable serialized binding for its current run.
- Malformed schema/status/hash/count/type, stale/replayed receipt, mismatched
  run identity, foreign or ambiguous cleanup identity and any mutation after
  binding fail closed with zero cleanup, action or public-route calls.
- One admitted stop lease invokes its injected exact-owned cleanup once. A
  repeated stop, repeated cleanup, reused receipt or foreign lease is refused
  before another callback.
- Receipts retain only typed outcomes, bounded counts, booleans and lowercase
  SHA-256 values; no raw UI, path, credentials, connection string, handle,
  screenshot or exception content crosses the boundary.
- The foundation remains dormant: no non-test caller, public capability,
  `open_external_processor` tool, profile field, stable admission, chooser,
  global input, foreground/desktop switch or raw UI action is added.
- Focused RED/GREEN, full Go/Python suites, Go vet, Windows cross-build,
  deterministic clean composition, LOC/predecessor/caller/public/forbidden/
  privacy scans, strict OpenSpec, manifest scope and diff gates pass.

## Scope
- Add one portable Go receipt-binding/stop-lease source and adjacent hostile
  tests that consume the already-published S1-S5 internal types.
- Add one internal Python receipt-binding/stop-lease module and adjacent
  hostile tests with the same exact schema and cleanup-binding rules.
- Retain ignored privacy-safe evidence containing commands, hashes, counts and
  typed outcomes only.

## Non-Goals
- No edits to published S1-S5 source/test files or dirty combined host-agent
  integration files.
- No public route, MCP/tool/profile/capability wiring, S7 stable admission,
  OSS-07 work or roadmap publication.
- No chooser, global input, visible/foreground action, desktop switch, raw UI,
  credential, path, screenshot or Windows live prompt rerun.

## Depends On
- Published S5-R1
  `openspec/board/4.done/oss-06-s5-r1-replace-prompt-fingerprint-with-addressed-admission.md`

## Change Set
1. `bind-hidden-direct-execute-receipt-foundation`

## Verify
- Hostile RED first for malformed schema/status/hash/count/type, stale/replayed
  receipt, mismatched run, foreign/ambiguous cleanup, mutation after binding
  and repeated stop; assert zero callbacks on every rejected row.
- Exact focused Go and Python tests, `go test ./...`, `go vet ./...`, full
  Python suite, Windows test and host-agent cross-build.
- Clean composition from published `3a0e0f6...` plus exact S6 paths; production
  additions `<=300`; all published S1-S5 source/test hashes unchanged.
- Dormant-caller, public-route/profile, forbidden-action and privacy scans;
  `bin/openspec validate --all --strict`, manifest working-tree scope-check and
  `git diff --check`.

Observed: initial hostile compile/import RED and review-cycle-1 rescue RED
preceded implementation. The rescue reproduced Python acceptance of PID
`4294967296`, a Python two-callback replay and a Go ledger data race. Focused Go
under `-race` and Python now pass; full Go/vet pass, ambient Python is `1654
passed`, clean-composed Python is `1581 passed, 4 skipped`, Windows test/host
cross-builds pass, production is `288/300`, and all `22` published predecessor
files are byte-identical. The ignored evidence index retains only hashes,
counts and typed outcomes.

## Archive
- `openspec/changes/archive/2026-08-31-bind-hidden-direct-execute-receipt-foundation/`

## Result
- Added one dormant portable Go receipt/cleanup lease and one frozen internal
  Python parser/lease with exact cross-language cleanup hashing, strict nested
  receipt validation, exact Go `uint32` PID bounds, post-bind mutation detection
  and atomic shared-ledger single-use cleanup. Rejected rows invoke no callback;
  concurrent leases invoke cleanup once and callback failure remains consumed.
- No published S1-S5 source/test, Windows runtime behavior, public capability,
  MCP/tool/profile route, S7 or OSS-07 path changed.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `bind-hidden-direct-execute-receipt-foundation`

### Why
Published S1-S5 prove the dormant hidden lifecycle, observation and addressed
prompt action, but no typed boundary lets Python accept the result without
also accepting mutable, stale or foreign cleanup identity.

### Goal
Publish the smallest dormant cross-language receipt and single-use cleanup
binding that fails closed before callbacks and adds no public authority.

### Scope
- Add only the isolated Go/Python boundary source and adjacent tests.
- Bind exact current-run hashes/counts to an opaque immutable cleanup hash.
- Prove hostile rejection, single-use cleanup and dormant/public safety.

### Acceptance
- Every card criterion passes within `300` added production lines.
- Clean composition and predecessor-byte gates isolate the S6 payload from the
  dirty combined S7/public-route candidate.
- One fresh independent ordinary/high review is required before publication.

### Depends On
- Published S5-R1 at `3a0e0f6899e75c05c33ba762d3c89873bf610b81`.

### Related
- `openspec/changes/archive/2026-08-31-bind-hidden-direct-execute-receipt-foundation/`

## Log
- 2026-08-31 FF corrected the stale S5-R1 dependency, removed the obsolete
  review-gated prerequisite and bounded S6 to one dormant internal change.
- 2026-08-31 delivery excludes all preexisting dirty combined/public-route,
  roadmap, S7/OSS-07 and `.codex/config.toml` paths; no staging, review,
  commit, push or Windows live action is authorized in this worker session.
- 2026-08-31 hostile RED established missing Go symbols and Python module, then
  isolated GREEN implementation passed focused/full ambient and clean-
  composition Go/Python, vet, Windows cross-build, LOC, predecessor, caller,
  forbidden/public and privacy gates.
- 2026-08-31 synced only
  `qa-mcp-hidden-direct-execute-receipt-foundation`, archived only the S6
  change and moved S6 to review-gated `3.inprogress`; fresh independent review
  remains intentionally unstarted.
- 2026-08-31 independent review cycle 1 returned NO-GO R1/R2: Python admitted
  PID values above Go `uint32`, and shared-ledger check/add was non-atomic.
- 2026-08-31 rescue attempt 1 added hostile PID/concurrency RED oracles, bounded
  Python PIDs to `1..4294967295`, atomically consumed shared ledgers in both
  languages, reran the complete offline matrix, and stopped for fresh review
  cycle 2 without launching review, staging, committing, pushing or starting
  S7/OSS-07.
- 2026-08-31T16:08:36Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
