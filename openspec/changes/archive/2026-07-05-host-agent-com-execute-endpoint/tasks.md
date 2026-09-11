## 1. Host-Agent COM Endpoint

- [x] 1.1 Add `POST /com/execute` behind the existing `withAuth` middleware.
- [x] 1.2 Add COM WorkerRequest policy validation for the fixed operation allowlist.
- [x] 1.3 Require operator-intent evidence for `guarded_posting_smoke` before worker resolution or spawn.
- [x] 1.4 Add fixed worker path configuration from `-com-worker`, `QA_MCP_COM_WORKER_EXE`, or `ai-com-worker.exe` next to the host-agent binary.
- [x] 1.5 Implement the COM worker runner with original JSON stdin, `--worker`, process-group timeout cleanup, bounded stderr diagnostics, and no request-body logging.
- [x] 1.6 Return valid worker stdout JSON as UTF-8 without `maxPlatformOutputRunes`, CP866 fallback decoding, or JSON restructuring.
- [x] 1.7 Extend authenticated `/health` with bounded COM worker availability diagnostics.

## 2. Installer And Documentation

- [x] 2.1 Bump `AgentVersion` and update `COMPATIBLE_HOST_AGENT_VERSIONS`.
- [x] 2.2 Update `host-agent/install-windows-host-agent.ps1` to install or reference `ai-com-worker.exe`, write `QA_MCP_COM_WORKER_EXE`, and pass `-com-worker`.
- [x] 2.3 Update `host-agent/README.md` with the `/com/execute` contract, worker installation path, security boundary, health diagnostics, and Windows E2E handoff.

## 3. Tests And Verification

- [x] 3.1 Run the 1C verification matrix checker in preflight mode for this artifact.
- [x] 3.2 Add fake-worker Go tests for valid read operation passthrough with large UTF-8 JSON, unknown operation before spawn, missing worker, guarded posting without intent, timeout process cleanup, invalid worker JSON, invalid token before body validation, and health worker availability.
- [x] 3.3 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 3.4 Run `GOOS=windows GOARCH=amd64 go build -ldflags "-H windowsgui" -o /tmp/qa-mcp-host-agent.exe .` under `host-agent/windows-display-agent`.
- [x] 3.5 Run PowerShell installer syntax verification when `pwsh` is available; otherwise record the Linux workspace gap.
- [x] 3.6 Run `openspec validate host-agent-com-execute-endpoint --strict`.
- [x] 3.7 Run `git diff --check`.
- [x] 3.8 Create `.artifacts/openspec/host-agent-com-execute-endpoint/verification-summary.md` with retained command outcomes and matrix evidence.
- [x] 3.9 Run the 1C verification matrix checker in archive-gate mode.

## 4. OpenSpec Handoff

- [x] 4.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into the main spec before archive.
- [x] 4.2 Prepare the completed change for archive with validation evidence.
- [x] 4.3 Keep protocol capture/replay evidence index updates as N/A because the change adds no new native TestClient protocol claim.

## Verification Notes

- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode preflight` passed and wrote `.artifacts/openspec/host-agent-com-execute-endpoint/matrix-preflight.json`.
- `go test ./...` passed under `host-agent/windows-display-agent`.
- `GOOS=windows GOARCH=amd64 go build -ldflags "-H windowsgui" -o /tmp/qa-mcp-host-agent.exe .` passed under `host-agent/windows-display-agent`.
- `pwsh` is not installed in this Linux workspace, so PowerShell installer syntax parsing could not run here; installer behavior was reviewed and left for the paired Windows E2E handoff.
- `openspec validate host-agent-com-execute-endpoint --strict` passed.
- `git diff --check` passed.
- `uv run --with pytest --with pyyaml pytest` passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` passed.
- `uv run --with pytest --with pyyaml pytest -m smoke` selected zero tests (`693 deselected / 0 selected`), so no smoke test failed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode archive` passed and wrote `.artifacts/openspec/host-agent-com-execute-endpoint/matrix-archive.json`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/com/execute` bridge for live-mcp COM WorkerRequest | Fake-worker Go tests plus cross-compiled Windows host-agent build; real COM smoke delegated to paired Windows/live-mcp E2E | scenario_file, scenario_log, runtime_apply_log | `.artifacts/openspec/host-agent-com-execute-endpoint/verification-summary.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real COMConnector registration and external-connection license checks cannot be executed in this Linux workspace and are owned by the paired live-mcp/root E2E delivery. |
