## 1. Test-first registration contract

- [x] 1.1 Add Go tests for startup registration, heartbeat renewal, fixture-registry reset/recovery, lease expiry after stop, immutable user, rejection/network failure, token redaction, and zero-request solo mode; run them RED and retain the failure summary.
- [x] 1.2 Add tests for startup configuration validation and bounded registration health output.

## 2. Registration client implementation

- [x] 2.1 Implement the bounded `ai1c.bridge-registration.v1` client, discovery envelope, lifecycle, retry timing, and immutable startup identity.
- [x] 2.2 Wire opt-in flags/environment into host-agent startup without changing solo mode or existing bridge endpoints.
- [x] 2.3 Document registry configuration, heartbeat/TTL defaults, secret handling, and the live-registry provider gap.

## 3. Verification and evidence

- [x] 3.1 Run focused Go tests, full host-agent Go tests, full component pytest, strict OpenSpec validation, and diff checks; retain offline evidence.
- [x] 3.2 Record real Windows host-agent and root live-registry round-trip as supervised provider gaps; do not claim those AC as PASS.
- [x] 3.3 Confirm no TestClient protocol evidence index update is needed because this change makes no protocol claim.

## 4. Cycle-1 no-go rescue

- [x] 4.1 Replace the producer-coupled fixture decoder with independent raw
  JSON validation against a frozen `ai1c.bridge-registration.v1` schema and
  prove a field-name drift is rejected.
- [x] 4.2 Enforce registry recovery timing with a deadline derived from one
  configured heartbeat plus a documented scheduler tolerance.
- [x] 4.3 While a failing RegistrationClient is active, exercise an existing
  authenticated bridge operation and assert its normal result.
- [x] 4.4 Rerun focused and full verification, retain cycle-2 evidence, sync
  the unchanged requirement delta idempotently, and re-archive.

## Verification Notes

- Cycle-2 RED: `go test ./... -run
  'TestRegistration|TestBSLHelperSupervisorLifecycleRestartRoutesAndStop'
  -count=1` failed because the producer-coupled fixture accepted the drifted
  `ttl` field with HTTP 204. The same run initially exposed an incorrect GET in
  the new operation assertion; after aligning it to the existing POST route,
  the schema-drift failure was the sole RED failure.
- Cycle-2 focused PASS: the corrected suite and ten repeated runs each of the
  schema-drift, heartbeat-recovery, and helper-restart tests passed. The
  registry failure case invokes authenticated `/window_list` while
  `last_error=registry-unavailable` and asserts its normal result.
- Cycle-2 full PASS: Go test/race/vet, Windows AMD64 cross-build, full pytest
  (803), smoke pytest (3), canonical suite drift (0 findings), strict change,
  capability and workspace OpenSpec validation, matrix preflight/archive gates
  and `git diff --check` passed. Retained command/output paths are listed in
  `.artifacts/openspec/bridge-self-registration-client/2026-07-11-cycle2/offline-verification.txt`.
- Spec sync was idempotent: all three delta requirements were already present
  in `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`; scoped strict
  validation and `openspec validate --all` passed without changing semantics.

- RED: `go test ./... -run 'TestRegistration' -count=1` failed to compile
  because `registrationEnvelope`, `RegistrationConfig`,
  `NewRegistrationClient`, and `Config.Registration` did not exist.
- No native TestClient request/response behavior changed, so protocol capture,
  frame ranges, replay, and evidence-index updates are N/A.
- Real Windows endpoint reachability and the live root registry schema
  round-trip remain `unverifiable` provider gaps for the supervised stand.
- PASS: focused registration Go tests and all host-agent Go tests passed;
  Windows AMD64 cross-build passed; full component pytest passed 799 tests;
  suite source-of-truth drift passed; smoke passed 3 tests; strict change and
  workspace OpenSpec validation plus `git diff --check` passed.
