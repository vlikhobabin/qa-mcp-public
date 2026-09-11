# Designer metadata-dump in diagnostics can hang and orphan a 1cv8 process

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived. **P3** robustness. Under epic 111.

## Source
- `docs/qa-mcp-connection-issues-2.md` finding **#14**. Real-base test 2026-07-07.

## Problem
An attempt to resolve a catalog name via Designer mode
(`DESIGNER /F"…\private-lab-infobase" /N"Админ" /P"" /DumpConfigToFiles …`) **timed out and
left an extra `1cv8.exe DESIGNER …` process running**, which had to be stopped
manually. Metadata-dump in ordinary connection diagnostics makes the infobase
state more confusing and makes it harder to tell which `1cv8.exe` is the active
test client.

## Scope
1. **Do not run Designer metadata dump as part of ordinary connection
   diagnostics** — resolve metadata/catalog names by a lighter path (descriptor /
   host-side introspection / COM) instead.
2. **If a Designer/heavy platform op is ever used**, run it through the
   host-agent with a hard timeout + guaranteed process cleanup, and report the
   spawned PID(s) so orphans are visible and killable.

## Acceptance
- Connection diagnostics never spawn a Designer process.
- Any host-side platform op that can hang enforces a timeout and cleans up /
  reports its PID; no orphaned `1cv8.exe DESIGNER` after a failed/timed-out run.

## Change Set
- `designer-dump-timeout-cleanup` - `openspec/changes/archive/2026-07-07-designer-dump-timeout-cleanup/`

## Change 1: `designer-dump-timeout-cleanup`

### Why
Ordinary connection diagnostics must not make the Windows/model-B state harder
to reason about by spawning a heavy Designer metadata dump that can hang.

### Goal
Make diagnostics Designer-free by contract, and make explicit host-agent
platform timeout/cancel failures report the spawned PID while keeping process
group cleanup.

### Scope
- Python doctor/diagnostic guidance and tests.
- Windows host-agent `/platform/execute` timeout/cancel response shape and tests.
- OpenSpec endpoint and host-agent security specs.
- Documentation for safe connection troubleshooting.

### Acceptance
- `qa_mcp_doctor` / `qa-mcp-doctor` diagnostics do not call Designer or
  `/DumpConfigToFiles`.
- `/platform/execute` timeout/cancel responses include spawned PID data and
  still clean up through the existing process-group path.
- Existing platform allowlist, mutation-class, operator-intent and redaction
  checks keep passing.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-07-designer-dump-timeout-cleanup/`

### Notes For `$openspec-ff-change`
- Modify `qa-mcp-tool-endpoint-contract` and
  `qa-mcp-windows-host-agent-security`.
- Keep live Windows Designer smoke as a deferred runtime checkpoint in this
  Linux workspace.

## Related
- `docs/qa-mcp-connection-issues-2.md` (#14), epic 111.
- host-agent `platform_exec.go` (timeout/cleanup), `process_group_windows.go`.
- `openspec/changes/archive/2026-07-07-designer-dump-timeout-cleanup/`
- this publish commit

## Verify
- `python3 -m py_compile src/qa_mcp/doctor.py tests/test_doctor.py` passed.
- `uv run --with pytest --with pyyaml pytest tests/test_doctor.py -q` passed (`9 passed`).
- `go test ./...` passed under `host-agent/windows-display-agent`.
- `env GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-designer-dump-timeout-cleanup.test.exe .` passed.
- `openspec validate designer-dump-timeout-cleanup --strict` passed.
- `git diff --check` passed.
- Matrix preflight and archive gate passed with retained output under `.artifacts/openspec/designer-dump-timeout-cleanup/20260707T205910Z/`.
- Full suite gate passed: full pytest, canonical suite drift helper, and smoke pytest marker gate. The component-local `scripts/check_suite_source_of_truth_drift.py` route is absent, so the canonical agent-core helper was used.

## Archive
- `openspec/changes/archive/2026-07-07-designer-dump-timeout-cleanup/`

## Result
- Delivered Designer-free connection diagnostics contract in Python doctor output and docs.
- `/platform/execute` now reports spawned PID data on success and timeout/cancel errors while preserving process-group cleanup, redaction, allowlist, mutation-class and operator-intent behavior.
- Deferred real Windows Designer timeout smoke as a runtime checkpoint because this Linux workspace has no attached Windows desktop or licensed Windows 1C platform.

## Next
- none

## Log
- 2026-07-07 filed from #14.
- 2026-07-07T20:57:25Z `$opsx-ff` created `designer-dump-timeout-cleanup` artifacts and moved card to `2.todo`.
- 2026-07-07T20:57:25Z `$opsx-do` started implementation and moved card to `3.inprogress`.
- 2026-07-07T21:08:17Z `$opsx-do` implemented, verified, synced specs, archived `designer-dump-timeout-cleanup`, and moved card to `4.done`.
- 2026-07-07T21:13:24Z `$opsx-pub` committed this card (`feat(qa-mcp): harden designer-free diagnostics`).
