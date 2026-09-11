# Retry I13 S4 Isolation After Session-1 Admission Restoration

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i15

## Order Index
405.10198

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/4.done/oss-06-s4-r1-i14-investigate-i13-s4-early-exit-and-task-topology-drift.md`

## Source
- Published I14 bounded investigation decision.
- Published I11 commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.
- Fresh operator authorization for exactly one original-contour typed
  Session-1 canary and, only after its success, one exact-source S4 isolation.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `yes`
- Live admission: `yes`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Use the separately restored original interactive Session-1 route for one
fail-closed admission canary and, only if it succeeds, one exact-source S4
isolation against the unchanged published I11 candidate and immutable run-1
fixture. Retain a bounded decision without retrying or certifying I13.

## Acceptance
- Use only the freshly operator-authorized original contour; do not provision,
  restore, unlock, rebind, administer or substitute any session, host,
  identity, platform, fixture, candidate or argv.
- Reconfirm the unchanged five-blob published-I11 lineage, exact candidate,
  platform, target, configuration, run-1 fixture and argv identities, an
  initially uncontended exact-owned surface and a successful typed Session-1
  canary before one S4 candidate invocation.
- If the typed Session-1 canary does not succeed, invoke no candidate and retain
  the truthful fail-closed `NOT-VERIFIABLE`/`BLOCKED` outcome with its resume
  condition; do not widen authority or retry.
- If the canary succeeds, invoke the exact-source S4 candidate at most once and
  retain only a closed stage/class, hashes, counts, booleans, exit code and
  duration; retain no raw output, UI, screenshots, credentials, connection
  strings, broad dumps or task names, and do not claim I13 certification.
- Observe the original started route with bounded scheduler attribution so the
  historical topology delta can distinguish harness/start behavior from
  external drift; if bounded evidence cannot distinguish them, retain
  `NOT-VERIFIABLE` and infer no cause.
- Restore the exact configuration before-image, remove only exact-owned state
  and prove repeated cleanup is a no-op; retain the initial last-access baseline
  and typed job/desktop/transport zero-state, and stop on any foreign target or
  residual owned state.
- Pass retained-evidence privacy/schema checks, focused/full offline Go and vet,
  deterministic unexecuted cross-builds, strict OpenSpec, manifest scope,
  public-surface, Apache-2.0 and tracked-plus-untracked whitespace gates before
  fresh critical/xhigh review.

## Non-Goals
- Retrying the I13 certification matrix, starting any other I13 row or claiming
  I13 certification.
- Changing product/test source, runtime authority, public or wire behavior,
  fixtures, candidate, argv or license paths.
- Restoring, unlocking, provisioning, administering or substituting any live
  contour surface inside this card.
- Mutating, exposing, stopping or removing unrelated tasks, processes,
  sessions or state.

## Depends On
- Published I14 investigation decision.

## Blocks
- `oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence`
- `oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle`

## Change Set
1. `retry-i13-s4-isolation-after-session1-admission-restoration`

## Verify
- Exact five-blob/candidate and contour preflight passed. The one typed
  Session-1 canary produced no receipt; candidate invocation count is zero and
  the conditional fixture/argv/S4 gate was not reached.
- Exact configuration and task/stage/process/job/desktop/transport/1C cleanup
  passed with a no-op rerun. Protected count stayed unchanged and the exact
  post-cleanup hash matches the historical before value, but the scheduler log
  is disabled and topology attribution remains `NOT-VERIFIABLE`.
- Nine-entry typed evidence index validates.
- `go -C host-agent/windows-display-agent test . -run
  '^(TestHiddenDirect|TestS4R2)' -count=1`, `go -C
  host-agent/windows-display-agent test ./... -count=1` and `go -C
  host-agent/windows-display-agent vet ./...` passed; deterministic unexecuted
  Windows amd64/386 production and test build pairs were byte-identical and
  exact temporary binaries were removed.
- `bin/openspec validate --all --strict`, `git diff --check`, the scoped shared
  public-surface scanner, tracked-plus-untracked whitespace, privacy,
  Apache-2.0 and delivery-manifest scope gates passed.

## Archive
- `openspec/changes/archive/2026-09-02-retry-i13-s4-isolation-after-session1-admission-restoration/`

## Related
- `docs/protocol-research/evidence/i14-i13-s4-early-exit-and-task-topology-investigation-2026-09-02/decision.json`
- `docs/protocol-research/evidence/i14-i13-s4-early-exit-and-task-topology-investigation-2026-09-02/findings.md`
- `openspec/changes/archive/2026-09-02-retry-i13-s4-isolation-after-session1-admission-restoration/`
- `openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md`
- `docs/protocol-research/evidence/i15-session1-admission-and-s4-isolation-2026-09-02/decision.json`
- `docs/protocol-research/evidence/i15-session1-admission-and-s4-isolation-2026-09-02/findings.md`

## Result
`NOT-VERIFIABLE`. The one authorized original-route canary produced no typed
Session-1 receipt, so candidate invocation count is exactly zero and no S4/I13
row ran. Exact configuration and owned-state double cleanup passed. Protected
task count remained unchanged and the exact post-cleanup hash matches the
historical before value, but disabled scheduler attribution and the missing
pre-start identity hash cannot distinguish harness/start behavior from external
drift. No cause is inferred; I13 remains active, unarchived and uncertified.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `retry-i13-s4-isolation-after-session1-admission-restoration`

### Why
I14 could not admit even a typed Session-1 canary, so it accepted no candidate
result and left the historical started-route topology delta unattributed.

### Goal
Use the separately restored original route to admit one typed canary and, only
after success, observe one exact-source S4 isolation with bounded topology and
cleanup evidence.

### Scope
- Exact published/runtime/input identity and initial before-images.
- One typed Session-1 canary followed conditionally by one exact-source S4
  isolation.
- Original started-route scheduler/topology attribution.
- Exact configuration restoration, exact-owned double cleanup and public-safe
  decision evidence.

### Acceptance
- The decision is evidence-backed, fail-closed, privacy-safe, changes no
  product/test or license path and does not claim I13 certification.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-09-02-retry-i13-s4-isolation-after-session1-admission-restoration/`

## Log
- 2026-09-02 created by published I14 as the only proposed successor after the
  original interactive route failed to admit a typed Session-1 canary.
- 2026-09-02 accepted after fresh operator authorization and fast-forwarded as
  one evidence-only change with an admission-before-candidate gate, one exact
  S4 ceiling, bounded started-route attribution and exact double-cleanup; no
  runtime action or implementation occurred during planning.
- 2026-09-02 exact source/candidate and contour preflight passed with initial
  configuration last-access plus typed owned job/desktop/transport zero-state.
  The one authorized original-route canary produced no Session-1 receipt, so
  candidate invocation remained zero and no fixture, S4 argv or I13 row was
  admitted. Exact task/process cleanup was a no-op after controller cleanup;
  stage cleanup removed one exact stage then zero; all initial configuration
  hashes and owned/1C zero-state matched afterward. Protected count stayed
  unchanged and the exact post-cleanup hash matched the historical before
  value, but the scheduler log was disabled and the pre-start identity hash was
  unavailable, so topology remains `NOT-VERIFIABLE` without causal inference.
- 2026-09-02 focused/full Go and vet, deterministic unexecuted Windows
  amd64/386 cross-build pairs, evidence/privacy, strict OpenSpec,
  public-surface, Apache-2.0, whitespace and manifest scope gates passed. The
  new decision capability was synced and archived; I13 remains active,
  unarchived and uncertified.
- 2026-09-02T10:24:16Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
