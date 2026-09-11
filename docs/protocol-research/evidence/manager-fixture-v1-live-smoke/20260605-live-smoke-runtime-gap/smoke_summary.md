# Manager Fixture V1 Live Smoke

Run id: `20260605-live-smoke-runtime-gap`

Status: `provider-gapped`

Smoke subset selected from the reviewed V1 catalog:

- `tm-v1-active-window`
- `tm-v1-active-form`
- `tm-v1-field-version`

Command:

```powershell
.\tools\protocol-research\run_protocol_capture.ps1 `
  -Scenario manager-fixture-v1-readonly `
  -ManagerFixtureV1Smoke `
  -RunId 20260605-live-smoke-runtime-gap `
  -ProxyPort 15382
```

Outcome:

- The runner failed closed during preflight because the default Vanessa EPF is
  absent:
  `releases\vanessa\single\vanessa-automation-single-51f920f-windows-screenshot-fixes.epf`.
- No TestClient, proxy or manager PID was started; cleanup scope is empty.
- The generated manager manifest is bounded to the three-command smoke subset.
- `case_events.jsonl` exists but is empty because the manager harness did not
  run.
- The join analyzer produced three non-accepted corpus rows and three
  unresolved join rows with reason `no_before_event`.
- Replay/direct Python-manager proof was not attempted because there was no
  joined range or live traffic.

Reviewed evidence:

- Runtime capture directory:
  `runtime/protocol-research/captures/20260605-live-smoke-runtime-gap/`
- Join report:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-smoke-runtime-gap/frame_join_report.md`
- Corpus rows:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-smoke-runtime-gap/corpus_cases.jsonl`

Gate:

- Full V1 catalog expansion remains blocked.
- Required next action: restore or provide a Vanessa EPF/runtime profile, rerun
  this three-command smoke, then require at least one joined row with a
  non-null range, request size, response size and normalized hash before
  broadening to the full 11-command catalog.

No live protocol mapping is accepted from this run.
