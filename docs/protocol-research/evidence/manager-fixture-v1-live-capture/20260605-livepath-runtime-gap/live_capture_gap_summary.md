# Manager Fixture V1 Live Capture Runtime Gap

Run id: `20260605-livepath-runtime-gap-2`

Command:

```powershell
.\tools\protocol-research\run_protocol_capture.ps1 `
  -Scenario manager-fixture-v1-readonly `
  -RunId 20260605-livepath-runtime-gap-2 `
  -ProxyPort 15382
```

Result:

- Capture runner status: `runtime_gap`.
- Missing runtime asset: `Vanessa EPF`.
- No TestClient, proxy or manager PID was started; `capture_summary.json`
  records an empty `pids` object.
- `manager_harness_manifest.json` was generated from the reviewed 11-command
  catalog.
- `manager_harness_invocation.json` records the intended custom manager
  harness path and entrypoint:
  `DataProcessor.ProtocolFixtureTestManager.Form.ManagerHarness` /
  `TM_RUN_FROM_CAPTURE_RUNNER_V1`.
- `manager_harness_invocation.feature.txt` contains the generated Vanessa
  `execute_step_from_text` payload that would pass `run_id`, proxy port,
  manifest path and output directory to the harness.
- `case_events.jsonl` exists as an empty file because no live manager harness
  command was executed.
- `manager_harness_result.json` status is `runtime_gap`; it is not accepted
  protocol evidence.

Validation:

- PowerShell parser check for `run_protocol_capture.ps1`: passed.
- `manager-fixture-v1-readonly -DryRun` after live-path changes: passed with
  run id `20260605-livepath-dryrun`.
- Non-dry-run preflight with missing EPF: passed as fail-closed runtime gap.
- Runtime JSON artifacts parse with Windows PowerShell `ConvertFrom-Json`.

Runtime artifacts are retained under:

- `runtime/protocol-research/captures/20260605-livepath-runtime-gap-2/`

No live TCP traffic, frame ranges, replay result or accepted protocol mapping
is claimed by this evidence.
