## Why

qa-mcp model B already has the right provider shape for the suite: the MCP server
can run as stdio, the Windows TestClient stays outside the container, and the
host-agent owns desktop operations. The thin image still bypasses the suite
provider base by running qa-mcp's own HTTP transport, binding port 8000 and
vendoring its own license broker.

## What Changes

- Change the protected thin image final stage to inherit the suite provider base
  image through an overrideable `SUITE_BASE_IMAGE`.
- Run `qa-native-mcp` as a stdio provider behind `ai-mcp-proxy serve-http` on
  container port 8080.
- Use the license broker supplied by the suite base image rather than copying
  `delivery/broker/ai1c-license` into the final image.
- Keep model B remote TestClient defaults and Windows host-agent integration
  unchanged.
- Add a scoped root-compose handoff for replacing the placeholder `ai-suite-qa`
  service with the published qa-mcp provider image.

## Capabilities

### New Capabilities
- `qa-mcp-suite-container-delivery`: qa-mcp thin images participate in the suite
  provider-base, proxy HTTP and gateway-ready delivery contract.

### Modified Capabilities
- none

## Impact

Touches Docker packaging, provider startup command, compose/runbook docs and
root suite coordination. It does not change protocol tools or Python manager
behavior. Live 1C runtime is not required for the transport/base verification;
verification is offline tests, image/proxy smoke and static compose inspection.
