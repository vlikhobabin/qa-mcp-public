## Why

Driving qa-mcp HEAD against a real Russian-locale [redacted third-party configuration] file base
(User@192.0.2.205, 1С 8.3.27.2130, user `Админ`) during the connection-issues
runtime acceptance surfaced five diagnostics defects that the offline Linux suite
could not catch. They blocked the green legs of `com_connector_doctor`,
`qa_mcp_doctor` and the UIA-visible fallback even though the underlying COM read,
doctor chain and window discovery were sound.

## What Changes

- Windows host-agent COMConnector doctor (`/com/doctor`) now:
  - serializes its result with a hand-rolled encoder instead of the `JSON`
    object, which the classic WSH JScript engine (`cscript //E:JScript`) does not
    provide;
  - calls `Columns.Count()` as a method (not a property) when reading the query
    result;
  - receives its request payload as ASCII `\uXXXX`-escaped JSON so a raw-UTF-8
    body is not corrupted by `cscript`'s ANSI stdin decoding (which broke Cyrillic
    usernames and failed `Connect` auth);
  - surfaces the JScript's structured stdout error on a non-zero `cscript` exit
    instead of an empty-stderr "COM worker failed without diagnostic output".
- Windows host-agent UIA read (`/uia/visible_list_cells`) suppresses the
  PowerShell progress stream and tolerates a `#< CLIXML` wrapper, so the visible
  cells parse even when `Add-Type` emits a first-use progress record.
- `qa_mcp_doctor` never aborts: the `_com_check` probe is wrapped so a
  timeout/connection error becomes a single `com-doctor-probe-failed` leg instead
  of crashing the whole ordered chain.

This change touches Windows host-agent Go code and Python manager (doctor) code.
It requires no live-1C runtime to verify the offline behavior; the green-leg
behavior was additionally proven live on the .205 [redacted third-party configuration] host.

No behavior change to the COM query path (`query_com`/`assert_com_count`), the
remote launch command, or the `read_list_grid` fail-loud classification — those
verified correct as shipped.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: the `/com/doctor` read-smoke and
  `/uia/visible_list_cells` endpoints must return correct structured results
  against a real Russian-locale file base (Cyrillic credentials, 1C COM member
  semantics, CLIXML-wrapped PowerShell output) and must not swallow the
  underlying diagnostic error.
- `qa-mcp-tool-endpoint-contract`: `qa_mcp_doctor` must always return one ordered
  pass/fail/skipped chain; a failing COM leg is reported as a structured `fail`,
  never an unhandled exception.

## Impact

- `host-agent/windows-display-agent/com_doctor_windows.go`
- `host-agent/windows-display-agent/driver_windows.go`
- `src/qa_mcp/doctor.py`
- Offline tests: `tests/test_doctor.py`, `tests/test_com_host.py`, host-agent
  `go test`. No dependency or wire-contract changes.
