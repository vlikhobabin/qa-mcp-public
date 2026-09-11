## Context

`host_agent_testclient_lifecycle_stop_supported()` already treats
`0.1.10-testclient-lifecycle-handle` as safe for `/testclient/stop` and allows
a protocol-compatible future host-agent to prove the same support with the
`testclient-lifecycle-handle-stop` capability. `RemoteAgentBackend.handshake()`
normalizes `/version` responses before returning them to callers, but it
currently omits the advertised `capabilities` field. The support helper
therefore cannot see future explicit support on the real handshake path.

No protocol capture, frame replay, live 1C runtime, or Windows host-agent
binary change is involved. The affected behavior is the Python remote display
backend's HTTP JSON normalization and remote stop routing decision.

## Goals / Non-Goals

**Goals:**

- Preserve only bounded, typed lifecycle-stop capability advertisements from
  `/version`.
- Accept the existing current lifecycle-stop host-agent version.
- Accept protocol-compatible future host-agents only when the preserved
  capability proves lifecycle-handle stop support.
- Continue refusing legacy/protocol-compatible PID-only routes before posting
  `/testclient/stop`.
- Prove the behavior with offline Python regression tests.

**Non-Goals:**

- Do not add new host-agent endpoints or change the Windows host-agent binary.
- Do not loosen exact operator version overrides or SHA-256 pinning.
- Do not infer stop support from arbitrary truthy capability values.
- Do not run live UI, COM, or TestClient capture evidence for this pure Python
  compatibility change.

## Decisions

1. Normalize capabilities inside `RemoteAgentBackend.handshake()`.

   The handshake is the boundary where untrusted `/version` JSON is already
   reduced to a bounded Python result. Preserving capabilities there keeps the
   support helper and every caller using the same sanitized shape instead of
   rereading raw payloads later.

2. Accept only two capability shapes.

   A list preserves only non-empty string capability names. A mapping is reduced
   to entries whose values are explicit booleans; this keeps
   `{"testclient-lifecycle-handle-stop": "yes"}` and other truthy values from
   becoming authorization signals.

3. Keep stop support capability-specific.

   Generic display protocol compatibility remains insufficient for
   `/testclient/stop`. The preserved capability only authorizes the
   lifecycle-handle stop route when it explicitly names
   `testclient-lifecycle-handle-stop`.

## Risks / Trade-offs

- [Risk] A future host-agent advertises a richer capability schema.
  -> Mitigation: unknown shapes are ignored and fail closed until qa-mcp adds a
  reviewed parser for that schema.
- [Risk] Capability payloads become large.
  -> Mitigation: preserve only list names or boolean mappings and bound the
  retained collection size.
- [Risk] Existing legacy host-agents are accidentally treated as lifecycle-stop
  capable.
  -> Mitigation: keep the current-version allowlist and add route-level tests
  that prove legacy `0.1.9-testclient-owned-lifecycle` still fails before
  `/testclient/stop`.
