## 1. Diagnostics Contract

- [x] 1.1 Add Python doctor regression coverage proving ordinary diagnostics use host-agent health/TestClient/COM routes and never invoke a Designer platform execute fallback.
- [x] 1.2 Update user-facing diagnostics documentation so catalog/open-link troubleshooting points to `qa_mcp_doctor`, descriptor/open-link input, metadata-provider input, or optional COM read-smoke instead of Designer metadata dumps.

## 2. Host-Agent Timeout Cleanup

- [x] 2.1 Extend `/platform/execute` timeout/cancel error payloads to include the spawned process PID in a structured field while keeping bounded/redacted diagnostics.
- [x] 2.2 Add Go tests for timed-out platform commands that assert PID reporting, process cleanup, and secret-safe output.
- [x] 2.3 Keep existing allowlist, mutation-class, operator-intent, and Designer explicit-operation policy unchanged.

## 3. Verification

- [x] 3.1 Run the verification matrix checker in preflight mode and retain output under `.artifacts/openspec/designer-dump-timeout-cleanup/<run-id>/`.
- [x] 3.2 Run focused Python doctor/tool-reference tests.
- [x] 3.3 Run focused Go host-agent tests under `host-agent/windows-display-agent`.
- [x] 3.4 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-designer-dump-timeout-cleanup.test.exe .` under `host-agent/windows-display-agent`.
- [x] 3.5 Run `openspec validate designer-dump-timeout-cleanup --strict`.
- [x] 3.6 Run `git diff --check`.
- [x] 3.7 Run the verification matrix checker in archive-gate mode and retain output under `.artifacts/openspec/designer-dump-timeout-cleanup/<run-id>/`.
- [x] 3.8 Run the suite regression gate: full pytest, suite source-of-truth drift helper, and smoke pytest marker gate.

## 4. OpenSpec Handoff

- [x] 4.1 Sync delta specs into `openspec/specs/qa-mcp-tool-endpoint-contract/spec.md` and `openspec/specs/qa-mcp-windows-host-agent-security/spec.md`.
- [x] 4.2 Archive `designer-dump-timeout-cleanup` after tasks and validation are complete.
- [x] 4.3 Record the Windows-host Designer timeout smoke as a deferred runtime checkpoint because this Linux workspace has no attached Windows desktop or licensed Windows 1C platform.
