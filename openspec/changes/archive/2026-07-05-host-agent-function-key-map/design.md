## Context

qa-mcp calls the remote host-agent display backend to send `F5` from
`_force_list_refresh`. The Windows host-agent sends input through Win32 virtual
keys, but the current `virtualKey` map only includes `f4` among function keys.
That makes `F5` fail before `SendInput` and prevents a cold dynamic list from
being force-refreshed over the display bridge.

## Goals / Non-Goals

**Goals:**
- Resolve `f1` through `f12` to `VK_F1` through `VK_F12`.
- Keep existing supported key aliases and modifier behavior unchanged.
- Make the keymap regression test run in the Linux CI pass, not only on
  Windows.

**Non-Goals:**
- Do not change mouse input, Unicode text input, focus acquisition, screenshot
  capture, or host-agent authentication.
- Do not add new business-data mutations or native TestClient protocol claims.
- Do not require a live Windows host in this Linux delivery.

## Decisions

1. **Keep the behavior in the host-agent keymap.** The change is limited to
   virtual-key name resolution. `SendInput` sequencing and focus behavior stay
   unchanged.

2. **Make key resolution unit-testable on Linux.** Move or keep the pure
   `virtualKey` mapping in a file that builds on both Windows and Linux, so
   `go test ./...` can verify `F5` in the active CI workspace. Windows-only
   input delivery remains covered by the existing build boundary.

3. **Use the contiguous Win32 function-key range.** The resolver maps `f1` to
   `0x70` and increments through `f12` at `0x7B`, matching the standard
   `VK_F1` through `VK_F12` constants.

## Risks / Trade-offs

- **Linux tests cannot prove real desktop delivery.** They prove key
  resolution. A live Windows TestClient smoke remains the final proof for
  `SendInput` delivery and is recorded as `N/A` here because no attached
  Windows desktop is available in this workspace.
- **Moving pure keymap code can affect package build tags.** Keep the helper
  dependency-free except for string normalization, and leave Windows-specific
  Win32 calls in the Windows build file.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `host-agent/windows-display-agent` display keymap for qa-mcp list refresh | Go unit test for `virtualKey` F1-F12 and Linux host-agent test pass | Go unit test output, Linux build/test output, retained verification summary | `.artifacts/openspec/host-agent-function-key-map/20260705T074532Z/function-key-map-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows TestClient dynamic-list `F5` delivery | Read-only attach + list refresh smoke against operator-owned Windows host | Retained QA/TestClient run log or host-agent transcript when Windows desktop is available | `.artifacts/openspec/host-agent-function-key-map/20260705T074532Z/windows-f5-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, PowerShell runtime, GUI desktop, or licensed 1C TestClient is available inside this Linux workspace. | The first Windows package run must execute this smoke before relying on live `F5` refresh delivery. |
