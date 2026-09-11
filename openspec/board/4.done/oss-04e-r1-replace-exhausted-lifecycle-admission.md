# Replace Exhausted TestClient Lifecycle Admission

## Status
4.done

## Owner
unassigned

## Series
oss-04e-r1

## Order Index
4035.1

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Replaces
- Unpublished exhausted
  `oss-04e-bind-testclient-lifecycle-admission`.

## Source Lineage
- Latest safe published baseline:
  `0bc7f45d18b6ded8fe8f0720bd16357b49b8ced9`.
- OSS-04E final cycle-3 tree:
  `a28c892287e08ada62f2e3140cd0eb7a466a03e1`; fingerprint:
  `sha256:566e0aef72e77b6670bbdc8517b891f2671209bec9843b1dc4f11cadb95e15ab`.
- Evidence-only stash `oss04e-exhausted-review-payload-20260826`, stash commit
  `9f68d9e2f8e7ba31d00b4ef03d4654fdf2a84a5b`. It proves lineage only and MUST
  NOT be restored or published wholesale.
- Canonical ignored evidence:
  `.runtime/changerail/evidence/oss-04e-bind-testclient-lifecycle-admission/index.json`
  (`48` entries),
  `.runtime/changerail/reviews/oss-04e-bind-testclient-lifecycle-admission.json`
  and the adjacent history.
- Cycle 1 blockers: remote attach probed before host-agent observation, remote
  launch admitted a mismatched target, unset host-agent port became zero and a
  process-global platform version overrode the provider profile.
- Rescue 1 closed those four blockers. Cycle 2 found client-target PID and
  lifecycle-handle PID/port disagreement still admitted; rescue 2 closed those
  explicit disagreements.
- Cycle 3 blocker: absent/zero raw `client_target.port` was defaulted and an
  `id` alias substituted for missing explicit `lifecycle_id`; all incomplete
  observations returned success and created a session. Review cycles `1–3`
  consumed rescue budget `2/2`, remaining `0`, exhausted `true`.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Repeated-defect rationale: this replacement closes the one exact retained
  raw-observation invariant before any broader lifecycle work.
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Goal
Reimplement the target-bound lifecycle admission capability from clean
published `main` and admit a remote owned TestClient session only when every
required raw identity member is explicit, correctly typed and exactly coherent.

## Acceptance
- Project launch/attach use only the provider profile; caller overrides and
  unavailable or mismatched targets return secret-safe typed blocked outcomes
  before Apache, Xvfb, platform, host-agent or protocol side effects.
- Project-bound remote launch requires an explicit positive integer PID and
  TPort plus an explicit non-empty `lifecycle_id` in the raw `client_target`;
  missing, zero, boolean, string or alias-only members fail closed without
  normalization to defaults.
- Top-level launch PID/port/lifecycle ID, raw `client_target` and raw lifecycle
  handle PID/port/id agree exactly before session creation; every disagreement
  leaves attachment/session state empty.
- Immutable target/session/generation/ownership/lifecycle identity remains
  secret-safe, and explicit unbound standalone schemas/behavior remain
  compatible.
- Production additions remain at or below `300` LOC; no cleanup completion,
  bound schema hiding, protocol change or final live certification is added.
- The exact focused/full/Windows verification floor passes and a fresh
  independent ChangeRail review returns `GO` before publication.

## Scope
- Reimplement the existing lifecycle admission capability in
  `src/qa_mcp/mcp_server.py`, its focused tests, synced spec/archive, cards and
  retained ignored verification evidence.
- Update the already-published apply-ready OpenSpec artifacts before apply so
  raw required-field/type/alias rejection is normative and directly tested.
- No restore of the exhausted stash, new public tool, authority, wire protocol,
  cleanup completion, schema hiding or OSS-04F implementation.

## Change Set
1. `bind-qa-mcp-testclient-lifecycle-admission` -
   `openspec/changes/archive/2026-08-27-bind-qa-mcp-testclient-lifecycle-admission/`

## Dependencies
- OSS-04D-R8 is published.
- OSS-04E has a fresh exhausted cycle-3 verdict/history and retained stash
  lineage.

## Blocks
- `openspec/board/2.todo/oss-04f-enforce-target-evidence-cleanup.md`

## Verify
- Test-first adversarial RED for absent/zero/boolean/string raw port, absent or
  alias-only lifecycle ID, invalid PID and top-level/client-target/handle
  disagreement; each case asserts no session and no downstream probe.
- Target-bound lifecycle and focused lifecycle/MCP/runtime-target suites.
- Exact full non-live CI with coverage, Python compilation, `git diff --check`,
  strict OpenSpec validation and production LOC gate `<=300`.
- Exact-source/wheel Windows offline admission proof on the authorized
  architect workstation and exact owned-stage cleanup/post-inventory.
- Delivery manifest scope reconciliation, deterministic preflight and fresh
  independent review.

## Result
Fresh implementation from published `main` admits only explicit coherent raw
remote identity and leaves every incomplete/mistyped/mismatched case without a
session or attachment. The payload adds `248` production lines, preserves the
standalone surface, syncs the new main spec and archives its completed change.
After review rescue 1, Linux gates pass with `37` target tests, `418` focused
tests and `1567` non-live tests at `74.52%` coverage. The exact wheel SHA-256
`5f09b5c771455bacb26537f5e4744f63a85077c2aab622e3cea5de5b7a6e1b3c`
passed Windows offline admission on `HISTORICAL-LAB-HOST\user`; its exact owned
stage was removed and post-cleanup process/listener inventory is empty.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `bind-qa-mcp-testclient-lifecycle-admission`

### Why
The exhausted implementation normalized incomplete host-agent identity into an
apparently coherent target instead of validating the raw observation first.

### Goal
Admit lifecycle only after required raw identity is explicit, well typed and
exactly equal across all owned launch observations.

### Scope
- Update existing OpenSpec artifacts with the raw identity invariant.
- Fresh bounded implementation from published `main`, adversarial tests and
  Linux/Windows evidence.
- No failed-stash restore or OSS-04F scope.

### Acceptance
- Every card criterion and updated delta requirement passes.
- The implementation stays within `300` added production LOC.
- The change syncs, archives and receives a fresh independent `GO` review.

### Depends On
- Exhausted OSS-04E cycle-3 verdict/history and published OSS-04D-R8.

### Related
- `openspec/changes/bind-qa-mcp-testclient-lifecycle-admission/`

## Log
- 2026-08-26 created by ChangeRail escalation after OSS-04E review cycle 3
  returned one incomplete raw identity blocker at rescue budget `2/2`.
- 2026-08-26 exact failed OSS-04E payload was preserved as
  `oss04e-exhausted-review-payload-20260826`; clean published `main` and the
  existing apply-ready artifacts are the only implementation source.
- 2026-08-27 updated the active artifacts with canonical raw identity,
  exact-type/no-alias admission and adversarial no-session/no-probe matrices;
  FF validation is current.
- 2026-08-27 moved to `3.inprogress`; test-first implementation started from
  published `main` without restoring the exhausted payload.
- 2026-08-27 implemented strict raw identity admission at `242` added
  production LOC; `35` target, `416` focused and `1565` non-live tests passed
  at `74.51%` coverage, with compilation/diff/strict OpenSpec gates clean.
- 2026-08-27 exact wheel passed authorized architect-Windows offline admission;
  the one owned stage was removed and post-cleanup inventory is empty. Specs
  synced and the completed change archived for fresh review.
- 2026-08-27 independent review cycle 1 returned `NO-GO`: Python numeric
  equality could bypass subordinate exact-type checks and retained RED/Windows
  command provenance was incomplete. Same-card rescue 1/2 added explicit type
  validation and collision oracles for all projections, refreshed command-bound
  evidence, and passed `37` target, `418` focused and `1567` non-live tests at
  `74.52%` plus a refreshed exact-wheel Windows proof and cleanup.
- 2026-08-27T04:27:42Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
