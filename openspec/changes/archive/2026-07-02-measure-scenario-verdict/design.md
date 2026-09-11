## Context

`measure_scenario` wraps a live debug-protocol run: it launches a debug-enabled TestClient, starts 1C performance
measurement, calls `mcp_server.run_scenario`, drains debug events, stops measurement and returns
`{ok, scenario_ok, perf_ok, report, report_text}`.

The scenario runner returns the stable `ScenarioResult.to_dict()` shape:

```text
{scenario, status, duration_sec, started_at, steps}
```

There is no `ok` key. The current implementation uses `bool(res.get("ok", res))`, so any non-empty result dict becomes
`scenario_ok: true`.

## Decision

Use the scenario result's `status` field as the single source of truth:

```python
scenario_ok = isinstance(res, dict) and res.get("status") == "passed"
```

Do not keep the old non-dict truthiness fallback. A malformed return from `run_scenario` is not a passed scenario and
must not become green.

## Verification Strategy

The bug is offline-reproducible. Unit tests will monkeypatch the live-only pieces in `measure_scenario`:

- `load_env_file`, `TestClientTarget.from_env`, `launch_test_client`;
- `subprocess.Popen` / `subprocess.run`;
- `DebuggerSession` so the code path obtains synthetic measure events;
- `mcp_server.run_scenario` to return failed and passed `ScenarioResult.to_dict()` payloads.

The test asserts that the returned `scenario_ok` follows `status` while the existing report keys remain present.

## Runtime And Safety

No live TestClient, Apache control, 1C debugger process or file infobase is used by the new tests. The production code
path still performs the same cleanup and Apache restart behavior; only the verdict calculation changes.

## Open Questions

None.
