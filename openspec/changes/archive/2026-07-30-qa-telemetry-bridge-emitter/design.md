## Context

qa-mcp already computes semantic QA outcomes in `mcp_server.py`: scenario
results are appended to `_RESULTS_LOG`, test reports are written from that log,
screenshots return retained paths, and verification-summary helpers return
status plus artifact paths. The suite proxy writes generic MCP observations,
but those rows cannot tell the retrospective what QA actually verified.

The agent-core ingestion contract is already present in
`agent-core/openspec/specs/qa-telemetry-bridge/spec.md`: a trace event payload
containing `qa_bridge_observation.kind == "qa_telemetry_bridge"` is summarized
as QA bridge telemetry when it carries bounded owner/evidence metadata.

## Goals / Non-Goals

**Goals:**

- Emit semantic QA bridge observations from qa-mcp when an active suite trace
  context is available.
- Keep payloads bounded: retained path, status, subject, duration and sanitized
  summaries only.
- Preserve non-traced behavior as a silent no-op.
- Verify implementation offline with a mock appender and an optional real trace
  store smoke.

**Non-Goals:**

- Changing agent-core ingestion or retrospective parsing.
- Capturing raw screenshots, live data, UI trees or customer payloads into the
  trace event payload.
- Requiring live 1C TestClient execution for the component verification floor.

## Decisions

1. **Add a small qa-mcp-owned emitter module.** The module owns context
   resolution, observation normalization and append dispatch. This keeps
   `mcp_server.py` hook points small and allows focused offline tests without
   importing the full MCP server.

2. **Resolve context from proxy state.** The emitter reads workspace and trace id
   from `AI1C_MCP_PROXY_WORKSPACE`, `AI1C_MCP_PROXY_TRACE_ID`, `AI1C_TRACE_ID`
   and `AI1C_MCP_PROXY_TRACE_CONTEXT_FILE`. The context file path is treated as
   optional JSON and can supply `workspace`, `trace_id` and `turn_id`. Missing
   or invalid context returns a structured no-op result.

3. **Prefer direct append, fall back to CLI.** When
   `/opt/ai-dev-suite-for-1c/agent-core/scripts/ai_trace_store.py` is importable,
   call `append_event` directly. If it is not importable, use
   `agent-core/bin/ai-trace append`. Both paths write an `evidence` event with
   layer `qa`, category `qa_telemetry_bridge`, provider `qa-mcp`, owner path
   `/opt/ai-dev-suite-for-1c/qa-mcp`, and `mirror_jsonl=true`.

4. **Wire after existing outcomes.** Emit after scenario result recording,
   report writing, screenshot capture, and selected verification-summary
   builders. Failures in the telemetry path must not change the tool result;
   the tool may include bounded `qa_telemetry_bridge` diagnostics in its own
   result only when useful for tests.

## Risks / Trade-offs

- Trace store import path differs in packaged/runtime layouts -> resolve the
  sibling agent-core path first, then fall back to `AI1C_AGENT_CORE_HOME` and
  `ai-trace` on `PATH`.
- Payloads could grow accidentally -> normalize observations through an
  allowlist and truncate error summaries.
- Silent no-op could hide misconfiguration -> return structured emitter results
  in tests and optionally surface a compact diagnostic when a context file is
  invalid, while keeping ordinary no-context runs unaffected.

## Migration Plan

1. Add the emitter module and offline tests.
2. Wire existing qa-mcp endpoints to call the emitter after successful outcome
   construction.
3. Run focused tests, `openspec validate`, `git diff --check` and a real trace
   append smoke.
4. Archive the change and let the root card prove retrospective visibility.
