# host-agent /com/execute: Content-Type с charset=utf-8

## Status
4.done

## Owner
qa-mcp - host-agent (`host-agent/windows-display-agent/com_exec.go`). Small COM
bridge follow-up to keep the `/com/execute` response contract consistent with
the UTF-8 JSON fix from the tester-feedback wave.

## OpenSpec Stage
archived

## Source
- tester-feedback wave `f43e699` fixed common `writeJSON` responses to emit
  `application/json; charset=utf-8`.
- COM bridge commit `338a24a` added `com_exec.go` with raw worker JSON
  passthrough but left the success header as bare `application/json`.

## Summary
`/com/execute` already returns UTF-8 worker JSON unchanged, but its success
response did not declare `charset=utf-8`. This card aligned the direct
raw-passthrough handler with the rest of the host-agent JSON contract without
restructuring the worker body.

## Acceptance
- `/com/execute` success response has `Content-Type:
  application/json; charset=utf-8`.
- The success body remains byte-for-byte worker stdout after the existing
  trim/JSON validity checks; no re-encoding, truncation, or JSON restructuring.
- `go test ./...` passes under `host-agent/windows-display-agent`.

## Change Set
- `com-execute-utf8-content-type` -
  `openspec/changes/archive/2026-07-06-com-execute-utf8-content-type/`

## Change 1: `com-execute-utf8-content-type`

### Why
The direct COM success response bypassed `writeJSON`, so it missed the shared
UTF-8 charset header. Any client that does not assume UTF-8 for JSON could
mis-decode localized 1C payloads even though the worker bytes are valid UTF-8.

### Goal
Declare UTF-8 JSON on successful `/com/execute` responses while preserving the
raw worker JSON passthrough behavior.

### Scope
- `host-agent/windows-display-agent/com_exec.go`: set success
  `Content-Type` to `application/json; charset=utf-8`.
- `host-agent/windows-display-agent/main_test.go`: assert the success header
  includes `charset=utf-8` and the non-ASCII worker body remains unchanged.

### Acceptance
- Successful `/com/execute` responses expose the UTF-8 charset.
- Existing COM allowlist, auth, timeout, redaction and worker passthrough tests
  continue to pass.
- No live COM, TestClient capture/replay, or 1C data mutation is required.

### Depends On
- `host-agent-com-execute-endpoint` archived in
  `openspec/changes/archive/2026-07-05-host-agent-com-execute-endpoint/`.

### Related
- `openspec/changes/archive/2026-07-06-com-execute-utf8-content-type/`
- `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`

## Verify
- `go test ./...` under `host-agent/windows-display-agent`: passed.
- `go -C host-agent/windows-display-agent test ./...`: passed under traced
  runner.
- `openspec validate com-execute-utf8-content-type --strict`: passed.
- `openspec validate qa-mcp-windows-host-agent-security --strict`: passed.
- `openspec validate --all`: passed after archive with 19 items.
- `git diff --check`: passed.
- Full suite gate `uv run --with pytest --with pyyaml pytest`: 707 passed.
- Suite drift gate: 0 findings.
- Smoke gate `uv run --with pytest --with pyyaml pytest -m smoke`: 2 passed,
  705 deselected.
- Matrix preflight and archive checks passed; retained evidence is under
  `.artifacts/openspec/com-execute-utf8-content-type/`.

## Archive
- `openspec/changes/archive/2026-07-06-com-execute-utf8-content-type/`

## Related
- `openspec/changes/archive/2026-07-06-com-execute-utf8-content-type/`
- `openspec/changes/archive/2026-07-05-host-agent-com-execute-endpoint/`
- `host-agent/windows-display-agent/com_exec.go`
- `host-agent/windows-display-agent/main_test.go`
- `.artifacts/openspec/com-execute-utf8-content-type/verification-summary.md`

## Result
Implemented, verified and archived `com-execute-utf8-content-type`: successful
`/com/execute` responses now declare
`application/json; charset=utf-8`, and the fake-worker regression test proves
the non-ASCII worker response body remains byte-for-byte unchanged. Published
by the scoped OPSX commit recorded in the publish summary.

## Next
- none

## Log
- 2026-07-06T00:00:00Z OPSX pub: scoped commit prepared with message
  `fix(host-agent): declare COM execute UTF-8 JSON`; final hash is recorded in
  the publish summary.
- 2026-07-06T00:00:00Z OPSX do: implemented the header fix, verified Go tests,
  OpenSpec gates, suite regression gates, matrix evidence, archived
  `openspec/changes/archive/2026-07-06-com-execute-utf8-content-type/`, and
  moved card to `4.done`.
- 2026-07-06T00:00:00Z OPSX ff: created apply-ready artifacts for
  `com-execute-utf8-content-type` and moved card to `2.todo`.
- 2026-07-06 card created: COM handler did not inherit the `writeJSON` charset
  fix; align it for HTTP-client consistency while preserving current httpx-safe
  behavior.
