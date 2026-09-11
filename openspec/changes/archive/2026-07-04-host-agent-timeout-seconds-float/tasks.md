## 1. Host-agent Decode And Timeout Normalization

- [x] 1.1 Change `agentCompleteRequest.TimeoutSeconds` to decode JSON numbers that may contain a decimal point.
- [x] 1.2 Update `normalizeAgentTimeout` to accept the decoded numeric type while preserving default, one-second floor and `maxAgentTimeout` clamp behavior.

## 2. Regression Coverage

- [x] 2.1 Add a handler-level test that posts a literal JSON float `timeout_seconds` body and asserts the request is accepted and dispatched.
- [x] 2.2 Keep existing int timeout, missing CLI, unknown agent, timeout and prompt-redaction tests passing.

## 3. Verification

- [x] 3.1 Run `go test ./...` from `host-agent/windows-display-agent`.
- [x] 3.2 Run `GOOS=windows GOARCH=amd64 go build -ldflags "-H windowsgui" -o /tmp/qa-mcp-host-agent.exe .` from `host-agent/windows-display-agent`.
- [x] 3.3 Run `openspec validate host-agent-timeout-seconds-float --strict` and `git diff --check`.
- [x] 3.4 Record that 1C runtime verification is not applicable because the change is limited to the host-agent HTTP decode contract and offline Go checks.
