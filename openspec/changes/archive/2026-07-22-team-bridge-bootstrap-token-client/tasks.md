## 1. Contract

- [x] 1.1 Inspect the existing component baseline and root dependency root f5-40-c10-team-git-onboarding-contract; record compatibility and safety boundaries.
- [x] 1.2 Add the versioned schema/client model and fail-closed validation required by the spec.

## 2. Implementation

- [x] 2.1 Implement redeem a short-lived server/project/user-bound onboarding grant once and store only protected bridge refresh/registration state while retaining explicit-token advanced compatibility.
- [x] 2.2 Add protected-state, redaction, idempotence/restart and compatibility behavior.

## 3. Verification

- [x] 3.1 Add success and negative tests proving: a valid grant registers without revealing credentials while expired, replayed, revoked or mismatched grants fail closed and leave no partial usable state.
- [x] 3.2 Run offline parser/exchange/replay/expiry/revoke/permission/redaction tests and retain only redacted commands/outcomes.
- [x] 3.3 Run component-required checks, openspec validate --all --strict and git diff --check.

## 4. Integration Handoff

- [x] 4.1 Update component docs/card and provide root with the reviewed contract version and commit/evidence summary.

## Completion Evidence

- Root contract source pinned to
  `root:f5-40-c10-team-git-onboarding-contract@5afed8cf668e0c9bdbb44a1d167470e9b58295e5`.
- RED evidence: `.runtime/team-bridge-bootstrap-credential-exchange/token-client-red.log`
  and `installer-red.log`.
- Offline verification: Go package tests/vet/race, Windows cross-compile, 838
  non-live Python tests and focused installer/smoke/artifact tests.
- Windows artifact SHA-256:
  `0f4b7fd1b2dcc44b0d48a515fc355a680f7f8b484c7811711311531d8abb2e81`.
- Review rescue verified root-compatible `Basic`, mixed-case `Bearer` and
  `token` Authorization values, malformed scheme rejection, strict envelope /
  payload / digest / response / restart-state failures and native Windows DACL
  rejection before any bootstrap exchange.
