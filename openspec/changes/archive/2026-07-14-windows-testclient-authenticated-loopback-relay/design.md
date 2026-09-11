## Context

The Windows TestClient TPort is transport-reachable over LAN but intentionally
does not complete the captured TestManager handshake for a genuinely remote
peer. Docker Desktop on the same Windows host works because its forwarded
connection originates locally. In the team topology the qa provider is remote,
so the workstation host-agent must provide that local termination.

## Goals / Non-Goals

**Goals:** authenticate before loopback dial; fixed target only; one active
manager; shared client connector; transparent binary relay; disabled by
default; sanitized health/evidence.

**Non-Goals:** generic TCP forwarding; caller-selected destinations; TLS/VPN;
multiple concurrent TestManagers for one TestClient; embedding the token in
profiles or evidence.

## Decisions

### Existing bridge secret authenticates a bounded preface

An enabled relay listens on an explicit address and expects one ASCII line:
`QA-MCP-TESTCLIENT-RELAY/1 <token>`. It bounds length/time, compares the token
in constant time, acquires a single-session slot and only then dials the fixed
`127.0.0.1:<configured-port>` target. The server returns `OK` before raw
bidirectional copy; all other responses are bounded codes without secrets.

### Python uses one transport factory

`connect_testclient()` reads a relay endpoint and token from runtime env. It
sends/validates the preface only when the requested address exactly matches the
configured relay endpoint. TestClientSession, ReplaySession, lifecycle probes
and direct protocol helpers all call this factory. With no relay configuration
it is exactly `socket.create_connection`.

### Launch port, protocol endpoint and display target are distinct

Host-agent launch still creates the local TestClient on its real TPort. After
host readiness, container-side readiness and the recorded attachment use the
configured relay endpoint. This prevents accidentally launching 1cv8 on the
relay port. Windows display commands still resolve the 1C top-level window by
the real local TPort, because the relay listener belongs to the host-agent and
cannot identify the TestClient process. `QA_MCP_HOST_AGENT_CLIENT_PORT`
therefore overrides display targeting only; protocol sockets continue through
the authenticated relay. When unset, it falls back to `QA_MCP_CLIENT_PORT` so
existing direct contours remain unchanged.

### Readiness does not consume the single-manager target

An authenticated relay connection necessarily opens the fixed loopback target,
so using the full connector as a generic port probe races the next TestManager
handshake and can terminate the Windows client. After a successful host-agent
launch, qa-mcp therefore combines the host-agent's local PID/TPort proof with a
TCP-only reachability probe of the relay listener. A repeated
`attach_test_client` reuses that source-bound launch result. The first
authenticated target connection belongs to the actual descriptor/read tool;
authentication or target failure still returns fail-loud from that tool.

## Risks / Trade-offs

- A raw relay expands the network surface → explicit opt-in, existing secret,
  constant-time auth, fixed loopback target and one session.
- Every protocol helper must use the factory → repository search plus focused
  tests prevent direct `socket.create_connection` regressions.
- A listener-only readiness probe does not validate the relay token → target
  readiness remains bound to the authenticated host-agent launch, and the first
  protocol tool is the authoritative authenticated end-to-end proof.
- Preface token lives in provider runtime env → same boundary as the existing
  host-agent token; never rendered into client profiles/evidence.

## Verification

- Go socket tests cover auth, malformed/oversized preface, busy session and
  transparent binary echo through fixed target.
- Python socket tests cover exact endpoint matching, auth failures and direct
  compatibility; display backend tests cover the separate real-TPort override;
  affected protocol tests remain green.
- Root T4 M9 proves launch/attach/descriptor/non-empty grid and owned cleanup.
