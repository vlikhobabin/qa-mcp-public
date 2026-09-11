## Context

The four connection-issues hardening cards (`qa-mcp-com-query-tool-and-worker-bundle`,
`read-list-grid-fail-loud-and-remote-window-discovery`,
`qa-mcp-doctor-endtoend-diagnostics`, `remote-testclient-launch-via-host-agent`)
each recorded a "retained Windows live-smoke provider gap". The 2026-07-08 run of
that gap drove qa-mcp HEAD against the real [redacted third-party configuration] file base on
User@192.0.2.205 (1С 8.3.27.2130, user `Админ`) and confirmed the shipped COM
query path (`Qty=1`), the doctor chain shape, the remote launch command and the
`read_list_grid` P0 fail-loud guarantee. Five diagnostics defects — invisible to
the offline Linux suite because they only manifest on a real Windows host with a
Russian-locale COM stack and a live PowerShell/cscript — blocked the green legs.

## Goals / Non-Goals

Goals:
- Make `com_connector_doctor`, `qa_mcp_doctor` and the UIA-visible fallback go
  green against a real Russian-locale file base.
- Keep the fixes minimal and local to the host-agent Go diagnostics and the
  Python doctor chain.

Non-Goals:
- No change to the COM query path, remote-launch command, or fail-loud read
  classification (verified correct as shipped).
- Not solving the two out-of-scope observations from the same run
  (host-agent-launched TestClient persistence; `read_list_grid` positive-read
  capture handshake on foreign configs — epic 111 item 4).

## Decisions

- **JScript result serialization → hand-rolled `enc()`** rather than a JSON
  polyfill. The classic WSH JScript engine (`cscript //E:JScript`) has no `JSON`
  object; a small recursive encoder over the doctor's fixed result shape
  (booleans/numbers/strings/arrays/plain objects, COM leaves → string) is
  smaller and dependency-free versus embedding json2.js.
- **`Columns.Count()` as a method.** 1C COM exposes the query-result column
  collection count as a method; the bare property form raises "Object doesn't
  support this property or method". Verified member-by-member on the live base.
- **ASCII-escape the cscript stdin payload (`asciiEscapeJSON`).** Go
  `json.Marshal` emits raw UTF-8 for non-ASCII, but `cscript`'s
  `WScript.StdIn.ReadAll()` decodes stdin with the console ANSI codepage, so a
  Cyrillic username corrupts and `Connect` fails auth. Escaping every non-ASCII
  rune to `\uXXXX` keeps the payload pure ASCII; the JScript `eval` reconstructs
  the exact runes regardless of codepage. Chosen over forcing a cscript Unicode
  mode (`//U` needs UTF-16 output plumbing) as the smaller, self-contained fix.
- **Surface cscript stdout on non-zero exit.** The JScript catch block writes a
  structured error to stdout before `WScript.Quit(2)`; the host-agent previously
  reported only the (empty) stderr. Prefer the stdout detail so the real COM
  error is not swallowed.
- **Suppress the PowerShell progress stream + tolerate CLIXML.** Set
  `$ProgressPreference='SilentlyContinue'` so the first `Add-Type` does not emit a
  progress record (the source of the `#< CLIXML` wrapper), and defensively
  extract the outermost `{ … }` object before `json.Unmarshal`.
- **Wrap `_com_check` like its sibling checks.** Every other doctor check already
  catches exceptions and returns a structured `_failure`; `_com_check` did not,
  so a probe timeout aborted the whole chain. Bring it in line.

## Risks / Trade-offs

- [Hand-rolled JScript encoder could mis-serialize an unusual COM value] →
  encoder falls back to `String(v)` for any non-plain object; the doctor result
  shape is fixed and small. Proven live returning `read_smoke:{rows:[{Qty:1}]}`.
- [`extractJSONObject` naïvely takes first `{`..last `}`] → the CLIXML wrapper
  contains no JSON braces, and `$ProgressPreference` removes the wrapper at
  source, so extraction is a belt-and-suspenders defense.

## Migration Plan

Rebuild the Windows host-agent (`GOOS=windows GOARCH=amd64`) and redeploy the
exe; no config or wire-contract change. Rollback = redeploy the prior host-agent
binary. The Python doctor fix ships with the qa-mcp package.

## Open Questions

- None for this change. The two out-of-scope observations are tracked separately.
