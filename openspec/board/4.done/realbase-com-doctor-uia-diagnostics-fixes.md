# Harden real-base COM/UIA/doctor diagnostics — 5 fixes found by the .205 [redacted third-party configuration] E2E

## Status
4.done

## Owner
unassigned

## Order Index
125

## OpenSpec Stage
archived. Runtime-acceptance follow-up under epic 111.

## Source
- 2026-07-08 functional acceptance of the six connection-issues hardening cards
  (`qa-mcp-com-query-tool-and-worker-bundle`, `read-list-grid-fail-loud-and-remote-window-discovery`,
  `qa-mcp-doctor-endtoend-diagnostics`, `remote-testclient-launch-via-host-agent`)
  on the real Windows host **User@192.0.2.205**, [redacted third-party configuration] file base
  (`C:\Users\User\Documents\private-lab-infobase`, 1С 8.3.27.2130, user `Админ`).
- These are the "retained provider gap / Windows live-smoke" items recorded on
  those cards. Driving qa-mcp **HEAD** against the real Cyrillic base surfaced
  five defects the offline Linux suite could not catch. All five are already
  implemented and verified in the working tree (see Change 1 → Notes).

## Problem
The real-base run confirmed the shipped behavior for the COM query path
(`query_com`/`assert_com_count` → `Qty=1`), the doctor chain shape, the remote
launch command and — most importantly — the `read_list_grid` P0 fail-loud
guarantee (never a fabricated `row_count:0`). But five diagnostics defects blocked
the green legs of `com_connector_doctor`, `qa_mcp_doctor` and the UIA-visible
fallback:

1. **`com_connector_doctor` JScript used the `JSON` object** (`JSON.stringify`),
   which the classic WSH JScript engine invoked by `cscript //E:JScript` does not
   provide → `Microsoft JScript: 'JSON' - undefined` after a successful Connect.
2. **`queryResult.Columns.Count` was read as a property** — in 1C COM it is a
   method → `Object doesn't support this property or method` in the read smoke.
3. **Cyrillic corruption in the doctor payload**: the host-agent sends the
   `/com/doctor` request as raw UTF-8 (Go `json.Marshal`), but `cscript`'s
   `WScript.StdIn.ReadAll()` decodes stdin with the console ANSI codepage → the
   `Админ` username corrupts → `COMConnector.Connect` fails auth
   («неверный пользователь или пароль»). The real error was also swallowed: on a
   non-zero cscript exit the host-agent reported the empty stderr
   ("COM worker failed without diagnostic output") instead of the structured
   error the JScript catch block wrote to stdout.
4. **`qa_mcp_doctor` crashed the whole chain**: `doctor._com_check` did not wrap
   the COM probe in `try/except`, so a `TimeoutError`/connection error (e.g. when
   the file base is busy) propagated and aborted the entire ordered diagnostic
   chain instead of recording a single failed COM leg.
5. **UIA-visible fallback broke on `#< CLIXML`**: `readVisibleListCells` runs a
   PowerShell UIA script and parses its stdout as JSON, but the first `Add-Type`
   emits a "Preparing modules for first use" progress record, which PowerShell
   serializes as a `#< CLIXML` wrapper around redirected output → `json.Unmarshal`
   `primitive-failed` even though the UIA read succeeded.

## Scope
Fix all five in the host-agent (`com_doctor_windows.go`, `driver_windows.go`) and
the Python doctor (`doctor.py`); no behavior change to the COM query path, the
remote launch command, or the fail-loud read classification (those verified
green as shipped).

## Acceptance
- `com_connector_doctor` on [redacted third-party configuration] `Справочник.Валюты` returns
  `ok:true, connected:true, read_smoke:{rows:[{Qty:1}]}` with the full registry
  block (verified on .205).
- `qa_mcp_doctor` always returns one ordered pass/fail/skipped chain; a slow/busy
  COM leg becomes a `com-doctor-probe-failed` `fail`, never an exception.
- On a non-zero cscript exit the doctor surfaces the JScript's structured error
  detail, not an empty-stderr placeholder.
- Host-agent `/uia/visible_list_cells` returns `ok:true` with the real cells from
  the live `V8TopLevelFrameSDI` window, tolerating a `#< CLIXML` wrapper.
- `uv run --with pytest --with pyyaml pytest` green; `go test ./...` and
  `GOOS=windows go vet` green; suite drift gate OK.

## Change Set
- `realbase-com-doctor-uia-diagnostics-fixes` → `openspec/changes/realbase-com-doctor-uia-diagnostics-fixes/`

## Archive
- `openspec/changes/archive/2026-07-08-realbase-com-doctor-uia-diagnostics-fixes/`

## Result
Implemented, verified and archived. Five diagnostics fixes landed
(`com_doctor_windows.go` ×3 + stdout-surface, `driver_windows.go` UIA CLIXML,
`doctor.py` `_com_check`); +3 requirements synced into
`qa-mcp-windows-host-agent-security` (2) and `qa-mcp-tool-endpoint-contract` (1).
Gates: full pytest **778 passed**, host-agent `go test`/`go vet` OK,
`openspec validate --all` 14/0, matrix archive-gate `ok:true`. All three green
legs (`com_connector_doctor` Qty=1, `qa_mcp_doctor` chain, UIA 15 cells) proven
live on User@192.0.2.205 [redacted third-party configuration] (retained runtime evidence). Two follow-up
observations (host-agent-launch persistence; `read_list_grid` positive-read
capture handshake on foreign configs) recorded for separate cards.

## Next
- run `$opsx-pub openspec/board/4.done/realbase-com-doctor-uia-diagnostics-fixes.md`

## Change 1: `realbase-com-doctor-uia-diagnostics-fixes`

### Why
The COMConnector doctor, the doctor chain and the UIA-visible fallback could not
go green against a real Russian-locale file base until these five diagnostics
defects were fixed.

### Goal
Land the five fixes with regression coverage and sync the affected host-agent /
doctor capability specs.

### Scope
- `host-agent/windows-display-agent/com_doctor_windows.go`: hand-rolled `enc()`
  JSON serializer (no `JSON` object), `Columns.Count()` method call,
  `asciiEscapeJSON` for the cscript stdin payload, and surface cscript stdout on
  non-zero exit.
- `host-agent/windows-display-agent/driver_windows.go`: `$ProgressPreference =
  'SilentlyContinue'` in the UIA script + `extractJSONObject` CLIXML tolerance.
- `src/qa_mcp/doctor.py`: wrap the `_com_check` probe in `try/except → _failure`.

### Acceptance
- As in the card Acceptance; each leg proven live on .205 and covered by
  offline tests where a Linux test can exercise it.

### Depends On
- none (follow-up to the four archived connection-issues cards).

### Related
- Capabilities to modify: `qa-mcp-windows-host-agent-security` (the `/com/doctor`
  and `/uia/visible_list_cells` endpoints) and `qa-mcp-tool-endpoint-contract`
  (the `com_connector_doctor` / `qa_mcp_doctor` tool results).
- `docs/qa-mcp-connection-issues-2.md`, epic 111.

### Notes For `$openspec-ff-change`
- **The implementation is already present and verified in the working tree**
  (`git diff` = `com_doctor_windows.go`, `driver_windows.go`, `doctor.py`). Create
  the OpenSpec change artifacts + spec deltas that document these fixes; `$opsx-do`
  should verify (tests already green) + sync specs + archive rather than
  re-implement.
- Extend the existing host-agent-security / tool-endpoint specs; do not create a
  new capability namespace.

## Log
- 2026-07-08 filed from the .205 [redacted third-party configuration] real-base functional acceptance; five
  diagnostics fixes implemented and verified, pending OpenSpec artifacts + publish.
- 2026-07-08 `$opsx-ff`: created apply-ready OpenSpec artifacts (proposal/design/
  specs/tasks + Verification Matrix); `validate --strict` and `validate --all` green.
- 2026-07-08 `$opsx-do`: verified (pytest 778, go test/vet, matrix archive-gate
  `ok:true`), synced +3 requirements into main specs, archived the change, moved
  card to `4.done`.
- 2026-07-08 `$opsx-pub`: review gate NOT run (operator-invoked deliver, verdict
  absent) — publishing on the operator's explicit "оформи и запушь" request;
  scoped commit + push.
