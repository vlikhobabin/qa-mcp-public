## 1. Supervisor launch contract

- [x] 1.1 Add explicit child-log configuration, close output handles after each
  child exit, and retain helper-directory CWD anchoring.
- [x] 1.2 Raise constructor and CLI startup-timeout defaults to 480 seconds.
- [x] 1.3 Add fake-helper tests for simulated service CWD, readiness, early
  stderr capture and restart/log-handle cleanup.

## 2. Windows scheduled-task delivery

- [x] 2.1 Extend `install-windows-host-agent.ps1` with BSL artifact, workspace,
  configuration, syntax-helper, platform-version, cache, child-log and timeout
  parameters and render them as fixed host-agent arguments.
- [x] 2.2 Configure Task Scheduler restart-on-failure and retain secret-safe
  command construction.
- [x] 2.3 Update host-agent documentation and installer contract tests.

## 3. Verify and archive

- [x] 3.1 Run focused Go/Python tests, `go test ./...` and `go vet ./...`.
- [x] 3.2 Sync both modified capabilities, run repository verification and
  strict OpenSpec validation, then archive the change with retained summaries.
