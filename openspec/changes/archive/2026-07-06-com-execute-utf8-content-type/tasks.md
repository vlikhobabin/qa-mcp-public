## 1. Host-Agent Charset Contract

- [x] 1.1 Change `/com/execute` success responses to set `Content-Type` to `application/json; charset=utf-8`.
- [x] 1.2 Preserve the existing raw worker JSON passthrough path without parsing, re-marshalling, truncating, or CP866 fallback decoding the worker response body.
- [x] 1.3 Extend the fake-worker COM success test to assert the UTF-8 charset header and byte-for-byte non-ASCII body preservation.

## 2. Verification

- [x] 2.1 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 2.2 Run `openspec validate com-execute-utf8-content-type --strict`.
- [x] 2.3 Run `openspec validate qa-mcp-windows-host-agent-security --strict` after syncing the delta spec.
- [x] 2.4 Run `openspec validate --all`.
- [x] 2.5 Run `git diff --check`.
- [x] 2.6 Retain `.artifacts/openspec/com-execute-utf8-content-type/verification-summary.md` with command outcomes and the matrix row resolution.

## 3. OpenSpec Handoff

- [x] 3.1 Sync the modified COM bridge requirement into `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`.
- [x] 3.2 Archive `com-execute-utf8-content-type` after tasks and validation are complete.
- [x] 3.3 Mark protocol capture/replay evidence as N/A because this change adds no native TestClient protocol claim.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/com/execute` HTTP response contract for live-mcp COM WorkerResponse JSON | Fake-worker Go test checks UTF-8 content type and non-ASCII raw body passthrough; live COM execution unchanged | scenario_file, scenario_log | `.artifacts/openspec/com-execute-utf8-content-type/verification-summary.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real COMConnector execution is outside this header-only change and remains covered by the earlier COM bridge delivery. |
