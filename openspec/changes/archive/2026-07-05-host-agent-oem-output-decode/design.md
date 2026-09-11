## Context

`runPlatformProcess` captures stdout and stderr as byte buffers, then currently
uses `Buffer.String()` before bounding and JSON serialization. Go strings may
hold invalid UTF-8 bytes, but `encoding/json` replaces invalid sequences with
`U+FFFD`. Windows 1C platform tools commonly emit localized console text in the
OEM code page, so Russian diagnostics from `ibcmd` can become unreadable even
though ASCII output remains intact.

## Goals / Non-Goals

**Goals:**
- Preserve valid UTF-8 and ASCII platform output unchanged.
- Decode invalid UTF-8 output as CP866 before redaction, bounding, and JSON
  response construction.
- Keep returned stdout/stderr as strings so existing callers do not need a
  response-shape migration.
- Preserve existing secret redaction and output length bounds.

**Non-Goals:**
- Do not add arbitrary shell execution or broaden executable allowlists.
- Do not change `operation`, `mutation_class`, or `operator_intent` policy
  enforcement.
- Do not introduce live platform command execution in this Linux workspace.
- Do not add base64 output fields unless string decoding cannot satisfy tests.

## Decisions

1. **Decode bytes before redaction.** Introduce a byte-aware platform-output
   normalization helper. It decodes valid UTF-8 directly and falls back to
   CP866 for invalid byte sequences, then applies the existing redaction and
   rune-limit behavior.

2. **Keep response compatibility.** The endpoint continues to return
   `stdout` and `stderr` string fields. There is no new base64 field in this
   change.

3. **Use a structured code-page decoder.** Prefer `golang.org/x/text` charmap
   support over ad hoc replacement tables so the behavior is reviewable and
   testable.

## Risks / Trade-offs

- **Not every Windows host uses CP866.** The immediate E2E finding is Russian
  OEM output, where CP866 is the relevant failure. A later enhancement can
  query the host console output code page if broader locale coverage is needed.
- **Binary output may decode to text.** `/platform/execute` is for bounded
  command diagnostics, not arbitrary binary transport. Keeping string output is
  consistent with the existing endpoint contract.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/platform/execute` stdout/stderr decoder | Go unit tests for CP866 Cyrillic output, UTF-8 preservation, output bounding, and redaction | Go unit test output, Linux build/test output, retained verification summary | `.artifacts/openspec/host-agent-oem-output-decode/20260705T074532Z/oem-output-decode-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows host `ibcmd` Russian stdout/stderr | Read-only platform command smoke against operator-owned Windows host | Retained host-agent transcript when Windows host is available | `.artifacts/openspec/host-agent-oem-output-decode/20260705T074532Z/windows-oem-output-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, PowerShell runtime, or licensed host 1C platform is available inside this Linux workspace. | The first Windows package run must confirm real `ibcmd` Russian diagnostics are readable. |
