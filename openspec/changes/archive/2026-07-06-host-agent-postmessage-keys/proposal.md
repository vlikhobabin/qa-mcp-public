## Why

The Windows host-agent currently sends `F5` and `Escape` through `SendInput`,
which requires the target 1C window to be foreground. On a busy interactive
desktop, Windows foreground-lock can deny `SetForegroundWindow`, so qa-mcp
cannot refresh or clean list state even though the 1C window was resolved
correctly.

## What Changes

- Deliver single-window-safe keys used by qa-mcp refresh and clean-state flows
  (`F5` and `Escape`) directly to the resolved 1C top-level window with Win32
  window messages instead of foreground-coupled `SendInput`.
- Keep authenticated targeting through the existing resolved-window path
  (`title`, `class:`, `hwnd:`, `pid:`, or the default `V8TopLevelFrame*`
  heuristic).
- Keep a hardened foreground route for primitives that still require real
  foreground, but report denied foreground as structured `foreground-denied`
  rather than a generic primitive failure.
- Bump the host-agent version and Python compatibility set so the changed input
  contract is explicit during `/version` handshake.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: extends the authenticated host-agent
  display-input contract so refresh/clean-state keys can be sent to the target
  1C window without stealing desktop foreground, and denied foreground attempts
  produce a structured diagnostic.

## Impact

- Touches host-agent Go code and tests under `host-agent/windows-display-agent/`.
- Touches Python host-agent version compatibility in
  `src/qa_mcp/protocol/display_backend.py`.
- Does not change native TestClient protocol frames, protocol replay captures,
  COM bridge behavior, model-A X11 behavior, MCP provider setup, EDT/meta
  snapshots, Vanessa MCP, live 1C data, or runtime lab configuration.
- Verification requires Go tests/build checks and retained Windows E2E evidence
  when a Windows host/TestClient desktop is available; this Linux workspace can
  provide offline contract evidence and record the Windows runtime gap.
