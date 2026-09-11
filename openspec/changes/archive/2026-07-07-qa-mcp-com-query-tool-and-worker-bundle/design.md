## Context

The current qa-mcp data tools are OData-oriented. In a Windows model-B setup
with a local file infobase and no OData publication, `assert_data`,
`assert_data_count`, and `role_data_matrix` cannot answer even a simple
catalog-row count. The Windows host can answer the same question through
`V83.COMConnector`, and the qa-mcp host-agent already exposes authenticated
`/com/execute` to run the frozen `ai-com-worker.exe` produced by live-mcp.

This change stays in qa-mcp ownership. It consumes the ready worker executable
as a release asset, exposes qa-mcp MCP tools over the existing host-agent bridge,
and adds host-agent diagnostics that are safe to run on Windows. It does not
change live-mcp worker source or raw TestClient protocol capture/replay.

## Goals / Non-Goals

**Goals:**

- Add read-only `query_com` and `assert_com_count` MCP tools for file infobases.
- Reuse host-agent `/com/execute` for actual COM query execution.
- Reject obvious write-shaped 1C query text before it leaves qa-mcp.
- Let standard release defaults supply `ai-com-worker.exe` so releases can bundle
  the worker without repeating `--com-worker-exe`.
- Make `com_worker` health impact explicit for COM-dependent flows.
- Add an authenticated host-agent COMConnector doctor that checks 64-bit
  registration and optionally performs a read-query smoke on the Windows host.

**Non-Goals:**

- No write, post, delete, fill, import, export, or mutation COM tool.
- No live-mcp source change; the ready worker remains externally produced.
- No raw capture update and no new protocol claim.
- No live Windows COM execution in the Linux qa-mcp lab run.

## Decisions

1. **Use `/com/execute` for query execution.**
   The worker bridge already constrains executable path, operation allowlist,
   timeout, token boundary, and UTF-8 JSON passthrough. The new MCP tools should
   build the WorkerRequest and normalize the WorkerResponse rather than adding a
   second query transport.

2. **Add a separate host-agent doctor endpoint for registration diagnostics.**
   The existing live-mcp worker does not implement registry/TypeLib inspection.
   Keeping the doctor in host-agent avoids cross-repo edits while keeping all
   registry, bitness, and `cscript.exe` smoke checks on the Windows host. The
   endpoint remains authenticated and accepts semantic inputs only.

3. **Treat read-only policy as a qa-mcp guardrail.**
   The MCP layer should reject obvious 1C query mutation verbs and dangerous
   external side-effect tokens before host transport. This is not a full parser;
   it is a fail-closed tripwire for common unsafe shapes. Ambiguous future
   mutation support must be a separate operator-intent-gated change.

4. **Use ignored release defaults for standard COM worker bundling.**
   `publish_self_hosted.sh` already loads ignored `.ai/release.env` files before
   parsing CLI arguments. A `COM_WORKER_EXE` default keeps standard publish
   commands simple while explicit `--com-worker-exe` remains the highest
   precedence path.

## Implementation Notes

- Add a small Python host-agent COM client helper under `src/qa_mcp/` so MCP
  tools can share URL, token, timeout, request construction, response parsing,
  and secret-safe structured errors.
- Register `query_com`, `assert_com_count`, and `com_connector_doctor` in
  `src/qa_mcp/mcp_server.py`.
- Preserve the existing deprecated OData tools; COM tools are additive.
- Add host-agent `/com/doctor` with a semantic JSON request:
  `infobase_path`, optional `user`, `password`, optional `query`,
  `timeout_seconds`, and optional `prog_id`.
- On Windows, the doctor should inspect HKCR/HKLM registry views for ProgID,
  CLSID, `InprocServer32`, and TypeLib. The 64-bit TypeLib GUID observed in the
  field report is `{98AC3B5B-5323-418F-8F07-E32F231D2393}`.
- For smoke execution, generate and run a fixed temporary JScript through
  64-bit `cscript.exe` without shell expansion. Delete the temporary script on
  completion and redact infobase path/user/password from error details.
- Keep Linux tests deterministic by injecting fake host-agent HTTP responses and
  by testing host-agent doctor routing/policy without real COM.

## Risks / Trade-offs

- **Linux cannot execute real COMConnector smoke.** -> Keep the real Windows
  smoke as a recorded provider/environment gap and retain offline contract
  evidence in this repo.
- **The read-only query guard is lexical, not a 1C parser.** -> Block obvious
  unsafe verbs locally and keep all mutation support out of scope.
- **COM worker production remains in live-mcp.** -> Bundle only an explicitly
  supplied ready executable and document the affected health features when it is
  absent.
- **Doctor endpoint spawns a host process.** -> Use authenticated access,
  semantic request fields, fixed `cscript.exe`, temp files, timeout limits, and
  existing execution capacity limiting.

## Migration Plan

1. Operators can continue publishing non-COM releases without a worker.
2. To enable COM query flows, set `COM_WORKER_EXE=<path-to-ai-com-worker.exe>` in
   ignored release defaults or pass `--com-worker-exe`.
3. Bootstrap already downloads manifest-declared worker assets and passes them
   to the host-agent installer.
4. If COMConnector TypeLib registration is broken, run the doctor and follow the
   elevated `System32\regsvr32.exe` remediation command.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| live_data_read | `query_com`, `assert_com_count`, host-agent `/com/execute` WorkerRequest | Offline fake host-agent query and count assertions; read-only rejection test | scenario_file, scenario_log, data_assertion | `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/com-query-offline-evidence.json` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real Windows COM smoke is tracked in the separate blocked row. |
| delivery_runtime_apply | `publish_self_hosted.sh`, bootstrap handoff, host-agent health metadata | Focused release-script tests with fake worker asset and host-agent health tests | scenario_file, scenario_log, runtime_apply_log | `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/release-health-evidence.json` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | External release republish remains operator action. |
| runtime_diagnostic | host-agent COMConnector doctor endpoint and MCP wrapper | Offline host-agent doctor tests for TypeLib-missing, read-only query rejection, and green fake smoke | scenario_file, scenario_log | `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/com-doctor-offline-evidence.json` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Registry shape can vary by Windows install; real smoke gap is tracked separately. |
| windows_com_live_smoke | BIT.FINANCE file infobase `Справочник.Валюты` count through 64-bit COMConnector | Operator-run Windows host smoke after installing bundled worker and repairing TypeLib if needed | live_read_proof, data_assertion, scenario_log | `.artifacts/openspec/qa-mcp-com-query-tool-and-worker-bundle/20260707T190050Z/windows-com-live-smoke-gap.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Current Linux workspace cannot instantiate `V83.COMConnector`; delivery relies on offline bridge tests plus operator Windows smoke follow-up. |
| managed_form_layout | not_applicable | No managed form layout or UI command changes | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change adds host-side data/diagnostic tools, not form UI behavior. | No UI-specific residual risk beyond existing TestClient tools. |

## Provider Gaps

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | windows_com_live_smoke | live_read_proof | Real `V83.COMConnector` CreateObject/Connect/query cannot run in the Linux lab. | Retain offline host-agent and MCP tests in this delivery; run `com_connector_doctor` and `query_com` on the Windows BIT.FINANCE host after publishing. |
