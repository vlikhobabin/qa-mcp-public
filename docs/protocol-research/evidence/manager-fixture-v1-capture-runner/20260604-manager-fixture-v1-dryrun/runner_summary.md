# Manager Fixture V1 Capture Runner Dry Run

Snapshot date: 2026-06-04.

## Scope

Change: `integrate-manager-fixture-v1-capture-runner`.

This evidence records the Windows-native capture runner scenario and dry-run
output contract. It does not claim a live 1C TestManager execution, visual UI
proof, frame range, normalized hash, replay result or accepted protocol
mapping.

## Runner Changes

- Scenario: `manager-fixture-v1-readonly`.
- Run id: `opsx-manager-fixture-v1-dryrun`.
- Ignored runtime directory:
  `runtime/protocol-research/captures/opsx-manager-fixture-v1-dryrun/`.
- The capture manifest records `runId`, `dryRun` and
  `livePathValidationSkipped`.
- `manager_harness_invocation.json` passes the shared run id, proxy
  TestClient port and runtime output directory to the manager harness contract.
- `manager_harness_manifest.json`, `case_events.jsonl` and
  `manager_harness_result.json` are written under the same runtime directory.
- Bootstrap and read-only phases are represented as separate event rows.

## Verification Notes

- PowerShell parser validation passed for
  `tools/protocol-research/run_protocol_capture.ps1`.
- Dry-run command passed:
  `.\tools\protocol-research\run_protocol_capture.ps1 -Scenario manager-fixture-v1-readonly -DryRun -RunId opsx-manager-fixture-v1-dryrun -ProxyPort 15382`.
- JSON parser validation passed for `capture_manifest.json`,
  `capture_summary.json`, `manager_harness_manifest.json`,
  `manager_harness_result.json`, `manager_harness_invocation.json` and
  `case_events.jsonl`.
- The dry-run reported `status=dry-run-ok` and wrote a manifest with six
  read-only commands.
- Dry-run did not start 1C, proxy or manager processes.
- The existing `finally` block still stops only the process handles created by
  the runner: TestClient, proxy and manager.

## Live Smoke Gap

The live smoke path could not be run in this workspace because the configured
Vanessa EPF is absent:

`releases/vanessa/single/vanessa-automation-single-51f920f-windows-screenshot-fixes.epf`

Both lab infobases are present (`C:\1C_BASES\vanessa_client` and
`C:\1C_BASES\vanessa_manager`). Earlier card evidence also records that the
manager fixture source was not deployed because EDT classified the manager
publish path as a full configuration reload and live COM access reported a
platform mismatch. The runner therefore keeps the live branch implemented but
records the current smoke as provider/runtime-gapped.

## Provider Gaps

```yaml
provider_gaps:
  - provider_id: project
    owner_path: C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp
    matrix_row: delivery_or_runtime_apply
    missing_evidence_type: live_manager_fixture_smoke
    observed_result: >
      The configured Vanessa EPF was not present, so non-dry-run TestManager
      startup cannot be executed from the capture runner in this workspace.
    retained_evidence: runtime dry-run output and OPSX trace trc_29bc39e061924329b4d257c49f7f502f
    residual_risk: >
      Medium: process startup, attach timing and manager harness invocation
      still need one live run after the EPF/runtime profile is restored.
  - provider_id: vanessa
    owner_path: /opt/vanessa-mcp-stack
    matrix_row: managed_form_layout
    missing_evidence_type: active_window_form_tree_screenshot
    observed_result: >
      Vanessa UI proof remains unavailable for this change because the
      project profile records vanessa-mcp as an expected unproxied provider
      gap and the manager harness cannot be started without the EPF.
    retained_evidence: OPSX trace trc_29bc39e061924329b4d257c49f7f502f
    residual_risk: >
      Medium: active-window and form-tree proof remains deferred to a live
      TestManager run.
```
