## Context

`POST /path/infobase` is already the authenticated host-side boundary used by
Live MCP to check whether a Windows file infobase path and marker file exist.
The active-client diagnostic belongs to the same boundary because the Linux
container cannot inspect Windows 1C processes or their launch arguments.

## Goals / Non-Goals

**Goals:**

- Add a bounded, best-effort host-side signal for active `1cv8`, `1cv8c`, and
  `1cv8s` processes whose launch metadata references the supplied file
  infobase path.
- Make the response useful for diagnostics without returning sensitive values:
  expose only status, count, process names, and whether path matching was
  supported.
- Keep authentication and invalid-request behavior unchanged.

**Non-Goals:**

- Proving that a matched process caused the timeout.
- Closing, killing, suspending, or otherwise managing 1C processes.
- Returning command lines, PIDs, executable paths, window titles, user names, or
  infobase paths.
- Adding a new unauthenticated endpoint or filesystem browsing capability.

## Design

The existing `runInfobasePathProbe` result gains an `active_processes` object.
The object is always present for valid authenticated requests:

```json
{
  "active_processes": {
    "source": "host_agent",
    "status": "available",
    "path_match_supported": true,
    "matching_process_count": 1,
    "process_names": ["1cv8c.exe"]
  }
}
```

When the host cannot inspect process metadata, the object uses
`status="unavailable"` and a compact `failure_reason`. The response does not
include raw process command lines or paths.

Implementation uses a small package-level process snapshot seam so tests can
inject deterministic process data. The default non-Windows snapshot returns an
unavailable status. The Windows implementation is allowed to use a read-only
process metadata route and must sanitize before returning.

## Verification Matrix

| Surface | Affected scope | Required evidence | Artifact path |
| --- | --- | --- | --- |
| Host-agent endpoint contract | `POST /path/infobase` response shape and auth boundary | Go unit tests for matched, unmatched, unavailable, and redaction cases | `host-agent/windows-display-agent` test output |
| Windows active-process runtime | Windows host-agent active 1C process discovery against demo host | Read-only Windows endpoint evidence when reachable; otherwise concrete not-verifiable row | `.runtime/changerail/evidence/` |
| 1C source/runtime mutation | N/A | No 1C source, UI, or data-changing operation is edited or executed | N/A: diagnostic-only host-agent endpoint |
