## Context

The incident in `docs/qa-mcp-connection-issues-2.md` shows a Windows
PowerShell manual JSON-RPC request where the intended navigation link
`e1cib/list/Справочник.Валюты` reached qa-mcp/1C as
`e1cib/list/??????????.??????`. The same request worked when the body was sent
as UTF-8 bytes with an explicit UTF-8 JSON content type.

qa-mcp has two HTTP-relevant paths:

- direct `QA_MCP_TRANSPORT=http`, served by `src/qa_mcp/mcp_server.py` through
  FastMCP's streamable HTTP app;
- the protected Docker model-B path, where `ai-mcp-proxy serve-http` owns the
  external HTTP request and forwards MCP messages to `qa-native-mcp` over stdio.

This change hardens the qa-mcp-owned direct HTTP path and adds a tool-level echo
diagnostic that works on both direct HTTP and proxy/stdin paths after JSON-RPC
parsing.

## Goals / Non-Goals

**Goals:**

- Reject non-UTF-8 direct HTTP JSON bodies before tool dispatch.
- Expose a simple echo diagnostic for received `open_link` and Cyrillic values.
- Flag likely mojibake/replacement text in the diagnostic result.
- Update active Windows JSON-RPC examples to use UTF-8 bytes plus
  `application/json; charset=utf-8`.

**Non-Goals:**

- Do not change TestClient wire frames, capture templates or navigation replay.
- Do not replace or modify `ai-mcp-proxy` in this qa-mcp change.
- Do not require live 1C runtime for the offline acceptance proof.

## Decisions

1. Add a small ASGI middleware around FastMCP's direct streamable HTTP app.
   The middleware checks JSON-like POST bodies before Starlette/FastMCP parses
   them. It rejects explicit non-UTF-8 charsets and invalid UTF-8 bytes, then
   replays the accepted body to the downstream app.

2. Keep the echo diagnostic at the MCP tool layer. The tool receives already
   parsed values, returns them unchanged, and adds heuristic warnings for
   replacement characters (`U+FFFD`) or long runs of question marks in values.
   This makes the diagnostic useful even when the HTTP boundary is owned by
   `ai-mcp-proxy`.

3. Keep documentation examples aligned with the incident. PowerShell examples
   that contain Cyrillic JSON-RPC payloads should use
   `[System.Text.Encoding]::UTF8.GetBytes(...)` and
   `-ContentType "application/json; charset=utf-8"`.

## Risks / Trade-offs

- Direct HTTP middleware does not protect the Docker proxy path. Mitigation:
  the echo diagnostic still flags corrupted values after parsing, and the
  runbooks force UTF-8 bytes for manual proxy requests.
- Question-mark detection is heuristic. Mitigation: warnings are advisory and
  never rewrite caller values.
- Direct HTTP body buffering adds small memory overhead. Mitigation: MCP
  JSON-RPC bodies are small diagnostics/control payloads in this product path.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | JSON-RPC `open_link` diagnostics before `read_list_grid`/`read_form_descriptor` troubleshooting | Offline diagnostic tool calls with good Cyrillic and mojibake links | `qa_testclient_bundle` equivalent via pytest summary for echo/result shape | `.artifacts/openspec/jsonrpc-navlink-utf8-hardening/20260707T200219Z/pytest-summary.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Low: live 1C is not needed to prove argument echoing. |
| Delivery or runtime apply | Direct HTTP MCP request-body charset gate | ASGI middleware tests for UTF-8, non-UTF-8 charset and invalid bytes | pytest output and retained summary | `.artifacts/openspec/jsonrpc-navlink-utf8-hardening/20260707T200219Z/http-utf8-gate.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Medium: Docker proxy body rejection remains owned by `ai-mcp-proxy`. |
| Delivery docs/runbook | Windows PowerShell JSON-RPC examples | Docs sweep for `Invoke-WebRequest` JSON-RPC bodies | grep/static diff review plus OpenSpec validation | `.artifacts/openspec/jsonrpc-navlink-utf8-hardening/20260707T200219Z/docs-sweep.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Low: future docs can still add bad examples without tests unless covered by static checks. |
| Managed form layout | Live Windows `read_list_grid` with Cyrillic `open_link` | Optional model-B smoke against a Windows host/TestClient | MCP transcript showing echo and form/list result | `.artifacts/openspec/jsonrpc-navlink-utf8-hardening/20260707T200219Z/windows-model-b-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, GUI desktop or user infobase is available inside this Linux workspace. | First Windows confirmation should run on the incident contour. |
