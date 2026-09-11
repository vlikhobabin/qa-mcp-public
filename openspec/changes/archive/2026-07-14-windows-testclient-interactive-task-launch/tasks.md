## 1. Regression first

- [x] 1.1 Add Go tests for one-string 1C argv, environment-block safety,
      password redaction and bounded interactive-session launch-context
      reporting; record RED against the WTS implementation.

## 2. Windows launcher

- [x] 2.1 Implement a fixed transient InteractiveToken task shell broker after
      verified active-session matching, authenticated in-memory request
      transport, actual-child process-handle monitoring and bounded setup
      failures.
- [x] 2.2 Remove the WTS/CreateProcessAsUser launch dependency while keeping
      non-Windows direct exec and readiness dwell unchanged.
- [x] 2.3 Update host-agent docs/security contract for the no-residual-artifact,
      credential-free-task boundary and Limited/Interactive principal behavior.
- [x] 2.4 Carry the exact QA platform version through the semantic launch
      request and fail closed when that catalog version is invalid or absent.

## 3. Verification

- [x] 3.1 Run focused/full Go tests, Windows cross-build, artifact builder,
      strict OpenSpec validation, secret scan and diff check.
- [x] 3.2 Run the real station immediate and >=60-second PID/TPort/window proof,
      then retain sanitized owned-cleanup evidence.

## Verification Evidence

- The failed direct/task-child attempts were retained as diagnostics and the
  delivered broker now uses `Shell.Application.ShellExecute`, discovers the
  actual PID from the requested TPort owner and leaves no task/wrapper artifact.
- `uv run pytest -q`: 829 passed; Go tests and Windows cross-build passed;
  protected image runtime verification reported 68 tools and clean compiled
  source/key scans.
- Source-bound installed host-agent SHA256:
  `55e57bd2bc4c35f026b4c600ed327b2f5e6c9fed24146966d3d39e37814e304d`.
- Final M9 launched platform `8.3.27.2130` with method
  `interactive_task_shell_broker`; the same PID/TPort/window remained live for
  61.833 seconds with zero transient task/artifact:
  `../.artifacts/openspec/team-t4-two-workstation-e2e-gate/20260713T200946Z-release-ready-rerun/matrix/M09/solo-regression.json`.
