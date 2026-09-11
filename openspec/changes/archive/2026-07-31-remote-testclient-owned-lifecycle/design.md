## Context

Remote-client mode uses the Windows host-agent for display primitives and for
host-side TestClient launch. The Python MCP server currently records the
launched endpoint as an attachment with `owns_process: false`, and
`stop_test_client` is guarded as local-boot-only. The host-agent exposes
`/testclient/launch` and `/testclient/status`, but not a cleanup route for the
process it just launched.

This change affects Python manager/MCP code and the Windows host-agent. It does
not introduce protocol frame knowledge, capture sources, or replay changes.
Frame ranges and dynamic fields are not modified. Runtime evidence is limited
to sanitized lifecycle state, reason codes, and bounded process absence proof.

## Goals / Non-Goals

**Goals:**

- Make a host-agent-launched remote TestClient provider-owned from the MCP
  caller's perspective.
- Route `stop_test_client` through the same host-agent when the handle came from
  remote `launch_test_client`.
- Ensure repeated stop calls are idempotent and return stable final states such
  as `stopped`, `already_stopped`, or `not_owned`.
- Scope cleanup to the exact launched process identity, not to arbitrary 1C
  process discovery.
- Preserve attach-only semantics for clients started outside qa-mcp.

**Non-Goals:**

- Do not stop manually attached or operator-started TestClients.
- Do not remove lock files, enumerate or terminate unrelated 1C sessions, or
  expose raw host command lines.
- Do not change protocol capture/replay semantics, infobase contents, or
  business data.
- Do not add a new dependency or require Vanessa MCP, EDT, or metadata
  snapshots.

## Decisions

1. Add `/testclient/stop` to the host-agent.

   The host-agent is the process creator in remote-client mode, so it is the
   only surface that can stop the host process without leaking host-control
   authority into the container. Reusing `/platform/execute` or host-side shell
   snippets would make cleanup command-shaped instead of lifecycle-shaped and
   would be harder to constrain.

2. Track launched TestClient records in host-agent memory keyed by opaque
   lifecycle id.

   The launch endpoint already resolves the PID that owns the requested TPort.
   The agent will generate and return a host-agent lifecycle handle whose id is
   not derived from the PID, then retain PID, port, launch method, a durable
   process-completion signal, and the exact terminate callback for that launched
   process under that id. Stop must match the requested lifecycle id to an
   owned record before terminating it. This keeps scope exact and avoids
   process-name, fresh PID lookup, PID-only reuse, or port heuristics.

3. Make stop idempotent.

   If the owned record has already exited, or a previous stop completed, the
   endpoint returns a typed final state instead of an error. The tombstone
   remains addressable by lifecycle id, so a repeated stop for an old lifecycle
   cannot resolve a newer same-PID launch.

4. Model remote launch as owned in the Python MCP result.

   The MCP server stores remote ownership metadata alongside the active
   attachment. A manually attached endpoint remains `owns_process: false`;
   a host-agent launch becomes `owns_process: true` with
   `lifecycle_owner: "host-agent"` and an opaque lifecycle handle id required
   for remote stop.

## Risks / Trade-offs

- [Risk] A process may exit before stop is requested. -> Treat the durable
  completion signal as an owned terminal state and return `already_stopped` /
  `exited` without touching other processes.
- [Risk] PID reuse could make a stale stop target unsafe. -> Stop only when the
  request carries the opaque lifecycle id issued for the owned launch, store
  finalized records by that id, use the retained terminate callback for the
  original process, and treat a closed completion signal as terminal before any
  termination attempt.
- [Risk] The Linux offline suite cannot prove Windows GUI disappearance. ->
  Cover contract behavior with Go/Python tests and retain a Windows host-agent
  integration proof when the authorized host is reachable, otherwise record a
  provider gap.
- [Risk] Older or protocol-compatible host-agents may expose a PID-only
  `/testclient/stop` route without opaque lifecycle-handle enforcement. ->
  Preserve generic display protocol compatibility for non-stop primitives, but
  make remote TestClient stop fail closed unless the host-agent is the current
  lifecycle-stop version or explicitly advertises lifecycle-handle stop support.
- [Risk] Windows PowerShell 5.1 does not reliably read UTF-8-without-BOM
  `-File` scripts as UTF-8 and may serialize first-use module progress as
  `#< CLIXML` on redirected streams. -> Keep retained live-proof inputs
  ASCII-safe when they include Cyrillic values, reconstruct those values from
  UTF-8 base64 inside the proof, and suppress progress output in the transient
  task helper scripts.
- [Risk] Retained lifecycle proof may accidentally include raw host-agent log
  excerpts. -> Record structured startup/cleanup booleans only; do not retain
  host-agent log lines in proof JSON.

## Migration Plan

1. Ship Python and host-agent changes together in qa-mcp.
2. Rebuild/stage the Windows host-agent through the existing release path before
   relying on remote stop in a live environment.
3. Existing manually launched clients continue using `attach_test_client` and
   are not affected.
4. Rollback is to disable `QA_MCP_HOST_AGENT` or use the previous host-agent
   binary; remote launch will keep returning structured host-agent diagnostics
   instead of local cleanup authority.
