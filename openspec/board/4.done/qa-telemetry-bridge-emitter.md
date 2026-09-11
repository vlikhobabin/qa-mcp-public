# QA telemetry bridge emitter (qa-mcp → suite trace store)

## Status
4.done

## Owner
qa-mcp runtime

## OpenSpec Stage
archived

## Source
- Root E2E 0→6 trace/logging analysis (2026-07-01/02), gap #3 (qa_bridge).
- Suite contract already exists: `agent-core/openspec/specs/qa-telemetry-bridge/spec.md`
  and parity card `agent-core/openspec/board/4.done/f6-08-qa-mcp-telemetry-and-evidence-parity.md`.

## Summary
qa-mcp emits **no** semantic telemetry into the suite trace store. In the E2E
retro, `observed_qa_bridge_count == 0` despite 18 qa-mcp proxy calls: the MCP
proxy records only generic `mcp_proxy_observation` rows (transport: method,
tool, latency, ok), while the semantic **QA telemetry bridge** layer — what QA
actually verified in the UI (subject, status, duration, retained evidence path) —
produced nothing. The retrospective's `QA Bridge Observations` section is empty
and no UI/BDD evidence flows into retrospective analysis.

Verified: the **agent-core ingestion side is complete** and validated by
`agent-core/scripts/smoke_ai_retrospective_qa_bridge.py`; it consumes a
`qa_telemetry_bridge` observation from any trace event payload. **The entire gap
is a missing emitter in qa-mcp** — a whole-repo grep of `/opt/ai-dev-suite-for-1c/qa-mcp`
for `qa_bridge` / `qa_telemetry_bridge` / `bridge_observation` / `ai-trace` /
`append_event` returns no source hits. No agent-core change is required for the
happy path.

## Current Triage (2026-07-06)

Still current. A repo grep over qa-mcp runtime/test/doc surfaces finds no
implemented `qa_telemetry_bridge` emitter or trace-store append path owned by
qa-mcp; the only concrete contract remains the agent-core smoke/retro ingestion
side referenced below. Keep this card in backlog until qa-mcp emits bounded
semantic QA observations under an active suite trace.

## Contract (what to emit)
An ordinary trace event whose payload carries `qa_bridge_observation` (ingested
by `agent-core/scripts/ai_retrospective_telemetry.py:724+`; kind constant
`QA_BRIDGE_OBSERVATION_KIND` in `ai_retrospective_common.py:43`). Canonical shape
(see `smoke_ai_retrospective_qa_bridge.py:114-134`):

```
{ "qa_bridge_observation": {
    "kind": "qa_telemetry_bridge",              # REQUIRED, exact value
    "subject": "scenario_outcome|readiness|active_window|…",
    "status": "ok|warn|fail|skipped|degraded",
    "duration_ms": 13,                          # falls back to row latency_ms
    "retained_evidence_path": ".artifacts/qa/<subject>.json",
    "sensitivity_class": "local_path",
    "provider_id": "qa-mcp",                    # → owner bucket `qa`
    "tool_name": "qa.testclient.bridge.<subject>",
    "owner_path": "/opt/ai-dev-suite-for-1c/qa-mcp",
    "error_class": "…", "error_summary": "…"    # on failure only
} }
```

Bounded-evidence rule (spec scenario "keeps evidence bounded"): store a **retained
path or sanitized summary only** — never raw screenshots, live data or customer
payloads.

## Context / evidence (qa-mcp scaffolding to reuse)
- Report/status/duration source: `qa-mcp/src/qa_mcp/scenario/reporting.py`
  (`junit_xml` `:53`, `write_allure_results` `:86`; per-scenario status +
  durations already computed) → best hook for `subject=scenario_outcome`.
- Evidence paths: `qa-mcp/src/qa_mcp/protocol/evidence.py` (`evidence_path` /
  `probe_evidence_paths`, repo-relative helpers `:61-235`) → `retained_evidence_path`.
- Screenshots: `qa-mcp/src/qa_mcp/protocol/screenshot.py`; JSONL writer
  `qa-mcp/src/qa_mcp/protocol/session.py:72`.
- Tool endpoints that produce semantic outcomes:
  `qa-mcp/src/qa_mcp/mcp_server.py` — `run_scenario`, `measure_scenario`,
  `write_test_report` (`:1359`), `capture_screenshot`, `get_test_results`, and
  verification summaries (`_evidence_ok` `:308`; status/ok/reason/`artifact_path`
  `:350-423`).
- Trace target plumbing (already present because qa-mcp runs behind the proxy):
  resolve `workspace` + `trace_id` from the proxy env / context file —
  `AI1C_MCP_PROXY_WORKSPACE`, `AI1C_MCP_PROXY_TRACE_ID` / `AI1C_TRACE_ID`,
  `AI1C_MCP_PROXY_TRACE_CONTEXT_FILE` (see `agent-core/scripts/ai_mcp_proxy.py:269-274`).

## Proposed design (best-effort, to be finalized in `$opsx-ff`)
1. **Bridge emitter module** in qa-mcp that builds a `qa_telemetry_bridge`
   observation from an existing outcome (scenario result, report write,
   screenshot capture, verification summary), filling subject/status/duration/
   retained_evidence_path/provider_id/owner_path, and error_class/summary on
   failure. Keep evidence bounded.
2. **Transport.** Prefer importing `append_event` from
   `agent-core/scripts/ai_trace_store.py` if agent-core is importable in the
   qa-mcp runtime; otherwise shell out to `agent-core/bin/ai-trace append
   --type evidence --payload-json '{"qa_bridge_observation": {…}}'`. Resolve
   `workspace`/`trace_id` from the proxy env/context file above; **no-op safely**
   when no trace context is present (so non-traced runs are unaffected).
3. **Wire-in points.** Emit after `run_scenario` / `measure_scenario`,
   `write_test_report`, `capture_screenshot`, and the verification-summary
   builders in `mcp_server.py`, plus the report path in `scenario/reporting.py`.
4. **Owner metadata** always set (`provider_id=qa-mcp`,
   `owner_path=/opt/ai-dev-suite-for-1c/qa-mcp`) so ingestion buckets to `qa` and
   avoids the `qa_bridge_missing_owner_metadata` diagnostic.

## Change Set
- `qa-telemetry-bridge-emitter`:
  `openspec/changes/archive/2026-07-30-qa-telemetry-bridge-emitter/`

## Change 1: `qa-telemetry-bridge-emitter`

### Why
The retrospective pipeline can grade QA bridge expectations, but qa-mcp does
not emit the semantic observation yet.

### Goal
Add a qa-mcp emitter that writes bounded `qa_telemetry_bridge` observations to
an active suite trace without affecting non-traced runs.

### Scope
- Emitter module and trace-context resolution.
- Scenario/report/screenshot/verification-summary wire-in.
- Offline tests and a retained trace append smoke.
- No agent-core ingestion changes unless implementation proves the contract is
  missing.

### Acceptance
- A qa-mcp scenario/report/screenshot/verification run under an active suite
  trace appends at least one `qa_telemetry_bridge` observation.
- Emitted observations carry qa-mcp owner metadata and bounded evidence paths or
  summaries only.
- Missing or invalid trace context is a safe no-op and does not change normal
  tool results.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-30-qa-telemetry-bridge-emitter/`

## Acceptance
- A qa-mcp scenario/report/screenshot/verification run under an active suite
  trace appends ≥1 `qa_telemetry_bridge` observation; the agent-core retro then
  reports `QA Bridge Observations` count > 0 bucketed under owner `qa`, with no
  `qa_bridge_missing_owner_metadata` / `qa_bridge_missing_support` diagnostic.
- Evidence stays bounded (retained path/summary only; no raw screenshots/live
  data in the payload).
- Runs with no trace context are unaffected (safe no-op).
- qa-mcp `uv run pytest` and the new smoke pass; `agent-core/scripts/smoke_ai_retrospective_qa_bridge.py`
  still passes against a real emitted event (optional cross-check).

## Result
Implemented. qa-mcp now has a bounded semantic telemetry bridge emitter in
`src/qa_mcp/telemetry_bridge.py`, wires scenario/report/screenshot and
persistence/cleanup verification outcomes through `src/qa_mcp/mcp_server.py`,
and preserves non-traced runs as safe no-ops.

The component OpenSpec change is synced and archived:
`openspec/changes/archive/2026-07-30-qa-telemetry-bridge-emitter/`.

Reviewed payload commit before final card metadata was `f099c8d`; card
finalization is amended into the local publish commit. Push status `skipped` on
`main`/`origin`.

## Verify
- RED: `uv run pytest -q tests/test_telemetry_bridge.py
  tests/test_mcp_server.py::test_record_result_emits_qa_bridge_observation
  tests/test_mcp_server.py::test_write_test_report_emits_qa_bridge_observation
  tests/test_mcp_server.py::test_capture_screenshot_emits_qa_bridge_observation`
  failed during collection because `qa_mcp.telemetry_bridge` did not exist.
- Focused GREEN: same command passed, `7 passed`.
- Broader focused suite: `uv run pytest -q tests/test_telemetry_bridge.py
  tests/test_mcp_server.py tests/test_reporting.py` passed, `125 passed`.
- Full offline suite: `uv run pytest -q` passed, `860 passed`.
- `openspec validate qa-telemetry-bridge-emitter --strict` passed before archive.
- `openspec validate qa-mcp-telemetry-bridge --strict` passed after spec sync.
- `openspec validate --all --strict` passed after archive, `19 passed, 0 failed`.
- `git diff --check` passed.
- Real trace append smoke: trace
  `trc_2043f056ef0a42968f032b8f919d512f`, evidence event
  `evt_34da5dea618147bba78d2d439b4fb48f`, JSONL mirror
  `.ai/traces/trc_2043f056ef0a42968f032b8f919d512f/events.jsonl`; the event
  contains `qa_bridge_observation.kind: "qa_telemetry_bridge"` and strict
  qa-mcp owner metadata.

## Next
- done

## Related
- Suite contract: `agent-core/openspec/specs/qa-telemetry-bridge/spec.md`; parity
  card `agent-core/openspec/board/4.done/f6-08-qa-mcp-telemetry-and-evidence-parity.md`.
- agent-core sibling: `telemetry-session-lifecycle-and-current-policy.md` — once
  qa-mcp emits, its `current` policy begins to grade `expected_qa_bridge`.
- Root memory: `next-session-trace-logging-analysis`.
- Main spec: `openspec/specs/qa-mcp-telemetry-bridge/spec.md`.
- Delivery manifest:
  `.runtime/changerail/delivery-manifests/qa-telemetry-bridge-emitter.json`.

## Log
- 2026-07-02 card created from the E2E trace/logging analysis (gap #3, qa_bridge).
- 2026-07-06 triage: still relevant; no qa-mcp emitter implementation found.
- 2026-07-30T00:00:00Z `$changerail-ff` created
  `openspec/changes/qa-telemetry-bridge-emitter/` and accepted the card for
  component delivery.
- 2026-07-30T00:00:00Z `$changerail-do` started implementation.
- 2026-07-30T06:59:11Z implemented the emitter and MCP hooks, synced
  `qa-mcp-telemetry-bridge`, archived
  `2026-07-30-qa-telemetry-bridge-emitter`, and completed offline pytest,
  OpenSpec, whitespace and real trace append smoke verification.
- 2026-07-30T07:16:00Z publish finalized card into `4.done`; reviewed payload
  commit before final card metadata was `f099c8d`; push status `skipped`.
