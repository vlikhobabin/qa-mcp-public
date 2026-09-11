## 1. Host-Agent CLI Semantics

- [x] 1.1 Forward non-empty `reasoning_effort` to Claude CLI as
  `--effort <level>`.
- [x] 1.2 Preserve existing Codex `model_reasoning_effort` command rendering.
- [x] 1.3 Convert unsupported effort behavior into a typed fail-closed
  diagnostic instead of successful downgraded output.
- [x] 1.4 Confirm selected-agent failures do not fallback to another installed
  CLI.

## 2. Readiness Metadata

- [x] 2.1 Return or retain bounded effective profile metadata for successful
  `/agent/complete` calls.
- [x] 2.2 Return or retain bounded selected-profile metadata for authenticated
  fail-closed calls.
- [x] 2.3 Verify prompt text, token values, local credential paths and raw
  unbounded stderr are absent from metadata and logs.

## 3. Verification

- [x] 3.1 Add Go tests for Claude effort command rendering.
- [x] 3.2 Add Go tests for Codex effort parity and explicit no-fallback agent
  selection.
- [x] 3.3 Run `go test ./...` in `host-agent/windows-display-agent`.
- [x] 3.4 If the Windows executable is rebuilt during delivery, retain
  source-bound artifact provenance and Windows read-only smoke evidence. Not
  applicable to the product executable: delivery did not rebuild or replace
  it. The separately mandatory Windows-native source verification passed with
  a source-bound Windows amd64 test binary; retained evidence:
  `.runtime/changerail/evidence/s35-qa-host-agent-claude-effort-parity/windows-native-verification.md`.
