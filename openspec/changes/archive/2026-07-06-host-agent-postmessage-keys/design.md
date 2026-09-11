## Context

The Windows host-agent resolves the 1C top-level window correctly, but
`handleSendKeys` currently calls `Focus` before `SendKeys`, and the Windows
driver emits keyboard input through `SendInput`. That route depends on the 1C
window being the OS foreground window. On a contended interactive desktop,
Windows can deny `SetForegroundWindow`, which blocks qa-mcp's `F5` refresh and
`Escape` clean-state sweep even though the target `V8TopLevelFrame*` window was
found.

This change affects QA/TestClient UI automation and the host-agent display
bridge. It does not make new native TestClient protocol claims, use protocol
capture/replay evidence, or require EDT/Vanessa/meta snapshots.

## Goals / Non-Goals

**Goals:**
- Send `F5` and `Escape` to the resolved 1C top-level window without requiring
  `SetForegroundWindow`.
- Keep the existing target-window resolution contract and authenticated
  endpoint boundary.
- Preserve real-foreground behavior for primitives that still need it, while
  returning structured `foreground-denied` diagnostics instead of HTTP 500.
- Bump the host-agent version and Python compatibility set for the changed
  input contract.

**Non-Goals:**
- Do not rewrite text input, mouse input, screenshots, COM execution, platform
  execution, or host-agent auth/firewall policy.
- Do not change model-A X11 input behavior.
- Do not add protocol captures, replay frames, or protocol command semantics.
- Do not perform live Windows desktop automation from this Linux workspace.

## Decisions

1. **Use target-window message delivery only for safe refresh keys.** The Go
   Windows driver will send `WM_KEYDOWN`/`WM_KEYUP` for `F5` and `Escape` to the
   resolved target HWND. Those keys are non-text, config-agnostic, and are the
   exact primitives qa-mcp needs for list refresh and clean-state sweeps. Other
   chords stay on the existing foreground-coupled `SendInput` route.

2. **Resolve before input, but do not focus for target-message keys.** The
   `/send_keys` handler should still resolve the target window and return target
   metadata. For an all-message-safe key sequence, it should call the
   target-window send path directly and never call `Focus`. This preserves
   default `V8TopLevelFrame*` targeting and avoids foreground-lock contention.

3. **Represent foreground denial as a typed driver error.** When foreground is
   genuinely required and `SetForegroundWindow` is denied, the driver should
   return an error that maps to `foreground-denied`, not generic
   `primitive-failed`. The HTTP response should be a non-500 structured
   response with `ok: false`, `error: "foreground-denied"`, and target context
   when available.

4. **Bump the handshake version.** Change `AgentVersion` and
   `HOST_AGENT_VERSION` to a new value for this input contract. Keep the
   compatibility set bounded by including the currently supported prior
   versions for install transition only.

5. **Retain offline and runtime evidence separately.** Linux Go tests can prove
   routing decisions, version compatibility, and error mapping. The actual busy
   Windows desktop behavior needs a retained Windows E2E transcript and is
   recorded as an applicable runtime evidence row that is unavailable in this
   workspace.

## Risks / Trade-offs

- [Risk] `PostMessage` may not reach child controls in some 1C windows.
  Mitigation: scope it to `F5` and `Escape`, retain Windows E2E proof, and keep
  other primitives on the existing foreground route.
- [Risk] A mixed key sequence could partially use message delivery and partially
  require foreground. Mitigation: route only all-message-safe sequences through
  the no-focus path; otherwise use the existing foreground route.
- [Risk] A non-500 foreground denial changes HTTP behavior for callers that
  assumed 500. Mitigation: keep the response structured with `ok: false` and a
  stable error code, and update Python diagnostics in the dependent change.
- [Risk] Version bump can reject older installed host-agents. Mitigation: update
  Python compatibility and tests, and keep install guidance in mismatch errors.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `host-agent/windows-display-agent` target-window `F5`/`Escape` delivery | Go unit tests for target-message key classification, `/send_keys` no-focus routing, and structured foreground denial | Go test output, Windows build check, retained verification summary | `.artifacts/openspec/host-agent-postmessage-keys/20260706T140652Z/postmessage-key-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows model-B `read_list_grid` refresh on busy desktop | Non-foreground `read_list_grid` against `demo10413` `Catalog.Currency`/`Справочник.Валюты` after installing the bumped host-agent | Retained host-agent transcript and MCP result showing populated rows without manual click | `.artifacts/openspec/host-agent-postmessage-keys/20260706T140652Z/windows-nonforeground-read-list-grid.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No operator-owned Windows GUI desktop, host-agent service, or licensed 1C TestClient is available inside this Linux workspace. | The first Windows package run must retain this transcript before relying on the busy-desktop proof. |
| Delivery or runtime apply | Host-agent version bump and Windows package install transition | Version handshake test and install guidance review | Python unit output and retained version compatibility summary | `.artifacts/openspec/host-agent-postmessage-keys/20260706T140652Z/version-compatibility.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
