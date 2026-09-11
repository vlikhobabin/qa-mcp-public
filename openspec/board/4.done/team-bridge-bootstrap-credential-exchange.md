# Team bridge bootstrap credential exchange

## Status
4.done

## Order Index
after published root team onboarding contract; before root workstation E2E

## Owner
qa-mcp host bridge client

## OpenSpec Stage
reviewed, synced, archived and published

## Source
- root `openspec/board/2.todo/f5-40-team-git-onboarding-contract.md`
- completed team host-agent self-registration baseline

## Summary
Teach the Windows host bridge to redeem a short-lived team onboarding grant and
register/refresh itself without asking an ordinary member to copy long-lived
bridge or gateway tokens.

## Acceptance
- Bridge accepts a protected short-lived grant reference, verifies
  server/project/user/source binding, redeems it once and stores only protected
  refresh material.
- Expired, replayed, revoked, wrong-user/project/server grants fail closed and
  never fall back to anonymous/default credentials.
- Registration/heartbeat/restart preserve per-user attribution and emit
  secret-free evidence suitable for root workstation smoke.
- Existing explicit-token advanced mode remains compatible; raw tokens are not
  printed, placed in argv or retained in captures/logs.
- Component's unrelated active `license-activation-bootstrap` change remains
  untouched and independently owned.

## Scope
- qa-mcp host-agent/bridge bootstrap client, protected state and offline/live
  registration tests.
- Root owns exchange server/orchestrator; no root files are edited here.

## Affected Repositories
- `qa-mcp`

## Change Set
- `team-bridge-bootstrap-token-client`
- `team-bridge-bootstrap-registration-evidence`

## Verify
- offline grant parser/replay/expiry/revoke/redaction tests
- live Linux-manager/Windows-host registration and heartbeat smoke under the
  component runtime preflight, with exact process cleanup
- restart/refresh/per-user attribution assertions
- `openspec validate --all --strict`; `git diff --check`

## Related
- root `openspec/board/2.todo/f5-40-team-git-onboarding-contract.md`
- root `openspec/board/2.todo/f5-50-team-workstation-onboarding.md`
- root `openspec/changes/f5-40-c10-team-git-onboarding-contract/`

## Result
Implemented both owning changes against root contract version `1` pinned at
`5afed8cf668e0c9bdbb44a1d167470e9b58295e5`. The Windows host-agent now
supports protected one-time bootstrap, strict source/binding/digest/expiry
validation, fail-closed refresh/restart state and unchanged mutually exclusive
explicit-token mode. The installer keeps credentials out of task argv and
protects the grant, Git authorization, atomic state and staged executable.

Offline verification passed the full 839-test non-live Python suite, focused
installer/smoke/artifact tests, Go tests/vet/race, Windows cross-compile and
strict OpenSpec validation. Final artifact SHA-256 is
`0f4b7fd1b2dcc44b0d48a515fc355a680f7f8b484c7811711311531d8abb2e81`.

Supervised final-artifact evidence on authorized workstation
`HISTORICAL-LAB-HOST` proved 8
fresh one-time registrations, stable `developer-a` / `team/demo10413` /
`team-server-primary` attribution, protected state after atomic refresh,
scheduled-task restart (`3128` -> `19876`), a read-only 12-window probe and
exact cleanup. Retained summaries contain only identifiers, status, counts and
digests; generated raw credential fixtures were removed after the run.

Independent review cycle 2 returned GO with R1-R4 closed and all five
acceptance criteria passing. Reviewed payload commit:
`4d2318704491c4e13789d987818a07a99213e0fe`; the final card-only amend is
published on `origin/main`.

## Next
- root may consume the pinned component artifact and redacted lifecycle
  evidence in the workstation onboarding E2E slice

## Change 1: `team-bridge-bootstrap-token-client`

### Why
Manual bridge tokens violate the target member flow and leak risk into prompts.

### Goal
Redeem a bound short-lived onboarding grant into protected bridge registration
state with fail-closed replay/expiry/revoke behavior.

### Scope
- Grant input/reference handling and server exchange client.
- Protected Windows state and explicit-token compatibility.
- Negative/redaction tests independent of live 1C runtime.

### Acceptance
- Valid grant registers once without revealing long-lived secrets.
- Invalid grant classes fail closed and leave no partial usable state.

### Depends On
- root `f5-40-c10-team-git-onboarding-contract`

### Related
- `openspec/changes/archive/2026-07-22-team-bridge-bootstrap-token-client/`

## Change 2: `team-bridge-bootstrap-registration-evidence`

### Why
Root onboarding needs proof that redeemed identity survives registration,
heartbeat, restart and provider/QA use.

### Goal
Extend registration evidence/smoke to cover bootstrap redemption, refresh,
per-user attribution and exact cleanup without secret-bearing captures.

### Scope
- Component runtime preflight, bridge lifecycle smoke and evidence summary.
- Failure recovery/restart and explicit process ownership cleanup.
- No business-data mutation beyond approved safe probes.

### Acceptance
- Live smoke proves correct user/project attribution after restart/refresh.
- Retained evidence contains only ids/status/digests and cleanup is complete.

### Depends On
- `team-bridge-bootstrap-token-client`

### Related
- `openspec/changes/archive/2026-07-22-team-bridge-bootstrap-registration-evidence/`

## Log
- 2026-07-20 accepted as the qa-mcp owning slice of the root release/bootstrap roadmap.
- 2026-07-22T05:38:06Z delivery started from clean `main` at `796e260`; root contract dependency is published at `5afed8c` and `license-activation-bootstrap` remains unrelated.
- 2026-07-22T06:46:21Z implementation and final Windows restart/refresh smoke passed; exact owned task, processes, paths, agent port and reverse tunnel were cleaned.
- 2026-07-22T06:48:00Z both delta specs synced to main specifications and both completed changes archived under `openspec/changes/archive/2026-07-22-*`.
- 2026-07-22T07:00:00Z independent review cycle 1 returned NO-GO (R1-R4): manifest closure, root-compatible Authorization schemes, Windows DACL enforcement and bounded negative coverage required correction.
- 2026-07-22T07:41:52Z rescue verification closed R1-R4 with manifest closure, Basic/Bearer/token compatibility, native Windows protected-DACL enforcement, expanded fail-closed tests and an exact-artifact Windows restart/refresh lifecycle; all owned remote and local credential fixtures were cleaned.
- 2026-07-22T07:54:00Z independent review cycle 2 returned GO; scoped reviewed payload committed as `4d2318704491c4e13789d987818a07a99213e0fe` and the card was finalized for `origin/main`.
