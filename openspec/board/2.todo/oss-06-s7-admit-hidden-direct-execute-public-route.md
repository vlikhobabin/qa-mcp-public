# Admit Hidden Direct-Execute Public Route

## Status
2.todo

## Owner
qa-mcp

## Series
oss-06-s7

## Order Index
405.10

## OpenSpec Stage
artifacts

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Repeated defect class: `no`
- Credential or mutation authority: `yes`
- Live admission: `yes`
- Final certification: `yes`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/oss-06-a2-authorize-bounded-hidden-direct-execute-admission.md","authorization_id":"oss-06-a2-authorize-bounded-hidden-direct-execute-admission"}`
- Authorized production LOC ceiling: `<=500`
- Published implementation baseline:
  `312e91453026cf808e6d48b521c971eb11e7ef96`

## Summary
Wire the published S1-S6 hidden direct-execute foundations into one backward-
compatible standalone Windows bridge capability and the stable project-bound
`open_external_processor` route. Preserve Linux behavior and fail closed when
the capability, typed receipt or exact-owned cleanup identity is absent or
invalid.

## Acceptance
- Added production LOC is `<=500` relative to exact published S6 baseline
  `312e914...`, with no deletion offsets, and the implementation matches the
  exact published I2/A2 authorization.
- Published S1-R1 through S6 foundation source/test files remain byte-identical;
  S7 composes them only through bounded host/Python integration paths.
- The authenticated bridge advertises
  `testclient-hidden-desktop-direct-execute` only when its existing launch
  route accepts an absolute EPF/ERF path and lowercase SHA-256 marker and can
  return the closed typed direct-execute receipt.
- Windows `open_external_processor` requires the advertised capability,
  immutable project target/session identity, the exact S6 receipt binding and
  one single-use exact-owned cleanup lease. Missing, malformed, stale, foreign,
  replayed or ambiguous identity fails before success or cleanup callbacks.
- The pre-stable tool schema keeps the `open_external_processor` name but
  exposes only a logical EPF/ERF path and optional expected caption; display,
  endpoint, coordinate, timing, retention and cleanup authority are absent.
- Windows uses only hidden native `/Execute`, S3/S4 observation, S5-R1
  addressed prompt action and S6 typed cleanup. Chooser, OCR/coordinates,
  global input, foreground takeover, desktop switching and older display/input
  fallback remain absent.
- Linux retains its existing target-bound qualified behavior and public result
  taxonomy; S7 does not broaden Linux input, evidence or cleanup authority.
- Public results retain only bounded stages, booleans, counts and hashes. Raw
  UI, paths, connection strings, credentials, handles and screenshots do not
  cross the bridge/Python boundary.
- Exact-source prompt-off, two distinct fresh prompt-on runs, recovery,
  malformed/capability-absent refusal and Python-to-MCP native proof pass on
  authorized Windows platform `8.3.27.2214` after final modularization, with
  zero `Default` leaks/global input/desktop switches and exact-owned cleanup.
- Stable admission occurs only after strict scope/LOC/predecessor/privacy
  gates, fresh critical `GO`, scoped publication and a final profile assertion.

## Depends On
- `openspec/board/4.done/oss-06-i2-publish-hidden-direct-execute-investigation-decision.md`
- `openspec/board/4.done/oss-06-a2-authorize-bounded-hidden-direct-execute-admission.md`
- `openspec/board/4.done/oss-06-s6-bind-direct-execute-receipt-foundation.md`
- Active certification
  `openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md`.
- Incomplete parent closure
  `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`.

## Change Set
1. `admit-hidden-direct-execute-public-route`

## Verify
- Hostile RED/GREEN for capability absence/version mismatch, malformed path or
  marker, invalid nested receipt, stale/replayed cleanup identity, duplicate
  stop, callback failure and every forbidden fallback; rejected rows invoke no
  launch, action, success or cleanup callback.
- Focused/full Go and Python suites, Go vet, compileall, Windows test/host
  cross-builds and public MCP schema/profile contract tests.
- Deterministic clean composition from published `312e914...` plus only S7
  paths; `<=500` production additions and exact S1-S6 predecessor hashes.
- Exact-source Windows prompt-off, fresh prompt-on, recovery and Python-to-MCP
  native matrices with exact cleanup and retained privacy-safe evidence.
- Strict change/all OpenSpec validation, authorization relation, manifest scope,
  untracked whitespace and `git diff --check` gates before critical review.

## Archive
- not started

## Related
- `openspec/changes/admit-hidden-direct-execute-public-route/`
- `openspec/board/4.done/oss-06-a2-authorize-bounded-hidden-direct-execute-admission.md`
- `openspec/board/4.done/oss-06-s6-bind-direct-execute-receipt-foundation.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md`
- `openspec/board/4.done/oss-06-s4-r1-i14-investigate-i13-s4-early-exit-and-task-topology-drift.md`
- `openspec/board/4.done/oss-06-s4-r1-i15-retry-i13-s4-isolation-after-session1-admission-restoration.md`
- `openspec/board/4.done/oss-06-s4-r1-i16-record-stable-profile-omission-after-i15.md`
- `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Result
Planning only. The single final S7 change is apply-ready against published S6
but blocked on I13 certification and published S4-R1 parent closure. No S7
implementation, runtime action, review, publication or OSS-07 work has started.
I16 omits `open_external_processor` from the stable standalone profile and
public support matrix; S7 remains incomplete and its dormant artifacts are not
deleted or certified.

## Next
- Do not run S7 delivery. I15 admitted no Session-1 receipt and invoked no
  candidate, so I13 remains uncertified. Resume only through a separately
  authorized successor after independently available typed admission, then
  review/publish I13 and the S4-R1 parent.
- After both prerequisites are tracked in `4.done`, deliver S7 from a clean
  composition of `312e914...`; preserve and exclude the dirty historical
  combined I1 payload and unrelated `.codex/config.toml`.
- Stable release no longer waits for S7 because I16 records the explicit
  omission. Any future S7 qualification remains a separately reviewed card
  with new authority; this card is not the next release-sequence delivery.

## Change 1: `admit-hidden-direct-execute-public-route`

### Why
S1-S6 now publish the dormant hidden lifecycle, observation, addressed prompt
action and cross-language exact cleanup receipt, but no reviewed public bridge
capability or MCP route composes them. The stable tool therefore remains
omitted even though its bounded foundations are complete.

### Goal
Publish the smallest backward-compatible bridge/Python integration that admits
`open_external_processor` only from the exact hidden direct-execute receipt and
exact-owned single-use cleanup identity.

### Scope
- Advertise and accept the bounded direct-execute capability through the
  existing authenticated bridge launch/stop surface.
- Compose published S1-S6 without editing their certified files.
- Bind the project-targeted Python operation and stable profile to the exact
  typed receipt, public stage taxonomy and single-use cleanup lease.
- Prove the final exact-source Windows matrix and unchanged Linux behavior.

### Acceptance
- Every card criterion passes within `500` production additions from
  `312e914...`, with published predecessor bytes unchanged.
- No rejected or ambiguous row produces launch, action, public success or
  cleanup authority, and no forbidden chooser/global-input fallback exists.
- One fresh independent critical review returns `GO` before publication or
  stable profile admission.

### Depends On
- Published I2 decision, A2 authorization and S6 at `312e914...`.

### Related
- `openspec/changes/admit-hidden-direct-execute-public-route/`

## Change Plan Notes
- This card owns only the final qa-mcp public integration. Runtime Proxy/RPW,
  Relay, Team, live-mcp and private AI for 1C downstream work remain in their
  owning repositories.
- The dirty combined I1 payload is historical evidence and MUST NOT be copied,
  restored, staged or treated as the S7 implementation baseline.
- Before critical review the card moves to its authorization-bound canonical
  `3.inprogress` path; planning in `2.todo` does not claim authorization use.

## Log
- 2026-08-31 S6 published at
  `312e91453026cf808e6d48b521c971eb11e7ef96` and satisfied the last S7
  prerequisite.
- 2026-08-31 fast-forward selected one bounded final integration change,
  preserved the published `<=500` authorization and excluded the dirty combined
  payload. No production implementation or runtime action was started.
- 2026-09-02 I12 reconciliation encoded the exact prerequisite graph: S7 stays
  blocked until I13 certification and the S4-R1 parent are independently
  reviewed, published and tracked in `4.done`.
- 2026-09-02 I13 stopped fail-closed after its first tracked S4 row exited
  before a receipt; I14 now owns the separate investigation. S7 remains
  blocked and no S7 runtime or implementation work started.
- 2026-09-02 I15 used one authorized original-route canary after exact
  preflight, but received no typed Session-1 receipt and invoked no candidate.
  S7 remains blocked and no S7 work started.
- 2026-09-02 I16 records stable-profile/public-support omission without
  completing S7, deleting its dormant artifacts or granting resume authority.
