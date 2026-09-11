# Certify Hidden Desktop Process Foundation Replacement

## Status
4.done

## Owner
unassigned

## Series
oss-06-s1-r1

## Order Index
405.41

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Replaces
- Unpublished exhausted
  `openspec/board/3.inprogress/oss-06-s1-extract-hidden-desktop-process-foundation.md`.

## Source Lineage
- Latest safe published baseline:
  `b847d08c4a139edb4a9c5e03ca313731b5d049b1`.
- S1 final cycle-3 reviewed tree:
  `a54ad92cfcdb2037ef66be188270445ecb2b2e22`; fingerprint:
  `sha256:6a16ae5e4130e36722a1a4f8e7854df98f9dea96e2b04af127c60e0537f6c6f6`.
- Canonical predecessor verdict/history:
  `.runtime/changerail/reviews/oss-06-s1-extract-hidden-desktop-process-foundation.json`
  and the adjacent history; cycles `1–3` consumed rescue budget `2/2`.
- Final blocker: the exact-source native command selected ProcessContract and
  NativeLifecycle but omitted the separately named
  CleanupClosesHandlesWhenTerminateFails GREEN oracle while evidence claimed
  it executed.
- Exact adopted S1 source/test hashes are retained in
  `.runtime/changerail/evidence/oss-06-s1-extract-hidden-desktop-process-foundation/final-verification.json`;
  candidate SHA-256 is
  `ef3292b80fb0f72e69c09ae192a457d2e9fddeec73acd3975c4fd77cc7481c7f`.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Publish the otherwise accepted dormant S1 foundation through a clean linked
replacement that executes the one omitted exact-source Windows GREEN oracle
and keeps evidence claims identical to the tests actually selected.

## Acceptance
- The replacement adopts only the four exact S1 source/test files plus their
  card/archive/spec lineage; production source remains `248/300` LOC and has no
  non-test caller, wire/public route or global-input action.
- An exact-source Windows candidate runs ProcessContract,
  CleanupClosesHandlesWhenTerminateFails and NativeLifecycle in one literal
  command, and all three pass.
- The retained native/evidence index claims only oracles selected by that exact
  command; candidate/source hashes and exact-owned cleanup are reproducible.
- Focused/full Go, Windows test and host cross-build, strict OpenSpec, manifest
  scope-check, production LOC and `git diff --check` gates pass.
- A fresh independent ChangeRail review returns `GO` before publication; the
  exhausted S1 verdict/history remain immutable lineage.

## Scope
- Adopt the exact four S1 source/test files without production behavior change.
- Add an explicit terminate-failure exact-owned cleanup scenario to the S1
  capability and certify it with the already-present regression test.
- Refresh sanitized replacement evidence and scoped delivery manifest.
- No S2 worker/job/TPort lifecycle, TestClient, public route, 1C, Docker,
  global input, desktop switch or user-visible UI action.

## Change Set
1. `certify-hidden-desktop-process-foundation-native-green`

## Depends On
- Published OSS-06 A2 authorization.
- Exhausted S1 cycle-3 verdict/history and exact retained source/candidate
  lineage.

## Blocks
- `openspec/board/1.backlog/oss-06-s2-extract-hidden-worker-lifecycle.md`

## Verify
- Literal focused/full Go and Windows cross-build commands.
- Clean-baseline composition from published HEAD plus only the four exact S1
  source/test files.
- Exact-source Windows native regex selecting all three named tests, with
  candidate hash, task result and bounded cleanup inventory.
- Canonical `<=300` production LOC preflight, strict OpenSpec, manifest
  scope-check and `git diff --check`.

## Archive
- `openspec/changes/archive/2026-08-30-certify-hidden-desktop-process-foundation-native-green/`

## Related
- `openspec/changes/archive/2026-08-30-certify-hidden-desktop-process-foundation-native-green/`
- `openspec/changes/archive/2026-08-30-extract-hidden-desktop-process-foundation/`

## Result
Exact-source candidate `ef3292b8...` passed the literal three-test Windows
selector with `LastTaskResult=0`. The same trusted host resumed at `.201`;
exact task/stage ownership was reverified and removed with owned/1C processes
at zero, listener `18081` preserved and Docker inventory unchanged at zero.
Strict/spec/scope/diff and canonical `248/300` gates pass; the change is synced
and archived, and fresh independent review cycle 1 returned `GO`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `certify-hidden-desktop-process-foundation-native-green`

### Why
The exhausted S1 code/test payload is otherwise accepted, but its final
evidence overclaimed one Windows-only oracle that the native regex did not run.

### Goal
Publish the exact dormant foundation with a truthful hash-bound Windows GREEN
for all three required tests.

### Scope
- Adopt unchanged exact S1 source/test payload and durable lineage.
- Make terminate-failure dual-close behavior explicit in the capability.
- Run and index the literal three-test native command and exact-owned cleanup.
- No new production behavior, authority, wire, route or S2 scope.

### Acceptance
- All card criteria pass against one exact candidate/source lineage.
- Predecessor final `NO-GO` and rescue exhaustion remain unchanged.
- Fresh independent replacement review returns `GO` before scoped publish.

### Depends On
- Exhausted S1 review cycle 3.

### Related
- `openspec/changes/certify-hidden-desktop-process-foundation-native-green/`

## Log
- 2026-08-30 linked replacement authorized by the operator after S1 final
  cycle-3 `NO-GO`; no third same-card rescue or S2 work was started.
- 2026-08-30 fast-forward created one apply-ready replacement change with
  exact S1 lineage, a normative terminate-failure cleanup scenario and a
  literal three-test Windows GREEN gate; production behavior remains unchanged.
- 2026-08-30 moved to `3.inprogress`; linked replacement delivery started
  without changing the adopted production/test source.
- 2026-08-30 exact candidate `ef3292b8...` passed ProcessContract,
  CleanupClosesHandlesWhenTerminateFails and NativeLifecycle in one literal
  Windows command. The host then became unreachable across the authorized
  DHCP range before post-cleanup inventory could be certified; delivery paused
  as `NOT-VERIFIABLE` without archive, review or publication.
- 2026-08-30 the same trusted `HISTORICAL-LAB-HOST\\historical-user` resumed at `.201`
  with the previously trusted ED25519 fingerprint. Exact task/action/args/path/
  hash ownership was reverified; only the current-run task/stage were removed.
  Post-inventory retained owned/1C processes `0`, listener `18081` = `1` and
  Docker inventory `0`.
- 2026-08-30 replacement scenario synced and change archived; focused/full Go,
  vet, exact hashes, strict OpenSpec, manifest scope, diff and canonical
  `248/300` LOC checks pass. Fresh independent review is pending.
- 2026-08-30T16:16:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
