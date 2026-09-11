## Context

The Windows host-agent already owns authenticated host-side primitives for
display, platform commands, agent CLI execution, and Live MCP COM worker
execution. Live MCP now needs a smaller primitive: determine whether a
configured file infobase directory exists on the Windows host and whether the
expected marker file, normally `1Cv8.1CD`, is present.

Using Linux `Path.exists()` in a provider container is incorrect for Windows
paths. Using `/platform/execute` or `/agent/complete` for `Test-Path` would be
too broad for this diagnostic. A dedicated endpoint keeps the filesystem
surface narrow and auditable.

## Goals / Non-Goals

**Goals:**

- Add `POST /path/infobase` behind existing host-agent auth and origin checks.
- Accept a bounded request with `path` and optional `marker`, defaulting the
  marker to `1Cv8.1CD`.
- Return only marker status and sanitized diagnostic fields.
- Reject path browsing behavior before touching the filesystem.
- Document the endpoint for Live MCP host-bridge diagnostics.

**Non-Goals:**

- Do not return directory listings, file contents, file sizes, timestamps,
  ACLs, owners, or normalized absolute paths.
- Do not execute PowerShell, shell fragments, arbitrary platform commands, BSL,
  or COM.
- Do not introduce a second token or unauthenticated status endpoint.

## Decisions

1. **Use a dedicated endpoint.** The endpoint name `POST /path/infobase` makes
   the safety class explicit and keeps it separate from subprocess-spawning
   endpoints.

2. **Require a directory target and simple marker.** The root `path` must be a
   non-empty string without NUL bytes. If the path exists but is not a
   directory, the probe reports `host_path_exists=false` with
   `failure_reason="host_path_not_directory"`. The marker must be a filename,
   not a relative or absolute path.

3. **Return secret-safe evidence only.** The response includes
   `response_id="infobase-path-probe"`, `path_kind="file_infobase"`,
   `marker`, booleans, and a stable failure reason. It does not echo the raw
   requested path.

4. **Keep compatibility with existing auth tests.** Registering the route under
   `withAuth` preserves missing-token, wrong-token, origin, and limiter
   behavior without a new auth path.

## Risks / Trade-offs

- [Risk] A marker probe can still reveal whether a path exists. -> It is
  authenticated, only answers for the caller-supplied configured path, and does
  not reveal child names or contents.
- [Risk] Different deployments use a custom marker name. -> The request accepts
  a simple marker override but rejects separators and NUL bytes.
- [Risk] Host-agent route changes need Windows packaging awareness. -> The Go
  tests run on Linux; Windows install/binary publication remains a later
  release packaging step.
