## Context

Card 120 fixes model-B display primitives but deliberately avoids a sensitive
auto-update path. The first install must happen on the Windows host, in the
interactive user context, so the agent can access the same desktop as the 1C
client.

## Goals / Non-Goals

**Goals:**

- Provide a one-liner install route for the Windows host.
- Register the agent as an interactive logon Scheduled Task, not a service.
- Configure the firewall rule for the chosen host-agent port.
- Make Python startup/first call verify the agent version and binary hash.
- Produce actionable errors for absent, mismatched or unauthorized agents.

**Non-Goals:**

- Do not implement `POST /update` or self-restart in v1.
- Do not copy binaries from the Linux container to an unprepared host.
- Do not require admin rights beyond the documented firewall/task setup.

## Decisions

- The install script lives next to the agent source, for example
  `host-agent/install-windows-host-agent.ps1`, and is documented in
  `docker/README.md`.
- The scheduled task runs at user logon with `/IT` semantics so it can see the
  interactive desktop. The script records where logs are written, but logs are
  not committed.
- The expected version/hash is carried by Python constants or a small package
  data file and compared to `/version`.
- A mismatch returns `host-agent-version-mismatch` with the exact install or
  update command; v1 never posts a replacement binary to the host.
- `QA_MCP_HOST_AGENT_TOKEN` is required for primitive calls and documented with
  the Docker Compose/model-B environment.

## Risks / Trade-offs

- PowerShell is normally out of scope for Linux workflows -> this is explicitly
  host-side Windows install material, not a Linux runtime entrypoint.
- Hash mismatch can block a locally rebuilt test binary -> allow an explicit
  development override only if documented as unsafe for normal runs.
- Firewall rules may need elevation -> installer reports the failed step and
  leaves the Python backend fail-closed.

## Migration Plan

1. Add install script and docs without changing default Linux behavior.
2. Add handshake checks to the remote display backend.
3. Add tests for absent, auth-failed, version-mismatch and version-match cases.
4. Verify the install route on the Windows lab before the E2E change archives.

## Open Questions

- None for v1. Auto-update is deferred.
