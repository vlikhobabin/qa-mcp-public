# S50-120: Bind remote UI actions to lifecycle window identity

## Status
4.done

## Order Index
120

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Root tracker: `/opt/ai-dev-suite-for-1c/openspec/board/1.backlog/s50-finans-extension-e2e-120-bind-remote-ui-actions-to-testclient-hwnd.md`
- Prerequisite: `openspec/board/4.done/remote-testclient-owned-lifecycle.md`
- Follow-up from S50 Finans extension E2E.

## Summary
Remote display actions must be scoped to the exact TestClient lifecycle/client
identity instead of depending on a non-empty 1C window title or wildcard
foreground selection. Screenshot, key, type, click and visible-list-cell routes
must fail closed rather than act on an unrelated foreground application.

## Acceptance Criteria
- [x] Launch or attach output exposes enough lifecycle/client identity for
  remote display primitives to target the owned TestClient window.
- [x] `capture_screenshot`, `send_keys`, `type_text`, `click` and visible-list
  reads send a lifecycle/client target when no explicit window is supplied.
- [x] Explicit window selectors still win over lifecycle/client targeting.
- [x] Empty-title TestClient windows are targetable without caption matching.
- [x] Wildcard/empty targeting cannot capture or mutate an unrelated foreground
  application when an owned TestClient context is active.
- [x] Locked, disconnected or non-interactive Windows sessions produce typed
  diagnostics suitable for MCP responses.
- [x] Captured evidence remains in ignored runtime paths only.

## Evidence Boundary
Retain only sanitized booleans, typed diagnostics and test outcomes. Do not
commit raw screenshots, HWND values, process identifiers, titles, credentials or
host-agent logs.

## Change Set
- `bind-remote-ui-actions-to-lifecycle-window`:
  `openspec/changes/archive/2026-08-01-bind-remote-ui-actions-to-lifecycle-window/`

## Change 1: `bind-remote-ui-actions-to-lifecycle-window`

### Why
The active TestClient lifecycle already identifies the remote client, but the
display routes do not consume that identity and can fall back to a weak window
or foreground selection.

### Goal
Bind every implicit remote display request to the exact active TestClient
lifecycle/client identity and return typed fail-closed diagnostics when that
target or its interactive Windows desktop is unavailable.

### Scope
- Python MCP active-attachment and remote display-backend target propagation.
- Windows host-agent lifecycle/PID/TPort validation, empty-title window
  resolution, capability/version contract and desktop-session diagnostics.
- Focused Python/Go regressions, Windows-native integration evidence and
  durable host-agent/tool documentation.
- No native TestClient wire-protocol changes, 1C metadata/BSL changes,
  business-data mutation or reviewed screenshot artifacts.

### Acceptance
- As in the card Acceptance Criteria.

### Depends On
- `remote-testclient-owned-lifecycle` (archived and published).

### Related
- `openspec/changes/archive/2026-08-01-bind-remote-ui-actions-to-lifecycle-window/`
- `openspec/changes/archive/2026-08-01-bind-remote-ui-actions-to-lifecycle-window/design.md`

## Verify
- Focused Python lifecycle-target suite: `5 passed`; the tests intercept the
  five outgoing display requests and prove target presence, explicit omission,
  capability refusal before POST, owned launch attachment and non-owning attach
  attachment.
- Review-cycle-1 rescue suite: `5 failed` before the fix and `5 passed` after.
  The tests drive the real MCP visible-list diagnostic with empty/wildcard
  configuration and prove missing/invalid active targets stop before POST.
- Complete display/MCP regression set: `198 passed`.
- Full offline Python coverage gate: `905 passed`, `71.78%` coverage against the
  required `60%` floor.
- `go test -count=1 ./...`: passed. The handler tests observe the exact resolved
  selector for all five routes and prove refusal happens before driver calls.
- `GOOS=windows GOARCH=amd64 go test -c`: passed; the ignored artifact is a
  PE32+ x86-64 Windows test binary.
- `openspec validate bind-remote-ui-actions-to-lifecycle-window --strict`:
  passed before archive. Post-archive `openspec validate --all --strict`:
  `20 passed, 0 failed`.
- Windows preflight resumed green against the authorized architect workstation:
  SSH and ICMP reached `HISTORICAL-LAB-HOST`, an interactive user session was
  present, and the temporary source-bound loopback route matched the local
  host-agent, native-test and owned-fixture hashes.
- S50-120A proved the `type_text` blocker was legacy proof-client parsing: an
  invalid-target control preserved HTTP `422` but lost the typed code, while the
  bounded reader recovered `invalid-client-target`; the real type route then
  passed `200/2xx` with both owned processes live.
- S50-120B completed the source-bound rerun: screenshot, key, type, click,
  visible-list cells, explicit override, unrelated-foreground isolation,
  weak-target refusal and typed-session native tests all passed. The exact
  empty-title target returned the owned accessible `VisibleCell` marker.
- Every attempt stopped its exact owned processes and removed its screenshot,
  token and logs. Final controller cleanup confirmed no owned process, exact
  scheduled task or remote stage remained.
- Sanitized ignored summaries:
  `.runtime/changerail/evidence/bind-remote-ui-actions-to-lifecycle-window/{preflight,offline-verification,windows-proof-20260801T052014Z,windows-proof-20260801T064500Z-resume,remote-cleanup-20260801T052014Z}.json`.
  Investigation evidence is under
  `.runtime/changerail/evidence/investigate-windows-display-type-transport-proof/`.
  Failed attempts are retained beside them as sanitized ignored JSON.
  The concrete matrix remains in the change `design.md` and follows
  `/opt/ai-dev-suite-for-1c/docs/dev-mcp-suite-opsx-runtime-verification.md`.

## Archive
- `openspec/changes/archive/2026-08-01-bind-remote-ui-actions-to-lifecycle-window/`

## Related
- Root tracker: `/opt/ai-dev-suite-for-1c/openspec/board/1.backlog/s50-finans-extension-e2e-120-bind-remote-ui-actions-to-testclient-hwnd.md`
- Prerequisite card: `openspec/board/4.done/remote-testclient-owned-lifecycle.md`
- Runtime verification standard: `/opt/ai-dev-suite-for-1c/docs/dev-mcp-suite-opsx-runtime-verification.md`
- OpenSpec change: `openspec/changes/archive/2026-08-01-bind-remote-ui-actions-to-lifecycle-window/`
- Investigation card: `openspec/board/4.done/s50-120a-investigate-windows-display-type-transport.md`
- Product-fix card: `openspec/board/4.done/s50-120b-fix-windows-visible-list-cell-runtime.md`

## Result
Implementation, offline verification, the source-bound Windows matrix, spec
sync and OpenSpec archive are complete. The reviewed payload is ready for the
second independent ChangeRail review cycle after the cycle-1 blockers were
reproduced and fixed.

Published reviewed payload as `618c8f509d492e00ab1294ce388ada4b86cdc582`; push status `pending` on `main`/`origin`.

## Next
- done

## Log
- 2026-07-31 ChangeRail fast-forward decomposed the story into one coherent
  lifecycle-window targeting change and created apply-ready proposal, design,
  delta specs and verification tasks.
- 2026-07-31 ChangeRail delivery implemented lifecycle-bound targeting and
  completed all offline gates, then stopped at the required Windows runtime
  verification gate after repeated preflight timeouts. No Windows action ran.
- 2026-08-01 ChangeRail resume reached and identified the authorized Windows
  host, ran three source-bound owned-fixture attempts, retained only sanitized
  results, completed exact cleanup, and stopped after the pre-review fix budget
  plus one bounded continuation were exhausted at the `type_text` transport
  boundary. A linked investigation card was placed next.
- 2026-08-01 S50-120A proved the type blocker was a proof-client parser defect,
  repaired that ignored boundary, completed every other matrix row and exact
  cleanup, and created S50-120B for the remaining exact-target visible-cell
  invariant.
- 2026-08-01 S50-120B supplied the green source-bound visible-cell and complete
  route/session/cleanup matrix. ChangeRail resumed, reran all local gates,
  synced the three capability deltas and archived the completed change for
  independent review.
- 2026-08-01 independent review cycle 1 returned `no-go`: the MCP visible-list
  diagnostic invented an explicit class selector, and active contexts without
  a client target could downgrade to TPort-only routing. A bounded same-card
  rescue added five failing branch-sensitive tests, fixed both paths, and
  reran the full verification floor green for review cycle 2.
- 2026-08-01T08:13:33Z publish finalized card into `4.done` with commit `618c8f509d492e00ab1294ce388ada4b86cdc582` and push status `pending`.
