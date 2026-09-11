# Card 118 multi-version release evidence — 2026-08-02

## Outcome

GREEN. One current model-A image completed the canonical Agent/MCP HTTP
attach/read path against both supported live platform baselines:
`8.3.27.2130` and `8.5.1.1343`. The run retained no credentials, raw form
values, infobases, captures, or large platform logs.

## Artifact and route

- Image: `qa-mcp:card118-current`
- Image identity:
  `sha256:330509dc2114519d637ea2acc8a25e967d7b0b07c2c9ed15e68112ddba27aa2e`
- Delivery model: Linux host-platform model A for both baselines
- Endpoints: `http://127.0.0.1:8003/mcp` for 8.3 and
  `http://127.0.0.1:8005/mcp` for 8.5
- MCP negotiation: protocol `2025-11-25`, session id present, 68 tools

The retained Windows 8.3 model-B evidence and the earlier 8.5 Linux protocol
grid were audited first. They remain supporting evidence, but neither replaced
the new proof: the old Windows HTTP run used the historical trailing-slash
route, while the 8.5 grid did not cross the Agent/MCP HTTP boundary.

## Observed release smokes

| Live platform | Protocol data | Attach | Read-only result | Cleanup |
| --- | --- | --- | --- | --- |
| `8.3.27.2130` | `_bundled/8.3` | `launch_test_client`: alive and listening; ownership marker retained | `read_form_descriptor` opened `Справочник.Товары`; 67 elements, values not retained | owned TestClient and Xvfb stopped; TPort/container absent; Apache restored to `active` |
| `8.5.1.1343` | `_bundled/8.3` fallback | `launch_test_client`: alive and listening; ownership marker retained | `read_form_descriptor` opened `Справочник.Товары`; 67 elements, values not retained | owned TestClient and Xvfb stopped; TPort/container absent; Apache remained `active` |

The 8.5 model-A dependency check ran against
`/opt/1cv8/x86_64/8.5.1.1343/1cv8` and reported zero missing libraries. The
8.3 build exposes the already-known bundled-libgcc symbol mismatch under raw
`ldd`; the actual launch profile autodetected
`/lib/x86_64-linux-gnu/libgcc_s.so.1`, after which `ldd` had no missing result
and the smoke passed.

## Runtime defects found and closed

The first current-image attempt exposed two packaging-path bugs before any 1C
write operation:

1. The JSON-RPC UTF-8 middleware replayed endless empty ASGI request bodies,
   starving the Streamable HTTP SSE response after an HTTP 200. The replay now
   forwards the real downstream disconnect; a regression test records the RED
   and GREEN behavior.
2. A wheel/container launch wrote the TestClient ownership marker below
   `QA_MCP_HOME`, but stateless cleanup searched beside site-packages. The
   default lookup now follows `QA_MCP_HOME`; lifecycle tests cover both that
   default and the explicit ownership-root override.

The final image above includes both corrections. Its final 8.3 and 8.5 runs
completed launch, read, ownership-checked teardown, and environment cleanup.

## Detailed local evidence

Sanitized machine-readable summaries for this run are under
`.artifacts/openspec/reconcile-qa-mcp-8-3-8-5-release-evidence/20260802T002132Z/`.
That ignored artifact tree contains only route/preflight and outcome summaries;
this curated report is the retained repository evidence.
