## Context

The COM bridge intentionally bypasses `writeJSON` on success because the worker
already writes a valid UTF-8 WorkerResponse JSON document and the host-agent
must return it without re-encoding, truncation, or JSON restructuring. That
direct write currently sets `Content-Type: application/json`, while the shared
JSON helper now sets `application/json; charset=utf-8`.

## Goals / Non-Goals

**Goals:**
- Make successful `/com/execute` responses declare UTF-8 JSON explicitly.
- Keep raw worker stdout passthrough unchanged after the existing trim and
  `json.Valid` checks.
- Cover the header and non-ASCII body behavior with a focused Go test.

**Non-Goals:**
- Do not parse and re-emit worker responses through `writeJSON`.
- Do not change worker path resolution, allowlist, guarded posting intent,
  timeout handling, secret redaction, or health diagnostics.
- Do not run live COM, TestClient, or protocol capture/replay for this
  header-only change.

## Decisions

- Keep the raw `w.Write(result)` response path and change only the success
  `Content-Type` value.
  - Rationale: the prior COM endpoint contract requires byte-preserving worker
    passthrough; `writeJSON` would marshal a Go value and could alter formatting
    or byte layout.
  - Alternative considered: parse worker stdout into a map and call
    `writeJSON`; rejected because it violates the passthrough contract.
- Extend the existing large UTF-8 COM success test instead of adding an
  integration-only test.
  - Rationale: the fake worker already exercises the exact HTTP handler path on
    Linux with non-ASCII response bytes and without requiring Windows COM.

## Risks / Trade-offs

- Header-only coverage does not prove real `V83.COMConnector` behavior.
  Mitigation: live COM execution is unchanged and was covered by the prior COM
  endpoint card; this change only alters the HTTP response header.
- Some Go HTTP stacks may normalize or append header parameters.
  Mitigation: tests assert the response includes `charset=utf-8` and preserves
  the body bytes, not an unrelated header ordering detail.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/com/execute` HTTP response contract for live-mcp COM WorkerResponse JSON | Fake-worker Go test checks UTF-8 content type and non-ASCII raw body passthrough; live COM execution unchanged | scenario_file, scenario_log | `.artifacts/openspec/com-execute-utf8-content-type/verification-summary.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real COMConnector execution is outside this header-only change and remains covered by the earlier COM bridge delivery. |
