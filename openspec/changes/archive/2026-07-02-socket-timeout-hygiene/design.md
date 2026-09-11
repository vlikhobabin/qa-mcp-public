## Context

Native write sessions open a socket before replaying setup frames. If setup
raises from `__enter__`, Python does not call `__exit__`, so the socket can
linger. The same sessions use short read-idle socket timeouts during exchanges,
and those timeouts can remain in force for later `sendall` calls. Lifecycle
teardown also accepts a raw pid and kills the owning process group without
confirming that qa-mcp owns that process.

## Goals / Non-Goals

**Goals:**
- Close sockets created by `NativeWriteSession.__enter__` when setup replay
  fails.
- Apply a send-appropriate timeout before outbound frames and classify
  `socket.timeout` from send paths distinctly from protocol divergence.
- Refuse `stop_test_client(pid)` for pids that are not known or recognizable as
  qa-mcp-owned TestClient runtime processes.
- Cover the behavior with offline fake-socket and process-ownership tests.

**Non-Goals:**
- No broad process supervisor rewrite.
- No new live mutation/action surface.
- No changes to business data or 1C metadata.

## Decisions

- **Setup cleanup in `__enter__`:** wrap setup replay after socket creation in a
  `try`/`except`, close the socket, clear local state, and re-raise the original
  error.
- **Send timeout boundary:** set the socket timeout to a configured send timeout
  immediately before `sendall`; restore or continue with the read timeout only
  during receive draining.
- **Truthful timeout mapping:** classify a `socket.timeout` raised by `sendall`
  as `send_timeout` or equivalent user-facing reason, not as response
  divergence.
- **Ownership guard:** prefer recorded launch ownership when available; for the
  stateless pid path, inspect `/proc/<pid>/comm` and refuse processes whose
  command name is not an expected `1cv8*` or `Xvfb` runtime component.

## Risks / Trade-offs

- [Risk] `/proc/<pid>/comm` is only a heuristic for stateless calls. Mitigation:
  fail closed for unknown names and keep recorded owned handles authoritative
  when available.
- [Risk] A send timeout value that is too high can delay failures. Mitigation:
  keep it bounded and separate from the short receive idle timeout.
- [Risk] Closing a socket on setup failure can mask close errors. Mitigation:
  preserve the original setup exception and ignore close errors only during
  cleanup.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Native session lifecycle | `NativeWriteSession.__enter__` setup replay failure | fake socket that raises during setup | offline unit test proving close is called and original error re-raises | `tests/` plus `.artifacts/openspec/socket-timeout-hygiene/2026-07-02/setup-cleanup/` if retained | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: setup cleanup is local to failed session startup |
| Socket send timeout | outbound frames in native write/session calls | fake socket with slow-send timeout | offline unit test proving distinct timeout reason, not divergence | `tests/` plus `.artifacts/openspec/socket-timeout-hygiene/2026-07-02/send-timeout/` if retained | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: external callers may compare old reason text |
| Runtime cleanup ownership | `stop_test_client(pid)` process-group teardown | fake `/proc` or monkeypatched ownership probe | offline unit test proving non-owned/non-TestClient pid refusal | `tests/` plus `.artifacts/openspec/socket-timeout-hygiene/2026-07-02/ownership/` if retained | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: stateless pid ownership remains conservative by design |
| Business data / posting | none | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | no business command, posting, import/export, or object write is introduced | No residual risk; no business-data surface is touched |
