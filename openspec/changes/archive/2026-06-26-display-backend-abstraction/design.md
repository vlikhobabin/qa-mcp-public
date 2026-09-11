## Context

The MCP server currently exposes display-bound tools through direct imports of
X11 helper functions. In model-B remote-client mode those tools return
`display-unavailable-remote-client`, while protocol tools use
`QA_MCP_CLIENT_HOST` and `QA_MCP_CLIENT_PORT` successfully. Card 120 fixes the
remaining display subset by placing a host-side native agent behind a Python
backend interface.

## Goals / Non-Goals

**Goals:**

- Keep Linux local TestClient behavior unchanged.
- Make the display primitive boundary explicit and unit-testable.
- Route configured remote-client display calls to the host agent instead of the
  Linux X display.
- Keep locate/text geometry and higher-level 1C orchestration in Python.
- Return structured, actionable errors when no usable display backend exists.

**Non-Goals:**

- Do not implement Windows UIA in v1.
- Do not add host-agent auto-update in this change.
- Do not move pure protocol tools behind the display backend.
- Do not change the model-B protocol TCP connection path.

## Decisions

- Introduce a Python backend module, for example
  `src/qa_mcp/protocol/display_backend.py`, with a small protocol: `type_text`,
  `send_keys`, `click`, `capture_screenshot`, and `list_windows`.
- `LocalXTestBackend` delegates to the existing XTEST, screenshot and window
  helper implementations. This keeps the current subprocess command shapes and
  tests valid.
- `RemoteAgentBackend` uses only the Python standard library HTTP client so
  the runtime dependency surface stays small. It reads `QA_MCP_HOST_AGENT` and
  optional `QA_MCP_HOST_AGENT_TOKEN`.
- MCP tools ask a backend resolver for the current backend. When
  `QA_MCP_REMOTE_CLIENT` is true and `QA_MCP_HOST_AGENT` is absent or fails the
  handshake, display tools return a structured error that includes the install
  command from the handshake change.
- The `open_external_processor` tool is treated as display-bound because it
  uses screenshot, locate, keyboard and mouse primitives.

## Risks / Trade-offs

- Remote agent network failure -> return a clear backend diagnostic and do not
  fall back to local X in remote-client mode.
- Coordinate systems can differ between Linux Xvfb and Windows GDI -> keep
  higher-level locate and geometry logic in Python against the returned PNG so
  tests exercise one implementation.
- HTTP client errors could hide actionable install instructions -> normalize
  connection, auth and version failures into stable result payloads.
- Existing tools mix direct helper imports with local closures -> refactor in
  small steps and cover the previous command shapes with tests.

## Migration Plan

1. Add the backend module and unit tests with fake runners/HTTP responses.
2. Replace MCP guard-only display tools with backend dispatch.
3. Route helper modules through the backend without changing public tool
   signatures.
4. Keep `QA_MCP_REMOTE_CLIENT` without `QA_MCP_HOST_AGENT` fail-closed until the
   host agent and handshake changes land.

## Open Questions

- None for v1. UIA and self-update remain separate follow-up work.
