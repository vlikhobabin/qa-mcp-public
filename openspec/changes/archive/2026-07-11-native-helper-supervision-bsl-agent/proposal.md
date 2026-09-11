## Why

The delivered workstation `bsl-agent` service has a stable consumer contract but no owner process on the Windows workstation. The frozen topology assigns launch, readiness, restart, routing, and shutdown ownership to qa-mcp's host-agent.

## What Changes

- Add opt-in supervision of `bsl-agent.exe workstation serve` using the delivered `ai1c.bsl-agent-workstation-supervision.v1` arguments, loopback endpoints, and owned-process stop semantics.
- Poll readiness, expose bounded state/version/restart count in host-agent health and `qa_mcp_doctor`, restart crashed helpers with configurable backoff, and stop only the owned helper with the host-agent.
- Add authenticated host-agent routes for read-only diagnostics and explicit resync to the configured loopback service.
- Preserve solo/non-W-B behavior when no helper is configured.
- Verify with fake helper processes in Go and pytest. Real Windows launch/control-event behavior and the paired workstation diagnostic round-trip remain supervised provider gaps.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: add bounded native-helper supervision and authenticated local BSL diagnostic routing.
- `qa-mcp-runtime-configuration`: add optional doctor reporting for the supervised workstation BSL service without making it a prerequisite for solo mode.

## Impact

- Host-agent Go lifecycle, HTTP routes, Python doctor output, tests, version compatibility, and host-agent documentation.
- Consumes read-only files from `/opt/ai-dev-suite-for-1c/bsl-mcp`; that repository is not modified.
- No BSL source mutation, 1C metadata/form/role/posting/report/migration changes, TestClient protocol changes, live 1C execution, Vanessa MCP, or EDT/meta snapshot dependency.
