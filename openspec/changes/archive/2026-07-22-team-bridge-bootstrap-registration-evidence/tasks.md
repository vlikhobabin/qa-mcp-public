## 1. Contract

- [x] 1.1 Inspect the existing component baseline and root dependency team-bridge-bootstrap-token-client; record compatibility and safety boundaries.
- [x] 1.2 Add the versioned schema/client model and fail-closed validation required by the spec.

## 2. Implementation

- [x] 2.1 Implement extend bridge lifecycle smoke/evidence to prove bootstrap redemption, protected refresh, per-user/project attribution, restart recovery and exact process cleanup.
- [x] 2.2 Add protected-state, redaction, idempotence/restart and compatibility behavior.

## 3. Verification

- [x] 3.1 Add success and negative tests proving: component runtime preflight and live smoke show correct attribution after restart/refresh with only ids/status/digests retained.
- [x] 3.2 Run component preflight, Windows host registration/heartbeat/restart/refresh and cleanup smoke and retain only redacted commands/outcomes.
- [x] 3.3 Run component-required checks, openspec validate --all --strict and git diff --check.

## 4. Integration Handoff

- [x] 4.1 Update component docs/card and provide root with the reviewed contract version and commit/evidence summary.

## Completion Evidence

- Retained redacted evidence:
  `.runtime/team-bridge-bootstrap-credential-exchange/live-cycle2-final2/{preflight.json,live-summary.json,evidence.json}`.
- Authorized Windows host `HISTORICAL-LAB-HOST` registered as
  `developer-a` for `team/demo10413` on `team-server-primary`; 8 issued grants
  produced 8 one-time redemptions and registrations.
- Final artifact survived a scheduled-task restart (`3128` -> `19876`), kept
  its state DACL protected, served a read-only 12-window probe and left no
  owned task, process, directory or listening port after cleanup.
- Retained summaries contain no raw grant, Git authorization, registration
  credential, bridge callback token or window title.
- Review rescue ran the Windows-only DACL and malformed-envelope/state suite
  natively on `HISTORICAL-LAB-HOST`; unsafe grant, Git authorization and restart
  state ACLs all failed before use.
