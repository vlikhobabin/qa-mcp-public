# qa-mcp standalone Windows host bridge

This directory contains the complete public source and installer for the
Windows side of standalone qa-mcp. The bridge has no AI for 1C runtime
dependency. Its executable exposes only authenticated TestClient lifecycle and
relay plus bounded window, input, screenshot and visible-cell UIA primitives.

## Public v1 contract

Every request requires `X-QA-MCP-Agent-Token`. Browser-origin requests are
accepted only from the configured allowlist. The authenticated
`GET /v1/capabilities` handshake returns:

- `api: qa-mcp.windows-host-bridge` and `api_major: 1`;
- the source-bound executable version and SHA-256;
- the exact standalone capability and endpoint lists.

The retained HTTP endpoints are `/version`, `/health`, `/send_keys`, `/type`,
`/click`, `/screenshot`, `/window_list`, `/uia/visible_list_cells`, and
`/testclient/{launch,status,stop}`. The optional TestClient relay is a separate
authenticated TCP listener that connects only to its configured loopback
TPort. COM, BSL, agent completion, Team registration/onboarding, host-path
probing and generic platform execution are not compiled or installed.

qa-mcp checks the API major and all required capabilities before lifecycle or
desktop actions. Missing capabilities and incompatible majors fail closed;
there is no legacy-route fallback.

## Build

From the public repository root:

```sh
./bin/ai-build-windows-host-agent build --output-dir .runtime/windows-host-agent
./bin/ai-build-windows-host-agent verify --bundle-dir .runtime/windows-host-agent
```

The builder cross-compiles the Windows/amd64 GUI executable, records source
revision/fingerprint and SHA-256, checks required standalone markers, and
rejects removed product markers. Release qualification must use those exact
bytes.

## Install and uninstall

Run the tracked installer in the interactive Windows user session. Keep the
token in its ACL-protected file; never pass it in scheduled-task arguments.

```powershell
powershell -ExecutionPolicy Bypass -File .\host-agent\install-windows-host-agent.ps1 `
  -ExePath .\qa-mcp-host-agent.exe `
  -BindAddress 127.0.0.1 `
  -PlatformCatalog 'C:\Program Files\1cv8'
```

For a Docker Desktop connection, bind explicitly and scope the firewall:

```powershell
powershell -ExecutionPolicy Bypass -File .\host-agent\install-windows-host-agent.ps1 `
  -ExePath .\qa-mcp-host-agent.exe `
  -BindAddress 0.0.0.0 `
  -RemoteAddress 192.168.65.0/24 `
  -TestClientRelayAddress 0.0.0.0:15382
```

Reinstall is idempotent: the task restarts only for exact executable, token or
argument drift. Uninstall validates that the scheduled task points at the
owned executable and then removes only the exact task, process, firewall rules
and install files. When `-TestClientRelayAddress` is omitted during uninstall,
the installer reads the owned relay port from its persisted env file before
deleting that state:

```powershell
powershell -ExecutionPolicy Bypass -File .\host-agent\install-windows-host-agent.ps1 -Uninstall
```

The standalone container uses `QA_MCP_HOST_AGENT`,
`QA_MCP_HOST_AGENT_TOKEN`, and, when enabled,
`QA_MCP_TESTCLIENT_RELAY_ENDPOINT`/`QA_MCP_TESTCLIENT_RELAY_TOKEN` to connect
through the same public v1 contract. A deployment probe must perform an actual
authenticated `TestClientSession.read_initial()` through that relay; listener
reachability alone is not protocol evidence.

## Safety

Every display/read route requires an active interactive desktop and a window
bound to the exact bridge-owned lifecycle ID/PID/TPort. Explicit window
selectors are compatibility hints and cannot replace or override that target.
All lifecycle and display handlers share an authenticated in-flight execution
limit and return `429 execution-capacity-exhausted` before handler/driver work
when full. Stop accepts only the bridge-owned lifecycle handle.
Locked/disconnected desktops, wrong targets, stale handles and incompatible
clients are rejected before input or process cleanup. Never stop 1C processes
by image name or broad pattern.
