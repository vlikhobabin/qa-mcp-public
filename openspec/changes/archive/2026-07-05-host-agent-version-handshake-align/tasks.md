## 1. Display Backend Handshake

- [x] 1.1 Align the default host-agent version expectation with the current
  supported host-agent build family.
- [x] 1.2 Add an explicit bounded compatibility set for default handshake
  behavior.
- [x] 1.3 Preserve exact comparison when
  `QA_MCP_HOST_AGENT_EXPECTED_VERSION` is supplied.
- [x] 1.4 Preserve exact SHA-256 pinning when
  `QA_MCP_HOST_AGENT_EXPECTED_SHA256` is supplied.

## 2. Tests And Verification

- [x] 2.1 Add Python tests for default-compatible host-agent versions.
- [x] 2.2 Add Python tests for exact override mismatch diagnostics.
- [x] 2.3 Add Python tests that SHA mismatch still fails independently.
- [x] 2.4 Run `uv run pytest tests/test_display_backend.py`.
- [x] 2.5 Run the 1C verification matrix checker in preflight and archive modes.
- [x] 2.6 Run `openspec validate host-agent-version-handshake-align --strict`.
- [x] 2.7 Run `git diff --check`.
- [x] 2.8 Record retained verification summary under
  `.artifacts/openspec/host-agent-version-handshake-align/20260705T074532Z/`.

## 3. OpenSpec Handoff

- [x] 3.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into
  the main spec before archive.
- [x] 3.2 Archive `host-agent-version-handshake-align` after tasks and
  validation are complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `RemoteAgentBackend.handshake()` default host-agent version compatibility | Python unit tests for accepted default-compatible versions, exact env override, mismatch diagnostics, and SHA mismatch preservation | Python focused test output, retained verification summary | `.artifacts/openspec/host-agent-version-handshake-align/20260705T074532Z/version-handshake-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Live Windows host-agent `/version` handshake | Read-only authenticated `/version` request against operator-owned Windows host | Retained host-agent transcript when Windows host is available | `.artifacts/openspec/host-agent-version-handshake-align/20260705T074532Z/windows-version-handshake-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host or host-agent service is available inside this Linux workspace. | The first Windows package run must confirm the installed service version against the default compatibility set. |
