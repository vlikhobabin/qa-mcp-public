## REMOVED Requirements

### Requirement: Thin image uses the suite provider base
**Reason**: The public standalone image must build from public inputs and must
not inherit an AI for 1C provider base.
**Migration**: Use the pinned public Python base defined by the independent
standalone runtime.

### Requirement: Thin image exposes MCP through the suite proxy
**Reason**: `ai-mcp-proxy` is a private product dependency.
**Migration**: Serve authenticated Streamable HTTP MCP directly through the
project-owned application.

### Requirement: Model-B doctor includes platform and COM doctor links
**Reason**: Standalone no longer depends on AI for 1C platform/COM worker
endpoints.
**Migration**: Report only the public bridge capability, lifecycle, relay,
display and target checks; data/platform integrations belong downstream.

## MODIFIED Requirements

### Requirement: Model B remote TestClient defaults remain intact
The independent standalone image SHALL preserve model-B defaults that connect
protocol tools to a host-side TestClient and display tools to the public Windows
bridge without importing or invoking AI for 1C services.

#### Scenario: Container starts with model B defaults
- **WHEN** the standalone image starts without per-user endpoint overrides
- **THEN** remote-client mode, `host.docker.internal` and the documented default
  TPort are selected
- **AND** the only optional host control dependency is the public bridge.
