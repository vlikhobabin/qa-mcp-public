# qa-mcp live-regression harness

**Roadmap card 111, item 3 (the keystone productization step).** The offline `pytest` suite proves qa-mcp encodes
the protocol correctly; it can never prove a real 1C TestClient still *accepts* what we send. That gap was
historically closed by one-shot, hand-run evidence scripts per board card. This harness turns those into a single,
repeatable, **gated** live run.

> One command boots a native `/TESTCLIENT`, exercises the LIVE-verified capabilities, compares against pinned
> expectations, emits JUnit/JSON/text reports and a non-zero exit code on any regression — so it is CI/cron-gateable.

## Run it

```bash
. .venv/bin/activate
python -m qa_mcp.regression \
  --odata-url "http://127.0.0.1:8316/vanessa_client/odata/standard.odata"
```

Defaults: env profile `.ai1c/vanessa-qa-mcp.env`, `127.0.0.1:15381`, reports under `runtime/live-regression/<UTC>/`
(git-ignored). Exit code is 0 only if every REQUIRED check passed.

Flags: `--include-write` (UI→DB roundtrip — **creates a lab record**), `--include-measure` (coverage/perf via the
debug protocol — slow, boots its own debug server), `--no-ui` (data-layer only, no boot), `--out`, `--host/--port`,
`--env`, `--wait-sec/--settle-sec`, `--max-ms` (perf assertion for the measure check), `--src-root` (config `.mdo`
root for the measure module-name resolver).

## Phases (the always-restart-Apache discipline)

The data-layer checks need Apache UP; the UI boot STOPS Apache. So the run is phased:

1. `data_pre` — Apache up, no client: OData data-layer asserts.
2. `ui` — boot `/TESTCLIENT` (stops Apache) → UI checks → **always** tear down in `finally` (restarts Apache).
3. `data_post` — Apache restored: the write-roundtrip's DB verification tail.
4. `measure` — standalone; `measure_scenario` owns its own debug client.

## The CORE check set (read-only, nightly-safe)

| check | capability (board card) |
| --- | --- |
| `preflight.protocol_drift` | version-resilience preflight (111 item 4) — informational; flags platform/template drift |
| `data_layer.banki` | data-layer assert via read-only OData (105) |
| `ui.assert_family` | the assert family through `run_scenario` on the live HomePage (103) — positive + negative |
| `ui.open_two_objects` | config-agnostic open of two different catalog main forms in one session (103) |
| `ui.read_descriptor` | capture-free live element enumeration of a form opened by nav-link (98 #1 / 106) |

Verified GREEN end-to-end on the lab `vanessa_client` (2026-06-22) — `evidence/card111-live-regression-2026-06-22/`.

## Protocol-version resilience (item 4)

The replayed captures are faithful to one platform protocol version. The `preflight.protocol_drift` check (and the
standalone `python -m qa_mcp.regression.versioning`) compares the live platform version + committed-template hashes
against the stamped baseline for the live version family (the per-version manifest
`config/protocol-capture-manifest-<version>.json`, e.g. `…-8.3.json`), so a red run is **diagnosed** ("platform
moved — refresh") not guessed. Stamp/refresh details: [`capture-refresh-runbook.md`](capture-refresh-runbook.md).

- `python -m qa_mcp.regression.versioning` — check drift (exit 1 on template/missing drift; add `--strict` to also
  fail on a platform-version bump).
- `python -m qa_mcp.regression.versioning --stamp` — re-baseline after a refresh or a blessed version bump.

## Architecture

- `src/qa_mcp/regression/harness.py` — pure, offline-tested orchestration core (`Check`, `CheckResult`,
  `RegressionReport`, `run_checks`). No lab dependency.
- `src/qa_mcp/regression/checks.py` — the curated live checks (call the real MCP tools; same targets the board-card
  evidence used). Add a capability check here as one `Check`.
- `src/qa_mcp/regression/__main__.py` — the phase-aware CLI (boot → run → report → teardown).
- `tests/test_regression_harness.py` — offline tests for the core + a transpile check that fails a Gherkin-phrasing
  drift *before* a slow live boot.

## Scheduling

Gate it in CI / cron on the lab host (the CORE set is side-effect-free). A red exit means a proven capability
regressed — the early signal the offline suite cannot give.
