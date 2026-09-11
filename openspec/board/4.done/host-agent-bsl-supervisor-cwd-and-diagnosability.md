# G14: harden the workstation host-agent launch and compatibility contract

## Status
4.done — both ordered changes are implemented, verified, synced, archived and
independently GO-reviewed; scoped publication completed.

## OpenSpec Stage
archived, independently reviewed and published

## Owner
qa-mcp host-agent/runtime. Root owns the thin-workstation manifest and runbook
consumer update; bsl-mcp owns only the native helper contract.

## Problem
On the T4 stand the supervised `bsl-agent.exe workstation serve` crashlooped (state=backoff,
restart_count climbing ~1/sec) and never reached `ready`, even though the identical args launched
by hand (via a `.bat`) reached `ready`. Two host-agent-side defects made this happen and made it
nearly undiagnosable:

1. **Inherited service CWD.** The host-agent runs under a Windows scheduled task / service whose CWD
   is `C:\Windows\System32`. The supervisor launched the bsl-agent child with that CWD. bsl-agent
   creates its log dir (`.bsl-agent/`) **relative to CWD** → `create log directory
   C:\Windows\System32\.bsl-agent` → **os error 5 (access denied)** → immediate exit, before it can
   open its own log. (Confirmed by capturing the child stderr.)
2. **Swallowed child stderr.** `run()` set neither `cmd.Stdout` nor `cmd.Stderr`, so the child's
   fatal message went nowhere; `/health` only reported `state=backoff` with no cause. This turned a
   one-line permission error into a multi-hour investigation.

Also required (config/launcher side, not host-agent code): the launcher must pass
`--bsl-platform-version`, `--bsl-syntax-helper-dir`, `--bsl-configuration-path`, and the supervisor
startup timeout must cover the cold warmup (~6 min ≫ the 60s default) — otherwise the supervisor
kills the helper mid-warmup and crashloops.

## Stand-proven checkpoint
`host-agent/windows-display-agent/bsl_supervisor.go` `run()`:
- Set `cmd.Dir = filepath.Dir(s.config.Binary)` (a writable dir the operator staged the binary in),
  so bsl-agent's CWD-relative log/cache dirs are writable regardless of the host-agent's service CWD.
- Env-gated child stderr/stdout capture: if `QA_MCP_BSL_CHILD_LOG` is set, redirect the child's
  output to that file (diagnosability; off by default).
- Dropped `hideChildWindow` (CREATE_NO_WINDOW) for the bsl child (investigated as a suspect; not the
  root cause, but the child inherits the host-agent's already-hidden console, so no window surfaces).

**Proven:** with `cmd.Dir` writable + the launcher passing platform-version/syntax-helper-dir/
configuration-path + `-bsl-startup-timeout 480s` + `BSL_CACHE_DIR=<writable>`, bsl-agent reached
`state=ready restart=0 version=0.4.170` under the supervisor on station A (.205).

## Change 1: `harden-bsl-supervisor-launch`

Adopt the checkpointed CWD fix and complete the actual Windows scheduled-task
product path: explicit helper flags/cache/log, a cold-warmup-safe timeout and
task restart-on-failure.

Критерии приёмки:
- [x] AC1.1 Root cause captured from child stderr: inherited
      `C:\Windows\System32` made `.bsl-agent` creation fail with os error 5.
- [x] AC1.2 An offline fake helper launched while the parent is in a simulated
      service CWD observes the helper-binary directory as its CWD and reaches
      `ready`.
- [x] AC1.3 A fake helper that exits early writes a bounded diagnostic to the
      configured child log; repeated restarts do not retain open log handles.
- [x] AC1.4 The default startup timeout is at least 480 seconds. The installer
      passes configuration path, syntax-helper dir, platform version, writable
      cache and child-log paths, and the scheduled task restarts on failure.
- [x] AC1.5 `go test ./...`, `go vet ./...`, qa-mcp focused Python tests,
      ChangeRail verification and strict OpenSpec validation pass.

## Change 2: `decouple-host-agent-version-compatibility`

Replace the recurring exact build-label allowlist gate with an explicit display
protocol contract. Preserve exact operator pins and legacy known-good builds.

Критерии приёмки:
- [x] AC2.1 `/version` advertises a stable display protocol id independent of
      the host-agent build label.
- [x] AC2.2 A newer/unknown build with the supported protocol is accepted by
      default; an unsupported/missing protocol on an unknown build fails closed.
- [x] AC2.3 Explicit `QA_MCP_HOST_AGENT_EXPECTED_VERSION` and SHA-256 pins stay
      exact.
- [x] AC2.4 Doctor reports bounded `version_relationship`, build version and
      display protocol without secrets.
- [x] AC2.5 The pre-existing forward-compat satellite card is recorded as
      absorbed, and regression tests cover the shipped-image + newer-agent case.

## Related
- Root T4 (M5); bsl-mcp `bsl-agent-native-crash-windows-workstation-serve.md`; contract
  `ai1c.bsl-agent-workstation-supervision.v1`; thin-workstation install renderer/docs.
- Absorbs `host-agent-display-bridge-version-forward-compat.md`.

## Result
Checkpoint `4476585` is now protected by offline service-CWD and early-stderr
regressions. The installer renders the complete BSL launch, rejects cold-start
timeouts below 480 seconds and gives the scheduled task a bounded restart
policy. Display compatibility is keyed to
`ai1c.windows-host-display-http.v1`; explicit version/SHA pins remain exact and
doctor reports the relationship. Focused Python tests passed 53/53, full
non-live Python gate passed 811 tests at 70.63% coverage, Go tests/vet and the
Windows cross-compile passed. Independent review cycle 1 returned GO for all
10 AC and exact 29-path scope. Its one non-blocking test-adequacy finding is
retained for the final Windows T4 rerun: Linux cannot execute Pester/Task
Scheduler or prove Windows handle semantics, so the rebuilt installer must be
exercised on both stations before the root product gate closes.

## Next
Update and publish the root thin-workstation manifest/runbook consumer, then
exercise the rebuilt installer and child-log/task durability on both Windows
stations during the final T4 gate.

## Log
- 2026-07-13 diagnosed on the T4 stand (captured supervised child stderr), fixed `bsl_supervisor.go`
  (cmd.Dir + env-gated child-log + no-window drop), proved bsl-agent `ready` under supervision, M5 unblocked.
- 2026-07-13 `$changerail-ff`: checkpoint adopted; decomposed into supervisor
  launch/durability and protocol compatibility changes with offline evidence
  requirements.
- 2026-07-13T13:47:29Z `$changerail-do`: both changes implemented; focused
  Python 53/53, full non-live Python 811/811 with 70.63% coverage, Go test/vet
  and Windows cross-compile passed; specs synced and changes archived.
- 2026-07-13T13:59:30Z independent review cycle 1 returned GO (10/10 AC,
  exact 29/29 paths, all gates reproduced); one non-blocking Windows-only test
  adequacy finding is explicitly routed to the final physical T4 rerun.
