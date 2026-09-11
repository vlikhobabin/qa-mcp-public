## Context

The model-B container can reach the Windows host over `host.docker.internal`,
but it cannot access the user's interactive desktop APIs. A process running in
the user's Windows desktop session must own the primitives that touch the
visible 1C client: keyboard, mouse, screenshot and window enumeration.

## Goals / Non-Goals

**Goals:**

- Produce a single static Go `.exe` with no 1C libraries and no installer
  dependency.
- Keep the agent thin: Win32 primitives in Go, orchestration in Python.
- Support Unicode text input through `SendInput` with `KEYEVENTF_UNICODE`.
- Return window-targeted PNG screenshots using `PrintWindow` with a `BitBlt`
  fallback.
- Require token authentication for primitive endpoints.

**Non-Goals:**

- Do not add UIA semantic lookup in v1.
- Do not implement self-update in v1.
- Do not embed Python locate/geometry logic into the Go agent.
- Do not run as a Windows service.

## Decisions

- Place the agent under a dedicated source root such as
  `host-agent/windows-display-agent/` with its own `go.mod`.
- Use `net/http` with JSON request/response payloads and a binary PNG response
  or base64 PNG field for screenshots; Python tests can fake either route.
- Implement `/version` and `/health` as unauthenticated or minimally
  authenticated read-only endpoints. Primitive endpoints require
  `X-QA-MCP-Agent-Token`.
- Foreground management is part of the agent API because the spike showed the
  1C form is a single `V8TopLevelFrameSDI` window. Requests can target by
  process id, title substring, or active foreground window depending on the
  primitive.
- Screenshot capture prefers `PrintWindow(PW_RENDERFULLCONTENT)` against the
  target top-level HWND and falls back to `BitBlt` when PrintWindow cannot
  render.

## Risks / Trade-offs

- Foreground lock may prevent input -> expose foreground diagnostics and keep
  live verification evidence for `GetForegroundWindow` and GUI thread focus.
- Antivirus or firewall policy may block the listener -> installer/handshake
  reports actionable setup steps and does not auto-replace binaries.
- GDI rendering can produce blank screenshots for minimized windows -> agent
  validates PNG size and captures a diagnostic result.
- Token configuration mismatch can look like agent failure -> stable 401 error
  body distinguishes auth from connectivity.

## Migration Plan

1. Add the Go module and unit-testable request/response handlers.
2. Add Windows-only Win32 implementation files guarded by build tags.
3. Add a deterministic build command for `qa-mcp-host-agent.exe`.
4. Wire Python remote backend tests against a fake agent before live Windows
   execution.

## Open Questions

- None for v1. Self-update and UIA remain follow-up scope.
