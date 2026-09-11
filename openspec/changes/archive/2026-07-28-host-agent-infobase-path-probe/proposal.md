## Why

Live MCP host-bridge diagnostics need host-side file infobase marker evidence
because Linux containers cannot reliably check Windows paths such as
`C:\1C_BASES\private-lab-infobase`.

## What Changes

- Add an authenticated host-agent endpoint that probes only one requested file
  infobase directory and expected marker filename.
- Return bounded booleans and diagnostic codes:
  `host_path_exists`, `database_file_exists`, and `failure_reason`.
- Reject path-probe requests that would become broad filesystem access,
  including empty paths, NUL bytes, file paths as the root target, and marker
  names containing separators.
- Keep the endpoint behind the same bearer token, origin checks, and auth
  limiter as existing sensitive host-agent endpoints.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: the host-agent exposes a marker-only,
  authenticated file infobase path probe without directory listing or file
  content access.

## Impact

- Host-agent Go server: route registration, request validation, filesystem
  marker probe, response shaping, unit tests.
- Docs: host-agent README endpoint reference.
- Runtime: read-only host path metadata only; no 1C process, UI action, BSL
  execution, directory listing, or file content access.
