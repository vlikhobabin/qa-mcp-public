## 1. COMConnector doctor JScript (`com_doctor_windows.go`)

- [x] 1.1 Replace `JSON.stringify` with a self-contained `enc()` encoder (no `JSON` object)
- [x] 1.2 Read `queryResult.Columns.Count()` as a method, not a property
- [x] 1.3 ASCII-escape the cscript stdin payload (`asciiEscapeJSON`) so Cyrillic credentials survive
- [x] 1.4 On non-zero cscript exit, surface the JScript stdout structured error instead of empty stderr

## 2. UIA visible-cells read (`driver_windows.go`)

- [x] 2.1 Set `$ProgressPreference = 'SilentlyContinue'` in the UIA PowerShell script
- [x] 2.2 Extract the outermost JSON object (`extractJSONObject`) to tolerate a `#< CLIXML` wrapper

## 3. Doctor chain (`src/qa_mcp/doctor.py`)

- [x] 3.1 Wrap the `_com_check` probe in `try/except` returning a `com-doctor-probe-failed` failure leg

## 4. Verification

- [x] 4.1 `uv run --with pytest --with pyyaml pytest` green (incl. `tests/test_doctor.py`, `tests/test_com_host.py`)
- [x] 4.2 Host-agent `go test ./...` and `GOOS=windows GOARCH=amd64 go vet` green
- [x] 4.3 Suite drift gate OK
- [x] 4.4 `openspec validate realbase-com-doctor-uia-diagnostics-fixes --strict` and `openspec validate --all` green

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient host diagnostics (COM) | host-agent `/com/doctor` read-smoke JScript (serialize/Count/Cyrillic/error-surface) | `com_connector_doctor` returns `ok:true` + `read_smoke:{rows:[{Qty:1}]}` on [redacted third-party configuration] | Live tool result on User@192.0.2.205 `Справочник.Валюты` | .artifacts/openspec/realbase-com-doctor-uia-diagnostics-fixes/20260708T044629Z/windows-live-smoke.json | provided | qa-mcp | — | offline Go tests cannot exercise a real Russian-locale COM stack; covered by the live .205 evidence |
| MCP tool contract (doctor chain) | `qa_mcp_doctor._com_check` exception handling | single ordered chain; busy COM leg → `com-doctor-probe-failed` fail | `tests/test_doctor.py` + live chain on .205 | tests/test_doctor.py | provided | qa-mcp | — | none — offline test covers the exception path |
| QA/TestClient host diagnostics (UIA) | host-agent `/uia/visible_list_cells` CLIXML tolerance | `ok:true` with real cells from live `V8TopLevelFrameSDI` | Live endpoint result on .205 (15 cells) | .artifacts/openspec/realbase-com-doctor-uia-diagnostics-fixes/20260708T044629Z/windows-live-smoke.json | provided | qa-mcp | — | CLIXML only appears with a live PowerShell/UIA host; covered by the live .205 evidence |
| COM query path / remote-launch / read_list_grid fail-loud | unchanged behavior | no code change; verified green as shipped | prior archived cards + .205 run | archived connection-issues changes | N/A | qa-mcp | verified-unchanged; out of this change's scope | none — no code change; fail-loud + Qty=1 re-confirmed on .205 |

Runtime note: the Windows live evidence was captured against the operator-owned
.205 host during the runtime-acceptance session; it is retained as session
runtime evidence (not a committed artifact) per the data-safety policy. Offline
Go/pytest coverage is the committed gate.
