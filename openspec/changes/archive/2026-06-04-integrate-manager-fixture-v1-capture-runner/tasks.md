## 1. Runner Scenario

- [x] 1.1 Inspect the existing Windows-native capture runner and identify the minimal scenario extension point.
- [x] 1.2 Add a manager fixture V1 read-only scenario that creates one shared `run_id` and runtime directory.
- [x] 1.3 Wire the TestClient connection through the TCP proxy and pass the proxy endpoint to the manager harness.
- [x] 1.4 Route `case_events.jsonl`, `manager_harness_result.json`, proxy traffic and 1C logs into the shared runtime directory.
- [x] 1.5 Label bootstrap/open-form traffic separately from read-only command cases.

## 2. Safety And Smoke

- [x] 2.1 Preserve owned-PID tracking for TestClient, proxy and manager processes.
- [x] 2.2 Add a dry-run or preflight path for manifest/output validation when live 1C startup is not available.
- [x] 2.3 Run a live smoke with a small read-only command subset through the proxy. Provider/runtime-gapped: the configured Vanessa EPF is absent, so the live branch is implemented but only dry-run evidence is retained for this change.
- [x] 2.4 Verify cleanup stops only PIDs created by the capture runner.
- [x] 2.5 Keep raw TCP data, full logs and generated run output under ignored `runtime/` paths.

## 3. Verification

- [x] 3.1 Run focused tests or script syntax checks for changed capture runner files.
- [x] 3.2 Run the manager fixture V1 capture smoke on Windows and retain the run summary. Provider/runtime-gapped: retained dry-run summary and live-smoke gap evidence instead of claiming a live 1C run.
- [x] 3.3 Run `openspec validate integrate-manager-fixture-v1-capture-runner --strict`.
- [x] 3.4 Run `openspec validate qa-mcp-protocol-lab --strict`.
- [x] 3.5 Run `git diff --check -- openspec/changes/integrate-manager-fixture-v1-capture-runner tools/protocol-research docs/protocol-research`.

## Verification Results

- PowerShell parser check passed for `tools/protocol-research/run_protocol_capture.ps1`.
- Dry-run passed:
  `.\tools\protocol-research\run_protocol_capture.ps1 -Scenario manager-fixture-v1-readonly -DryRun -RunId opsx-manager-fixture-v1-dryrun -ProxyPort 15382`.
- JSON parser check passed for the dry-run `capture_manifest.json`,
  `capture_summary.json`, `manager_harness_manifest.json`,
  `manager_harness_result.json`, `manager_harness_invocation.json` and
  `case_events.jsonl`.
- Reviewed evidence:
  `docs/protocol-research/evidence/manager-fixture-v1-capture-runner/20260604-manager-fixture-v1-dryrun/runner_summary.md`.
- Runtime dry-run output is ignored under
  `runtime/protocol-research/captures/opsx-manager-fixture-v1-dryrun/`.
- Live smoke was not run because the configured Vanessa EPF
  `releases/vanessa/single/vanessa-automation-single-51f920f-windows-screenshot-fixes.epf`
  is absent. The runner branch is implemented, and the gap is retained as a
  provider/runtime gap instead of a live-run claim.
- `openspec validate integrate-manager-fixture-v1-capture-runner --strict`
  passed.
- `openspec validate qa-mcp-protocol-lab --strict` passed.
- `git diff --check -- openspec/changes/integrate-manager-fixture-v1-capture-runner tools/protocol-research docs/protocol-research`
  passed with CRLF conversion warnings only.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Capture runner scenario starting TestClient, proxy and manager harness | Windows-native command plan, owned-PID model and shared run layout | `runtime_apply_log`, `scenario_log`, cleanup evidence | `runtime/protocol-research/captures/opsx-manager-fixture-v1-dryrun/`; `docs/protocol-research/evidence/manager-fixture-v1-capture-runner/20260604-manager-fixture-v1-dryrun/runner_summary.md` | provider-gap recorded | `project:qa-mcp` | Live startup blocked by missing configured Vanessa EPF; dry-run validates run layout without starting 1C | Medium: live process startup and attach timing still need one run after EPF/runtime profile restoration |
| Managed form layout | Client fixture form opened during bootstrap | Bootstrap phase evidence and active form proof | `active_window`, `form_tree`, `scenario_log` | `docs/protocol-research/evidence/manager-fixture-v1-capture-runner/20260604-manager-fixture-v1-dryrun/runner_summary.md` | provider-gap recorded | `/opt/vanessa-mcp-stack` | Vanessa UI proof cannot run without the configured EPF and remains an expected unproxied provider gap in this profile | Medium: bootstrap visual proof remains deferred |
| BSL-only module edit | Manager harness invocation surface consumed by runner | Compatibility check between runner arguments and 1C harness fields | `bsl_diagnostics`, `scenario_file` | `runtime/protocol-research/captures/opsx-manager-fixture-v1-dryrun/manager_harness_invocation.json`; `docs/protocol-research/evidence/manager-fixture-v1-readonly-contract/20260604-manager-fixture-v1-readonly-contract/command_catalog_summary.md` | source/dry-run verified with provider gap | `/opt/edt-lab`, `project:qa-mcp` | Runner integration changed only the PowerShell invocation contract; focused BSL diagnostics remain gapped by the prior EDT validation/tooling issues | Medium: command-line invocation details may need one live iteration |
| Migration or data repair | Business data and infobase data repair | N/A | N/A | N/A | N/A | `project:qa-mcp` | Runner integration must not modify business data or run data repair | Low: only runtime harness state is expected |
