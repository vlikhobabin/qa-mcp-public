# Fix Windows TestClient launch and solo read regression

## Status

4.done

## Owner

unassigned

## OpenSpec Stage

archived

## Problem

The final T4 solo regression initialized all nine MCP providers and passed the
license gate, but QA could not complete its required live read on `.201`:

- product `launch_test_client` failed with
  `testclient-interactive-session-unavailable` because `WTSQueryUserToken`
  lacked the required privilege;
- the first transient InteractiveToken-task implementation launched
  8.3.27.2130, but real M9 proved that scheduler task release/completion kills
  the child job before durable TPort readiness;
- the authenticated loopback relay is ready, but cannot be credited until a
  durable product launch reaches attach/descriptor/grid.
- the T4 operators observed visible BSL/helper console windows stealing focus;
  `.201` also showed an owned stale-listener restart loop on the one-second
  supervisor backoff.

## Scope

- Make host-agent launch work from the delivered scheduled-task security
  context, or select a supported launch mechanism that does not require an
  unavailable privilege.
- Reproduce and fix the attached Windows TestClient protocol reset on the
  published thin image and supported 8.3.27 client.
- Retain launch, attach, descriptor and non-empty grid evidence without window
  title/customer-data leakage.

## Evidence

- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T162024Z-final-gate/matrix/M09/solo-regression.json`
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T162024Z-final-gate/matrix/M09/manual-attach-diagnostic.json`
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/matrix/M09/solo-regression.json`

## Acceptance

- Product launch produces a listening TestClient in the active Windows session
  from the installed host-agent task.
- `attach_test_client`, `read_form_descriptor` and `read_list_grid` return a
  non-empty `Валюты` result through the solo gateway on a clean rerun.
- The TestClient is removed by owning cleanup, and no per-launch task/wrapper
  artifacts remain after launch.

## Change Set

1. `windows-testclient-interactive-task-launch`
2. `windows-testclient-authenticated-loopback-relay`
3. `windows-host-agent-windowless-helper-lifecycle`
4. `windows-testclient-relay-listener-only-readiness`
5. `windows-testclient-launch-fail-closed-cleanup`
6. `windows-testclient-task-cleanup-runtime-proof`

## Verify

- focused Go launch/relay tests and Windows cross-build
- focused Python transport/lifecycle/tool tests
- full offline Python and Go suites
- root T4 M9 launch → attach → descriptor → non-empty `Валюты` grid proof
- strict OpenSpec validation, secret scan and `git diff --check`

## Archive

- `openspec/changes/archive/2026-07-14-windows-testclient-interactive-task-launch/`
- `openspec/changes/archive/2026-07-14-windows-testclient-authenticated-loopback-relay/`
- `openspec/changes/archive/2026-07-14-windows-host-agent-windowless-helper-lifecycle/`
- `openspec/changes/archive/2026-07-14-windows-testclient-relay-listener-only-readiness/`
- `openspec/changes/archive/2026-07-14-windows-testclient-launch-fail-closed-cleanup/`
- `openspec/changes/archive/2026-07-14-windows-testclient-task-cleanup-runtime-proof/`

## Result

The first independent ChangeRail review returned `no-go`: generic
`port_is_listening` still authenticated the relay and opened the
single-manager target, and M9 did not retain the source-bound digest of the
binary under test. Changes 1-3 remain delivered and archived. Change 4 fixes
the readiness isolation defect; the root-owned rerun now retains exact artifact
binding for the new independent review.

The delivered source-bound 0.1.7 host-agent launches through the authenticated
transient task shell broker, routes protocol through the fixed-target relay and
keeps display targeting on the real TPort. Final M9 returned a 46-element form
descriptor and 20-row `Валюты` grid; the same PID/TPort/window remained live
for 62.662 seconds with zero transient task/artifact. Both stations retained
one ready BSL helper, restart_count=0 and visible console count=0.
The exact artifact SHA matches the retained source manifest, both bootstrap
rows and both runtime process inventories with no mismatch.
The final evidence index records M9 as `pass`, and `verdict.json` records
`release_ready` with no blocking row or check:

- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/evidence-index.json`
- `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260714T114204Z-source-bound-release-ready-rerun/verdict.json`

The next independent review found two fail-closed gaps: an empty requested
platform version could select the newest installed build, and request
cancellation could kill the registration PowerShell before its `finally`
removed the transient task. Change 5 requires the exact four-component version
and adds Go-owned exact-name unregister on a fresh 15-second background context
before every post-registration return, with a deferred unexpected-return
retry. Explicit cleanup failure is returned as an error. The full Python suite
has 833 passing tests; native Go tests and the Windows test cross-build pass.

The following independent review verified those source changes but returned
no-go because the retained Windows artifact still had source fingerprint
`622c96dc...`, not the current cleanup source. Change 6 connects explicit and
deferred cleanup through a behavioral guard, adds an AST production-call-site
contract, and retains a Windows-native cancel/failure/fallback proof from
source fingerprint `63e8d407...`. The same artifact SHA `9c5e61ea...` completed
a real normal TestClient launch with exact PID/window immediately and after 62
seconds; all proof resources were removed and the immutable T4 baseline
comparison returned `ok`:

- `../.artifacts/openspec/windows-testclient-task-cleanup-runtime-proof/20260714T160743Z-current-source-bound-runtime-proof/runtime-proof-summary.json`
- `../.artifacts/openspec/windows-testclient-task-cleanup-runtime-proof/20260714T160743Z-current-source-bound-runtime-proof/windows-runtime/windows-cleanup-integration.summary.json`
- `../.artifacts/openspec/windows-testclient-task-cleanup-runtime-proof/20260714T160743Z-current-source-bound-runtime-proof/windows-runtime/current-host-agent-normal-launch.summary.json`

Published reviewed payload as `e53053b48a0f2d977f49d7193aa9bcaaaa0e1446`; push status `pending` on `main`/`origin`.

## Next

- done

## Change 1: `windows-testclient-interactive-task-launch`

### Why

`WTSQueryUserToken` needs `SeTcbPrivilege`, and even SYSTEM
`CreateProcessAsUserW` produced a client that exited before TPort. A transient
InteractiveToken task could start the same command, but live M9 proved its
child is terminated with the scheduler job when the task completes or is
released. The installed host-agent itself already owns a durable
Limited/Interactive active-session context.

### Goal

Launch the product-owned TestClient through the interactive Windows shell after
verifying the active-console session of the installed Limited/Interactive
host-agent.

### Scope

- Verify the host-agent session matches the active console session, then pass
  the exact executable/one-string argv over an authenticated ephemeral loopback
  exchange to a fixed hidden InteractiveToken task broker using
  `Shell.Application.ShellExecute`.
- Put no credential in task metadata; remove the task before response and
  create no wrapper/PID handoff file.
- Resolve the requested TPort listener owner and reopen that actual 1cv8 process
  handle for ownership/readiness monitoring; fail closed on session mismatch
  or process-creation failure.
- Keep the non-Windows direct-exec path unchanged.

### Acceptance

- Normal Limited/Interactive host-agent principal launches without
  `WTSQueryUserToken` or `SeTcbPrivilege`.
- PID, TPort and window persist at the immediate and >=60-second probes.
- Readiness and early-exit diagnostics remain honest and secret-safe.

### Related

- `openspec/changes/archive/2026-07-14-windows-testclient-interactive-task-launch/`
- supersedes
  `openspec/board/5.canceled/host-agent-testclient-persistence-interactive-launch-mechanism.md`

## Change 2: `windows-testclient-authenticated-loopback-relay`

### Why

The T4 qa provider runs on the Linux team server, so a direct LAN connection to
the Windows TPort receives the known `66 53 b2 a6` + EOF rejection. A local
Windows-origin connection is required for the full manager handshake.

### Goal

Route protocol sessions through an opt-in authenticated host-agent TCP relay
that validates the existing bridge secret and dials only the fixed loopback
TestClient port.

### Scope

- Add an opt-in relay listener with a bounded token preface, constant-time auth,
  one active TestManager session and fixed `127.0.0.1:<TPort>` target.
- Add a shared Python TestClient connector so every lifecycle/session/replay
  path uses the relay preface only for the configured relay endpoint.
- Keep host-agent display/window targeting on the real local TestClient TPort
  instead of the relay listener port.
- Keep solo/local direct TCP unchanged when relay configuration is absent.
- Wire compose/root T4 to the relay endpoint without emitting its token.

### Acceptance

- Unauthenticated, wrong-token, oversized-preface and concurrent connections
  fail before a loopback target is opened.
- The authenticated route transparently carries a binary protocol session and
  does not permit caller-selected target addresses.
- Root T4 M9 returns a non-empty `Валюты` descriptor/grid through the solo
  gateway and retains only sanitized evidence.

### Related

- `openspec/changes/archive/2026-07-14-windows-testclient-authenticated-loopback-relay/`
- `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/`

## Change 3: `windows-host-agent-windowless-helper-lifecycle`

### Why

Real T4 use exposed a persistent `bsl-agent.exe` console and one-second helper
console flashes that took focus from both workstation operators. Process-group
configuration discarded existing no-window flags, while BSL relied on an
implicit inherited-console assumption. A stale owned BSL listener on `.201`
made that child restart every second.

### Goal

Run all installed host-agent background helpers without visible consoles or
focus steal, and reconcile only a stale installer-owned BSL process during
artifact replacement.

### Scope

- Preserve no-window flags when applying Windows process-group ownership.
- Give the BSL helper its required console semantics with a hidden initial
  window.
- Stop a stale BSL process only by exact staged executable path during install.
- Prove healthy stable supervision and no helper console windows on both T4
  stations before resuming M9.

### Acceptance

- No persistent or flashing background helper console is visible on `.201` or
  `.205`.
- BSL readiness remains green with stable restart count.
- Reinstall does not terminate an unrelated same-name process.

### Related

- `openspec/changes/archive/2026-07-14-windows-host-agent-windowless-helper-lifecycle/`

## Change 4: `windows-testclient-relay-listener-only-readiness`

### Why

Independent review found that the generic lifecycle liveness probe used the
authenticated connector. On the configured relay endpoint that opens and then
immediately discards the fixed single-manager target, racing the next real
descriptor/read session.

### Goal

Make every generic relay readiness/status probe listener-only while preserving
authenticated target access for actual protocol sessions.

### Scope

- Detect the exact configured relay endpoint in the shared lifecycle probe.
- Use TCP-only relay listener reachability for readiness/status/info/state
  checks without sending the authentication preface.
- Keep direct endpoints and real protocol sessions on the existing connector.
- Add focused negative tests that fail if public status paths authenticate or
  dial the relay target.

### Acceptance

- Generic liveness probes against the relay endpoint send no authentication
  preface and do not open its target.
- `test_client_status`, `infobase_info` and `get_state` inherit the safe probe.
- Real descriptor/read sessions continue to authenticate through the relay.

### Related

- `openspec/changes/archive/2026-07-14-windows-testclient-relay-listener-only-readiness/`

## Change 5: `windows-testclient-launch-fail-closed-cleanup`

### Goal

Bind every product launch to a non-empty exact platform version and make
transient scheduled-task cleanup independent from request cancellation while
remaining exact-name and fail-closed.

### Related

- `openspec/changes/archive/2026-07-14-windows-testclient-launch-fail-closed-cleanup/`
- `openspec/board/3.inprogress/windows-host-agent-atomic-release-delivery.md`

## Change 6: `windows-testclient-task-cleanup-runtime-proof`

### Goal

Keep both production cleanup call sites mechanically enforced and retain a
current source-bound Windows cancel/failure/fallback plus normal-launch proof.

### Related

- `openspec/changes/archive/2026-07-14-windows-testclient-task-cleanup-runtime-proof/`
- `openspec/board/3.inprogress/windows-host-agent-atomic-release-delivery.md`

## Log

- 2026-07-13 accepted from final T4 M9 evidence and decomposed into persistent
  interactive launch plus authenticated loopback relay changes.
- 2026-07-13 local implementation, full offline verification, Windows artifact
  installation and protected-image build completed; real M9 proof pending.
- 2026-07-14 T4 paused after operator-visible console/focus-steal regression;
  change 3 added and both station tasks stopped pending windowless proof.
- 2026-07-14 final M9 passed launch/attach/descriptor/grid/61.833-second
  stability, Help search and two-station windowless-helper proof; all three
  changes synced and archived, awaiting independent review.
- 2026-07-14 independent review returned no-go on generic relay readiness and
  missing final source-bound M9 digest; Change 4 opened for the owner-local fix.
- 2026-07-14 Change 4 passed 831 Python tests, native Go tests, Windows GUI
  cross-build, focused relay tests and strict OpenSpec validation; synced and
  archived for the source-bound rerun.
- 2026-07-14 the next review returned no-go on empty-version fallback,
  cancellation-sensitive task cleanup and split publication scope; Change 5
  passed RED/GREEN, 833 Python tests, native Go and Windows cross-build gates,
  then synced and archived. Atomic publication is delegated to the combined QA
  delivery card.
- 2026-07-14 review cycle 3 found the retained artifact predates the cleanup
  rescue and the helper-only test could survive removal of production call
  sites. Change 6 closed both gaps and retained exact Windows cleanup/baseline
  evidence; publication remains pending fresh review.
- 2026-07-14T19:09:40Z publish finalized card into `4.done` with commit `e53053b48a0f2d977f49d7193aa9bcaaaa0e1446` and push status `pending`.
