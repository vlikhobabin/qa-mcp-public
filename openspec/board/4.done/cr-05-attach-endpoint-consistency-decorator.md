# CR-05 — Attach-endpoint consistency + tool decorator + local-boot guard

## Status
4.done

## Order Index
5

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Multi-agent code review 2026-07-02, findings A4 (arch), finding 5/6/7 (server),
  S3, plus server duplication items 1/4/5. Full report: `docs/code-review-2026-07-02.md`.

## Summary
`attach_test_client` records an active endpoint, but only ~16 of the ~41
endpoint-touching tools actually honor it — so after an attach, the other ~25
replay/action tools silently target `127.0.0.1:15381`, giving **split-brain
behavior inside one session** (reads follow the attach; clicks/dialogs hit a
different or dead client). The fix and the pervasive per-tool boilerplate have
the same solution: a single `@testclient_tool` decorator that resolves the
endpoint, shapes errors, resolves the capture dir, annotates `attached_endpoint`,
and applies the local-boot guard. This card is **behavioral** (fixes a real bug)
and **offline-testable** via the tool registry.

## Problems (verified against code)

### A4 / finding-5 — ~25 tools never resolve the attached endpoint
`_resolve_testclient_endpoint` (`mcp_server.py:170`) is applied to
`run_scenario` / `run_step` / `write_form_value(s)` / `assert_form_value` /
`wait_for_form_value` / `read_form_descriptor` / `read_record` / `read_table_cell`
/ `read_list_*` / `get_window_list_testclient`, but **not** to `switch_page`
(`:1955`), `toggle_checkbox` (`:1971`), `set_choice` (`:1989`), `set_table_cell`
(`:2009`), `set_table_date_cell` (`:2389`), `select_table_row` (`:2474`),
`open_list` (`:2499`), `search_list` (`:2516`), `set_list_view` (`:2550`),
`advanced_search` (`:2570`), `run_report` (`:2590`), `read_spreadsheet_cell`
(`:2609`), `choose_from_list` (`:2630`), `answer_dialog` (`:2652`),
`set_reference_field` (`:2674`), `open_card` (`:2696`), `close_window` (`:2715`),
`activate_window` (`:2737`), `read_user_messages` (`:2758`), `choose_from_menu`
(`:2776`), `click_command` (`:2797`), the table-row ops (`:2814-2918`), and
`measure_scenario` (`:4344`). After `attach_test_client(host=X, port=Y)` the agent
omits host/port (as the attach contract advertises) → these tools hit the wrong
client.

### S3 — `measure_scenario` lacks the local-boot guard
`mcp_server.py:4343-4364`: `measure_scenario` boots a local `dbgs` +
`1cv8 /TESTCLIENT /DEBUG` and (in `measure.py:327`) runs
`sudo systemctl start apache2`, but is **not** wrapped with
`@_local_only_tool(local_boot=True)`. In model-B (`QA_MCP_REMOTE_CLIENT=1` thin
container) it raises an opaque `FileNotFoundError: .../dbgs` instead of the
structured "not served here" guidance every other boot tool returns.

### Duplication that the decorator removes (server report items 1/4/5)
The `try: host, port, attachment = _resolve_testclient_endpoint(...) / except
ConnectionError: return _attach_tool_error(...)` + trailing
`result["attached_endpoint"] = attachment` triple appears ~12×; ~20 tools are
exactly `template = derive_X(resolve_capture_dir(capture, _repo_root()), …);
return native_Y(template, …, host=host, port=port)`; the dynlist result-assembly
block is duplicated 4×.

## Recommended remediation
- Introduce `@testclient_tool(...)` (extending the existing `_local_only_tool`
  pattern at `mcp_server.py:212-237`, using `functools.wraps` so the FastMCP
  schema survives) that, for every wrapped tool:
  1. resolves the endpoint via `_resolve_testclient_endpoint` (attach-aware) —
     making it **impossible to forget**;
  2. resolves the capture dir (`resolve_capture_dir(capture, _repo_root())`);
  3. wraps the body in the standard error envelope (catch `ConnectionError`,
     `FileNotFoundError` from a bad capture, `ValueError`) → structured result.
     NOTE (post cr-03/cr-04): the write path now raises `WriteRetargetError` and
     `ProtocolSendTimeout` and returns structured `retarget_failed` / `send_timeout`
     results; the envelope must **pass these through unchanged**, not flatten them
     into a generic error;
  4. annotates `attached_endpoint` on the result;
  5. optionally applies `local_only` / `local_boot` guards (covers S3).
- Apply it to **all** endpoint-touching tools, including the ~25 that currently
  bypass resolution and `measure_scenario`.
- **Do not change** internal call flow that currently routes through the
  registered tool (`_write_open_link_fields_by_label` → `write_form_fields_by_label`)
  without also moving the shared body into a plain function both call — otherwise
  internal calls flow through the remote-mode guard. Prefer extracting the body.

## Acceptance
- A **parametrized contract test** iterates the tool registry
  (`mcp._tool_manager.list_tools()`, as `test_clean_tool_surface` already does)
  and asserts, for every endpoint-touching tool, that after
  `attach_test_client(host=X, port=Y)` with omitted host/port the tool connects to
  `X:Y` (assert via a monkeypatched connector capturing host/port) — **no** tool
  falls back to `127.0.0.1`.
- `measure_scenario` under `QA_MCP_REMOTE_CLIENT=1` returns the structured
  "not served here" result, not `FileNotFoundError` — new test.
- Invalid args / bad `capture` name produce a structured error result (not a raw
  traceback) for every wrapped tool — covered by the contract test.
- The `_resolve_testclient_endpoint` / `_attach_tool_error` / `attached_endpoint`
  triple and the `derive_X → native_Y` one-liners are expressed once via the
  decorator (net line reduction in `mcp_server.py`); existing tests still pass.
- `uv run pytest -q` green.

## Suggested change decomposition (for `$opsx-ff`)
- **Change 1 — `testclient-tool-decorator`** (capability: MCP tool surface): the
  decorator + apply to all endpoint tools + local-boot guard for `measure_scenario`.
- **Change 2 — `attach-contract-test`** (capability: MCP tool surface): the
  registry-driven contract test asserting universal attach-awareness and structured
  errors.

## Change Set
- `testclient-tool-decorator`
- `attach-contract-test`

## Change 1: `testclient-tool-decorator`

### Why
Endpoint-aware behavior and error shaping are scattered across many MCP tools, making split-brain attached sessions easy to create and hard to audit.

### Goal
Introduce the shared endpoint-aware tool decorator and apply it to endpoint-touching tools, including the local-boot guard for `measure_scenario`.

### Scope
- Add the decorator in `src/qa_mcp/mcp_server.py`.
- Resolve active attached endpoints, capture directories and structured wrapper errors centrally.
- Preserve structured `retarget_failed` and `send_timeout` results.
- Refactor internal shared bodies only where needed to avoid decorated tool calls from internal helpers.

### Acceptance
- Omitted `host`/`port` on endpoint-touching decorated tools uses the active attached endpoint.
- Bad capture or invalid arguments return structured results.
- `measure_scenario` is blocked by the standard local-only result in remote-client mode.

### Depends On
- none

### Related
- `openspec/changes/testclient-tool-decorator/`

### Notes For `$openspec-ff-change`
- Use capability `qa-mcp-tool-endpoint-contract`.
- Runtime 1C evidence is not required; use offline pytest with monkeypatched connectors.

## Change 2: `attach-contract-test`

### Why
A registry-level contract test is needed so future MCP tools cannot silently bypass the attach endpoint contract.

### Goal
Add a parametrized offline test that inspects registered endpoint-touching tools and proves attach-aware endpoint selection plus structured wrapper errors.

### Scope
- Add explicit endpoint-touching tool classification in tests.
- Monkeypatch connector/native helper seams to capture host/port without live 1C runtime.
- Cover invalid wrapper inputs and `measure_scenario` remote-client behavior.

### Acceptance
- Every endpoint-touching registered tool is covered or explicitly classified as not opening a TestClient connection.
- After `attach_test_client(host=X, port=Y)`, covered tools called with omitted `host`/`port` connect to `X:Y`.
- New endpoint tools without classification fail the contract test.

### Depends On
- `testclient-tool-decorator`

### Related
- `openspec/changes/attach-contract-test/`

### Notes For `$openspec-ff-change`
- Use capability `qa-mcp-tool-endpoint-contract`.
- Keep tests offline and deterministic; do not require Linux TestClient runtime.

## Verify
- OpenSpec artifacts validated by `$opsx-ff`.
- `uv run pytest tests/test_mcp_server.py -q` → 84 passed.
- `uv run pytest tests/test_clean_tool_surface.py tests/test_measure.py -q` → 11 passed.
- `uv run pytest -q` → 658 passed.
- `openspec validate testclient-tool-decorator --strict` → valid.
- `openspec validate attach-contract-test --strict` → valid.
- `openspec validate qa-mcp-tool-endpoint-contract --strict` → valid.
- `openspec validate --all` → 13 passed, 0 failed before archive.
- Matrix preflight/archive gates passed for both changes.

## Related
- `docs/code-review-2026-07-02.md` (A4, server findings 5/6/7, S3)
- Enables/precedes **CR-08** (the decorator is reused by the mcp_server split).
- `openspec/changes/testclient-tool-decorator/`
- `openspec/changes/attach-contract-test/`
- `openspec/changes/archive/2026-07-02-testclient-tool-decorator/`
- `openspec/changes/archive/2026-07-02-attach-contract-test/`
- `openspec/specs/qa-mcp-tool-endpoint-contract/spec.md`

## Result
Implemented, verified, synced into `openspec/specs/qa-mcp-tool-endpoint-contract/spec.md`, and archived:
- `openspec/changes/archive/2026-07-02-testclient-tool-decorator/`
- `openspec/changes/archive/2026-07-02-attach-contract-test/`

Publish commit: `76dda4e` (`Fix attach endpoint routing for MCP tools`).

## Next
- none

## Log
- 2026-07-02 card created from the code-review report (A4, S3, tool-boilerplate dedup).
- 2026-07-02 `$opsx-ff`: decomposed into `testclient-tool-decorator` and
  `attach-contract-test`; created apply-ready OpenSpec artifacts.
- 2026-07-02 `$opsx-do`: implemented the shared endpoint-aware decorator,
  applied it to endpoint-touching tools, added registry attach-contract tests,
  passed full pytest/OpenSpec/matrix verification, synced specs, and archived
  both changes.
- 2026-07-02 `$opsx-pub`: committed and prepared the scoped CR-05 delivery for
  push; final commit hash is reported in the publish summary.
- 2026-07-02 tail cleanup: added decorator-level regression coverage that
  preserves structured `retarget_failed` and `send_timeout` native results
  while annotating the active attached endpoint.
