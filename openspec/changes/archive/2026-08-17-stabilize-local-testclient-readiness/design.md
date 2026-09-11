## Context

`launch_test_client` currently waits for a connectable TPort, sleeps, writes an
ownership marker and returns. The probe does not read the TestClient protocol
greeting and can therefore precede license/session failure. Cleanup validates
the primary PID before it validates an Xvfb recorded in the same marker.

## Decisions

1. Local readiness checks TPort without reading the protocol greeting, then
   observes the process for a 20-second default `settle_sec` window. Reading
   the greeting consumes the cold-client manager session and is reserved for
   explicit doctor/protocol calls. Controlled callers may still override the
   stability window.
2. A process exit or collapsed listener during the bounded stability window is
   a launch failure; owned client/display resources are torn down before the
   exception is returned.
3. Diagnostics reuse bounded log tails and redact the configured infobase
   password.
4. Stateless cleanup may accept an already-missing primary PID only when an
   exact qa-mcp ownership marker exists. Any live companion Xvfb must still
   match PID, start ticks, process group and command name before termination.
5. Missing companion processes are treated as already cleaned; mismatched or
   reused companion processes remain a refusal.
6. A local launch refuses an already-listening TPort before it changes Apache,
   starts Xvfb or starts 1C. This prevents an existing endpoint from being
   attributed to a newly spawned PID.
7. The ownership marker is written immediately after process creation and
   before readiness waits. A transport cancellation can therefore leave an
   owned but recoverable lifecycle instead of an unmarked orphan.

## Risks

- The listener probe cannot prove the full manager handshake without consuming
  the cold-client session. Delayed license/session failures are instead caught
  by the 20-second process observation and bounded launch logs.
- The stability window adds 20 seconds to a successful default local launch.
  This covers the observed delayed license failure while retaining the
  existing explicit `settle_sec` override for controlled callers.
- A process can still race onto the TPort after the initial vacancy check. The
  local single-owner workflow and early marker bound that residual race, while
  a pre-existing listener now fails closed.
