## 1. Runtime Preparation

- [x] 1.1 Define the focused pending-row runtime command or wrapper for manager
  fixture V1 read-only probes.
- [x] 1.2 Record endpoint readiness evidence before any row probe runs.
- [x] 1.3 Preserve run id, TestClient port, proxy port, fixture route and owned
  PIDs in a compact reviewed summary.
- [x] 1.4 Record a provider/runtime gap when no clean endpoint can be started or
  attached.
- [x] 1.5 Confirm raw runtime output remains under ignored
  `runtime/protocol-research/` paths.

## 2. Verification

- [x] 2.1 Run PowerShell parser validation for any changed `.ps1` runner.
- [x] 2.2 Run the focused runtime preflight on Windows or retain the provider
  gap summary.
- [x] 2.3 Confirm cleanup stops only runner-owned PIDs.
- [x] 2.4 Run `openspec validate prepare-manager-fixture-v1-pending-probe-runtime --strict`.

## Evidence

- Runtime preflight command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\protocol-research\run_protocol_capture.ps1 -Scenario manager-fixture-v1-readonly -RunId 20260606-pending-readonly-runtime-preflight -ManagerFixtureV1CaseId tm-v1-active-window -StartupTimeoutSec 10 -ManagerReadyTimeoutSec 15 -ManagerHarnessTimeoutSec 15`.
- Runtime status: `runtime_gap`; missing asset: `Vanessa EPF`.
- Runtime evidence:
  `runtime/protocol-research/captures/20260606-pending-readonly-runtime-preflight/capture_summary.json`.
- Reviewed evidence:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-readonly-runtime-preflight/runtime_summary.md`.
- Cleanup evidence: preflight exited before process startup; `pids` and
  `cleanup` are empty in `capture_summary.json`; no `1cv8` process or lab TCP
  listener was observed after the run.
- Parser validation:
  `tools\protocol-research\run_protocol_capture.ps1` parsed successfully with
  `System.Management.Automation.Language.Parser`.
- Raw output policy: generated runtime files remain under ignored
  `runtime/protocol-research/`; compact reviewed summary is under
  `docs/protocol-research/evidence/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Pending-row TestClient/proxy/manager startup and cleanup | Windows-native preflight/run command with selected run id and ports | `scenario_log`, `runtime_apply_log`, `cleanup_evidence` | `.artifacts/openspec/prepare-manager-fixture-v1-pending-probe-runtime/<run-id>/runtime-preflight/` | required | `project:qa-mcp` | N/A | High: local 1C startup or port ownership can block live probes |
| Managed form layout | Client fixture V1 form opened for probe readiness | Active window/form proof for the controlled fixture route | `active_window`, `form_tree` or provider gap summary | `.artifacts/openspec/prepare-manager-fixture-v1-pending-probe-runtime/<run-id>/fixture-open/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI proof may be unavailable when Vanessa/live providers are offline |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change prepares runtime evidence and should not edit BSL source | Low: no BSL behavior changes are planned |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
