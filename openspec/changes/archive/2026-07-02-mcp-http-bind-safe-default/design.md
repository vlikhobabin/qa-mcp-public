## Context

The thin Docker path already prefers `127.0.0.1:8000`. The model-A path differs: `QA_MCP_HTTP_HOST` defaults to `0.0.0.0`, `docker/run-host-platform.sh` uses host networking, and `docker/docker-compose.yml` publishes port `8000` on all interfaces. Because the FastMCP streamable-HTTP surface has no authentication layer, safe defaults must be network-local.

## Design

Make loopback the normal model-A path:

- Change `QA_MCP_HTTP_HOST` default in `src/qa_mcp/mcp_server.py` to `127.0.0.1`.
- Add a guard such as `QA_MCP_HTTP_ALLOW_UNSAFE_BIND=1` for `0.0.0.0`, `::` or other wildcard/non-loopback host values. Without the opt-in, fail closed or rewrite to loopback with a clear startup error; failing closed is preferred because it prevents a misleading deployment.
- Emit a warning when unsafe bind is explicitly enabled, stating that the HTTP MCP transport has no built-in auth and should be fronted by an auth proxy or isolated network.
- Change `docker/docker-compose.yml` to publish `127.0.0.1:8000:8000`.
- Keep the thin compose/bootstrap path local-only and align docs so both model-A and thin users see the same safe default.
- Update `docker/run-host-platform.sh` so host-network runs bind the MCP server to loopback unless the operator sets both the host and the unsafe opt-in.

## Verification

This is a transport/configuration change, not a 1C runtime card. Verification is:

- Focused Python unit tests or startup-config tests proving loopback is the default and unsafe wildcard binds fail without opt-in.
- Static inspection of Docker Compose and run scripts for loopback publish defaults.
- Existing offline server/tool-surface tests to ensure the transport change does not alter registered tools.
