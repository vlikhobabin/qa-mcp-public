## 1. Safe HTTP Bind Defaults

- [x] 1.1 Change the model-A HTTP host default in `src/qa_mcp/mcp_server.py` to `127.0.0.1`.
- [x] 1.2 Add an explicit unsafe-bind opt-in for wildcard or non-loopback HTTP hosts and warn when it is used.
- [x] 1.3 Update `docker/docker-compose.yml` to publish `127.0.0.1:8000:8000`.
- [x] 1.4 Update `docker/run-host-platform.sh` to keep host-network MCP binds local unless unsafe exposure is explicitly requested.

## 2. Documentation And Verification

- [x] 2.1 Update README or delivery Docker docs with the local-only default and exposed-mode warning.
- [x] 2.2 Add focused Python/config tests for loopback default and wildcard rejection without opt-in.
- [x] 2.3 Run the focused tests plus relevant offline tool-surface tests.
- [x] 2.4 Run `openspec validate mcp-http-bind-safe-default --strict`.
