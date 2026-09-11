## 1. Platform Output Decoder

- [x] 1.1 Add byte-aware platform stdout/stderr normalization before JSON
  response construction.
- [x] 1.2 Preserve valid UTF-8 and ASCII output unchanged.
- [x] 1.3 Decode invalid UTF-8 output with CP866 fallback.
- [x] 1.4 Preserve existing output trimming, rune limits, and secret redaction.

## 2. Tests And Verification

- [x] 2.1 Add Go tests for CP866 Russian stdout/stderr becoming readable
  Unicode text.
- [x] 2.2 Add Go tests that valid UTF-8 and ASCII output are preserved.
- [x] 2.3 Add Go tests that redaction still applies after decoding.
- [x] 2.4 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 2.5 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-oem-output-decode.test.exe .` under `host-agent/windows-display-agent`.
- [x] 2.6 Run the 1C verification matrix checker in preflight and archive modes.
- [x] 2.7 Run `openspec validate host-agent-oem-output-decode --strict`.
- [x] 2.8 Run `git diff --check`.
- [x] 2.9 Record retained verification summary under
  `.artifacts/openspec/host-agent-oem-output-decode/20260705T074532Z/`.

## 3. OpenSpec Handoff

- [x] 3.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into
  the main spec before archive.
- [x] 3.2 Archive `host-agent-oem-output-decode` after tasks and validation are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/platform/execute` stdout/stderr decoder | Go unit tests for CP866 Cyrillic output, UTF-8 preservation, output bounding, and redaction | Go unit test output, Linux build/test output, retained verification summary | `.artifacts/openspec/host-agent-oem-output-decode/20260705T074532Z/oem-output-decode-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows host `ibcmd` Russian stdout/stderr | Read-only platform command smoke against operator-owned Windows host | Retained host-agent transcript when Windows host is available | `.artifacts/openspec/host-agent-oem-output-decode/20260705T074532Z/windows-oem-output-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, PowerShell runtime, or licensed host 1C platform is available inside this Linux workspace. | The first Windows package run must confirm real `ibcmd` Russian diagnostics are readable. |
