## Why

Remote display primitives can currently fall back from a missing or weak window selector to a generic 1C/foreground-window heuristic. When the owned TestClient has an empty caption, that behavior can target an unrelated foreground application, so UI reads and actions must instead be bound to the active TestClient lifecycle identity and fail closed when the Windows desktop cannot prove that target.

## What Changes

- Extend remote launch and attach state with a bounded lifecycle/client display target that identifies the exact host TestClient process/window without depending on its caption.
- Route `capture_screenshot`, `send_keys`, `type_text`, `click`, and visible-list-cell reads through the active lifecycle/client target whenever the caller does not supply an explicit window selector.
- Preserve explicit-window precedence and reject missing, stale, mismatched, wildcard, or ambiguous implicit targets before any screenshot or input is attempted.
- Return typed locked, disconnected, and non-interactive desktop diagnostics through the host-agent and MCP result boundary.
- Add focused Python and Go regressions, Windows build/integration verification, and ignored sanitized runtime evidence. This changes Python manager/MCP and Windows host-agent runtime behavior plus durable user-facing documentation; it does not add a TestClient wire-protocol claim, require Vanessa MCP, or require EDT/metadata snapshots.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: Remote display tools inherit the active TestClient lifecycle target unless an explicit window selector is supplied, and expose typed targeting/session failures.
- `qa-mcp-windows-host-agent-security`: Authenticated display endpoints resolve only the exact lifecycle/client-owned window and never fall back to an unrelated foreground application.
- `qa-mcp-protocol-lab`: Windows verification retains sanitized proof for empty-title targeting, explicit override precedence, fail-closed isolation, and desktop-session diagnostics.

## Impact

- Python: `src/qa_mcp/mcp_server.py`, `src/qa_mcp/protocol/display_backend.py`, and focused endpoint/backend tests.
- Windows host-agent: display request schemas, lifecycle/window resolution, Win32 session diagnostics, version/capability compatibility, and Go tests under `host-agent/windows-display-agent/`.
- Contracts/docs: the three modified OpenSpec capabilities and the remote display/tool reference where behavior changes are user-visible.
- Verification: offline Python and Go suites, Windows cross-compile, strict OpenSpec/whitespace checks, and a Windows host-agent integration proof with only sanitized booleans/reason codes retained under ignored `.runtime/` paths.
