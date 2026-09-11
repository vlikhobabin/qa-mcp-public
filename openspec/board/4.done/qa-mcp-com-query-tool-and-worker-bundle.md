# Add a host-side COM read-query tool + bundle ai-com-worker.exe + a COMConnector doctor

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived. **P1 capability gap**. Under epic 111.

## Source
- `docs/qa-mcp-connection-issues-2.md` findings **#15, #4, #13, #16** — real-base
  test on [redacted third-party configuration] (file infobase, no OData), 8.3.27.2130, 2026-07-07.

## Problem
For a local **file** infobase without OData publishing, qa-mcp cannot answer a
simple data question ("how many rows in `Справочник.Валюты`") through its own
tool surface. The data tools (`assert_data`, `assert_data_count`,
`role_data_matrix`) are **OData-oriented** (`base_url`/`entity_set`) and return
`OData base_url not configured` for a file base. Meanwhile a read-only COM query
worked from the host after fixing registration:
```
ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК Qty ИЗ Справочник.Валюты  ->  Count=1
```
So the capability exists on the host but is not reachable through qa-mcp.

**The plumbing is ~80% built:** the host-agent already exposes
`/com/execute` (`host-agent/windows-display-agent/com_exec.go`) which shells out
to `ai-com-worker.exe`, and the suite already has that worker
(`live-mcp/src/finshtab_1c_live/com_worker_exe.py` + PyInstaller spec +
`build-com-worker-exe.sh`). Two gaps: (a) `ai-com-worker.exe` is **not bundled**
in the qa-mcp release, so host-agent `/health` reports
`com_worker: { available:false, error:"com-worker-not-found" }` (#4); (b) there
is **no qa-mcp MCP tool** that routes a COM read query to `/com/execute`.

Additionally (#13/#16): 64-bit `V83.COMConnector` registration is fragile — a
non-admin `regsvr32` leaves the TypeLib
(`{98AC3B5B-5323-418F-8F07-E32F231D2393}`) missing → `TYPE_E_LIBNOTREGISTERED
(0x8002801D)` on `Connect`, even though the ProgID + InprocServer32 exist. Fixed
only by **elevated** 64-bit `C:\Windows\System32\regsvr32.exe`.

## Scope
1. **Bundle `ai-com-worker.exe`** in the qa-mcp release (host-agent asset next to
   `qa-mcp-host-agent.exe`); `publish_self_hosted.sh` already has a
   `--com-worker-exe` flag (currently omitted → the WARNING in the report). Wire
   it into the standard build/publish + install.
2. **New read-only MCP tool** (e.g. `query_com` / `assert_com_count`) that runs
   on the host via host-agent `/com/execute` (NOT inside the container). Minimal
   schema: `infobase_path,user,password,query,timeout_sec` → `{ok,rows,transport:"com",platform,bitness}`.
   Read-only by default; reject obvious write ops unless explicitly enabled.
3. **`com_connector_doctor`** (#16) — checks bitness, elevation, platform roots,
   `V83.COMConnector` ProgID/CLSID/InprocServer32, TypeLib GUID + `win64` path, a
   real `CreateObject` + `Connect(<file ib>)` + a small read query; if TypeLib is
   missing, recommend elevated `System32\regsvr32.exe` (not SysWOW64). Note the
   observed quirk: PowerShell/.NET COM binding creates the connector but reading
   result fields is awkward; WSH/JScript late binding read reliably.
4. **`/health` clarity** (#4): classify `com_worker` absence as a feature-impact
   warning, not silently under `ok:true`; state which flows need it.

## Acceptance
- With the worker bundled, host-agent `/health` shows `com_worker.available:true`.
- `query_com`/`assert_com_count` on [redacted third-party configuration] returns `Qty=1` for
  `Справочник.Валюты` via host-side COM, read-only.
- `com_connector_doctor` reports TypeLib-missing with the exact elevated
  registration command, and green after registration.

## Change Set
- `qa-mcp-com-query-tool-and-worker-bundle` →
  `openspec/changes/archive/2026-07-07-qa-mcp-com-query-tool-and-worker-bundle/`

## Verify
- `uv run --with pytest --with pyyaml pytest` → 759 passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` → OK.
- `uv run --with pytest --with pyyaml pytest -m smoke` → 3 passed.
- `(cd host-agent/windows-display-agent && go test ./...)` → passed.
- `(cd host-agent/windows-display-agent && GOOS=windows GOARCH=amd64 go build ...)` → passed.
- `openspec validate qa-mcp-tool-endpoint-contract --strict` → passed.
- `openspec validate qa-mcp-self-hosted-release --strict` → passed.
- `openspec validate qa-mcp-windows-host-agent-security --strict` → passed.
- `openspec validate --all` → passed after archive.
- `git diff --check` → passed.
- Matrix evidence:
  `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/matrix-preflight.json`,
  `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/matrix-archive-gate.json`.

## Archive
- `openspec/changes/archive/2026-07-07-qa-mcp-com-query-tool-and-worker-bundle/`

## Result
Implemented, archived, and published by the OPSX commit on `main`. qa-mcp now
exposes host-side read-only COM query tools (`query_com`, `assert_com_count`)
and a `com_connector_doctor` MCP wrapper.
The Windows host-agent has an authenticated `/com/doctor` endpoint, clearer
`com_worker` health impact metadata, and Windows-only registry/JScript smoke
support. The release helper accepts `COM_WORKER_EXE` / `QA_MCP_COM_WORKER_EXE`
defaults for bundling `ai-com-worker.exe`, and docs explain the missing-worker
feature impact.

Retained provider gap: the real Windows BIT.FINANCE `Qty=1` COM live smoke was
not executed in this Linux workspace. See
`.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/windows-com-live-smoke-gap.json`.

## Next
- Run the retained Windows live-smoke follow-up on the BIT.FINANCE host when that
  operator environment is available.

## Change 1: `qa-mcp-com-query-tool-and-worker-bundle`

### Why
qa-mcp needs a host-side read-only COM data path for Windows file infobases
without OData, plus reliable worker bundling and COMConnector diagnostics.

### Goal
Expose `query_com`, `assert_com_count`, and `com_connector_doctor` through
qa-mcp while making the standard self-hosted release path bundle the ready
`ai-com-worker.exe` when supplied.

### Scope
- MCP tool wrappers and host-agent COM helper code.
- Windows host-agent `/com/doctor` diagnostics and health metadata.
- Self-hosted release default wiring and delivery docs.
- Offline Linux tests plus retained evidence; real Windows COM smoke is a
  recorded provider/environment gap for operator follow-up.

### Acceptance
- `query_com` routes a read-only query to host-agent `/com/execute` and returns
  structured COM rows.
- `assert_com_count` compares the first numeric COM result.
- Unsafe query text is rejected before host transport.
- `com_connector_doctor` reports TypeLib-missing repair guidance and supports a
  green read-smoke response from the host.
- Release default `COM_WORKER_EXE` stages `ai-com-worker.exe` unless an explicit
  CLI path overrides it.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-07-qa-mcp-com-query-tool-and-worker-bundle/`

### Notes For `$openspec-ff-change`
- Artifacts are complete; proceed to implementation.

## Related
- `docs/qa-mcp-connection-issues-2.md` (#4/#13/#15/#16), epic 111.
- host-agent `com_exec.go` (`/com/execute`); live-mcp `com_worker_exe.py`,
  `build-com-worker-exe.sh`; [[live-mcp-com-over-host-bridge]] /
  [[com-primary-e2e-phased-plan]] (COM worker already proven on historical-user).
- `tools/release/publish_self_hosted.sh` (`--com-worker-exe`).
- `openspec/changes/archive/2026-07-07-qa-mcp-com-query-tool-and-worker-bundle/`
- `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/com-query-offline-evidence.json`
- `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/release-health-evidence.json`
- `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/com-doctor-offline-evidence.json`
- `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/windows-com-live-smoke-gap.json`
- Publish commit: `feat(qa-mcp): add host-side COM query tools` on `main`.

## Log
- 2026-07-07 filed from the .205 real-base report; plumbing already exists in the
  host-agent + live-mcp — this is bundle + expose + doctor, not build-from-scratch.
- 2026-07-07T19:00:50Z OPSX ff: created apply-ready OpenSpec artifacts for
  `qa-mcp-com-query-tool-and-worker-bundle` and moved card to `2.todo`.
- 2026-07-07T19:00:50Z OPSX do: implementation started; matrix preflight passed.
- 2026-07-07T19:00:50Z OPSX do: implemented, verified, synced specs, archived
  `qa-mcp-com-query-tool-and-worker-bundle`, and recorded Windows COM live-smoke
  provider gap for follow-up execution on the Windows host.
- 2026-07-07 OPSX pub: staged scoped card-owned diff, committed the delivery, and
  prepared push to `origin/main`.
