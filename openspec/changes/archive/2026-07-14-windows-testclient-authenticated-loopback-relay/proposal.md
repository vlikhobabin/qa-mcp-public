## Why

The T4 solo provider runs on the Linux team server and connects to the Windows
TestClient over LAN. The proven Windows protocol behavior rejects that remote
peer with `66 53 b2 a6` + EOF, while a connection originating on the Windows
host completes the same manager handshake. Direct attach therefore cannot
satisfy the required solo read.

## What Changes

- Add an opt-in host-agent TCP relay that authenticates a bounded preface with
  the existing bridge secret and dials only a fixed loopback TestClient port.
- Limit the relay to one active TestManager session and fail closed before
  target connect on malformed/unauthorized requests.
- Route every Python TestClient socket path through one relay-aware connector.
- Keep the authenticated protocol relay endpoint separate from the real local
  TPort used by Windows display/window resolution.
- Keep readiness/attach probes from consuming the Windows client's
  single-manager session: combine host-agent target readiness with a
  listener-only container route probe and reserve authenticated target access
  for the real protocol tool.
- Wire compose and root T4 M9 to the relay endpoint while leaving direct local
  TCP unchanged when the feature is disabled.

## Capabilities

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: define the authenticated fixed-target
  relay boundary.
- `qa-mcp-runtime-configuration`: define relay endpoint/token configuration and
  direct-mode compatibility, including an explicit host-agent display TPort
  when the protocol endpoint is a relay listener.
- `qa-mcp-tool-endpoint-contract`: make launch/attach/read use the same routed
  protocol endpoint.

## Impact

- Go host-agent listener/health/config/installer
- Python TestClient transport and all direct socket consumers
- Docker compose environment and root T4 M9 harness/runbook
