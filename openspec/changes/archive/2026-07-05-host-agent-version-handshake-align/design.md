## Context

`RemoteAgentBackend.handshake()` calls `/version`, reads the host-agent
`version`, and currently requires exact equality with
`HOST_AGENT_VERSION = "0.1.0-card124"` unless the environment supplies
`QA_MCP_HOST_AGENT_EXPECTED_VERSION`. The current host-agent reports
`0.1.0-platform-execute`, so an otherwise reachable and authenticated display
backend is rejected before any keystroke, screenshot, or window-list primitive
can run.

## Goals / Non-Goals

**Goals:**
- Make the default handshake accept the current supported host-agent build
  without an environment override.
- Keep explicit operator version overrides exact.
- Keep unsupported versions as `host-agent-version-mismatch` with install
  guidance.

**Non-Goals:**
- Do not remove SHA-256 pinning or weaken it when
  `QA_MCP_HOST_AGENT_EXPECTED_SHA256` is supplied.
- Do not make the host-agent endpoint unauthenticated.
- Do not introduce broad semver ranges that silently accept unknown binaries.

## Decisions

1. **Use a bounded compatibility set for the default pin.** The default
   handshake accepts the newly built host-agent version and the already shipped
   `0.1.0-platform-execute` build. Unknown versions continue to fail.

2. **Keep env override exact.** When an operator supplies
   `QA_MCP_HOST_AGENT_EXPECTED_VERSION`, the backend compares against that
   value exactly. This preserves the existing diagnostic and pinning behavior.

3. **Do not couple version acceptance to SHA acceptance.** SHA pinning remains
   exact and independent. A compatible version with the wrong configured SHA
   still fails as `host-agent-hash-mismatch`.

## Risks / Trade-offs

- **A compatible older build may lack newer fixes.** The default compatibility
  set intentionally accepts the current deployed build so existing installations
  recover from the handshake mismatch. The package/release flow still needs to
  install the newer host-agent to get keymap and output-decoding fixes.
- **Too much tolerance would hide real drift.** Keep the compatibility set
  explicit and small rather than semver-wide.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `RemoteAgentBackend.handshake()` default host-agent version compatibility | Python unit tests for accepted default-compatible versions, exact env override, mismatch diagnostics, and SHA mismatch preservation | Python focused test output, retained verification summary | `.artifacts/openspec/host-agent-version-handshake-align/20260705T074532Z/version-handshake-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Live Windows host-agent `/version` handshake | Read-only authenticated `/version` request against operator-owned Windows host | Retained host-agent transcript when Windows host is available | `.artifacts/openspec/host-agent-version-handshake-align/20260705T074532Z/windows-version-handshake-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host or host-agent service is available inside this Linux workspace. | The first Windows package run must confirm the installed service version against the default compatibility set. |
