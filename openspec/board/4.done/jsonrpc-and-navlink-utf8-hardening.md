# JSON-RPC / navigation-link UTF-8 hardening (echo received values, reject/flag mojibake)

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived. **P1**. Same encoding family as the shipped BOM fix. Under epic 111.

## Source
- `docs/qa-mcp-connection-issues-2.md` finding **#9** (+ related #2 error clarity).
- Sibling (delivered): `4.done`/`bootstrap-testclient-launch-script-bom-cyrillic`
  (Cyrillic `/N` corrupted by a BOM-less launch script under PowerShell 5.1).

## Problem
Cyrillic content is repeatedly corrupted on the Windows/PowerShell path. In #9 a
`read_list_grid` call whose navigation link was
```
e1cib/list/Справочник.Валюты
```
arrived at qa-mcp/1C as `e1cib/list/??????????.??????` when the PowerShell
client used default encoding → 1C: «Не удалось перейти по навигационной ссылке».
Sending the body as UTF-8 bytes with `Content-Type: application/json; charset=utf-8`
fixed it (`opened: "Валюты"`). This produces a false impression that the link is
invalid, and is very easy to hit from PowerShell diagnostics on Windows.

## Scope
1. **Force UTF-8 for JSON-RPC bodies** in qa-mcp's own diagnostics/examples/tools
   and document `Content-Type: application/json; charset=utf-8` for Windows.
2. **Echo the received value** — a link/echo diagnostic that returns the exact
   received `open_link` (and other Cyrillic args) so a caller can immediately see
   mojibake instead of a misleading "invalid link".
3. **Reject/flag non-UTF-8** request bodies with a clear error rather than
   forwarding corrupted text downstream to 1C.
4. **Runbook/examples sweep** — every Windows/PowerShell JSON-RPC example in the
   agent-install runbook + docs forces UTF-8 (Invoke-WebRequest defaults corrupt).

## Acceptance
- A `read_list_grid` (or echo diagnostic) with a Cyrillic `open_link` sent via a
  documented UTF-8 example resolves the form; the echo shows the exact link.
- A deliberately non-UTF-8 body is rejected with a clear, non-corrupting error.
- All shipped Windows JSON-RPC examples specify UTF-8.

## Related
- `docs/qa-mcp-connection-issues-2.md` (#9, #2), epic 111.
- `4.done`/`bootstrap-testclient-launch-script-bom-cyrillic` (BOM fix — same class).
- `openspec/changes/archive/2026-07-07-jsonrpc-navlink-utf8-hardening/`

## Change Set
- `openspec/changes/archive/2026-07-07-jsonrpc-navlink-utf8-hardening/`

## Verify
- `openspec validate jsonrpc-navlink-utf8-hardening --strict` passed.
- `uv run pytest -q tests/test_mcp_server.py -k 'utf8_gate or echo_jsonrpc_arguments or http_bind'` passed: 9 passed, 93 deselected.
- `uv run --with pytest --with pyyaml pytest` passed: 769 passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` passed: 0 findings.
- `uv run --with pytest --with pyyaml pytest -m smoke` passed: 3 passed, 766 deselected.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py openspec/changes/jsonrpc-navlink-utf8-hardening/design.md --mode archive --output .artifacts/openspec/jsonrpc-navlink-utf8-hardening/20260707T200219Z/matrix-archive-gate.json --json` passed.
- `openspec validate qa-mcp-tool-endpoint-contract --strict` passed.
- `openspec validate qa-mcp-self-hosted-release --strict` passed.
- `openspec validate --all` passed.
- `git diff --check` passed.

## Result
Delivered `jsonrpc-navlink-utf8-hardening`: qa-mcp now exposes `echo_jsonrpc_arguments`, flags likely mojibake in received parsed values, rejects non-UTF-8 direct HTTP JSON-RPC bodies before tool dispatch, and documents UTF-8-safe Windows PowerShell JSON-RPC examples.

## Next
- Run the optional Windows model-B live smoke on the incident contour when a Windows host/TestClient is attached.

## Change 1: `jsonrpc-navlink-utf8-hardening`

### Why
Cyrillic JSON-RPC arguments can be corrupted by Windows/PowerShell defaults
before qa-mcp receives them, making a transport encoding problem look like an
invalid 1C navigation link.

### Goal
Add qa-mcp-owned diagnostics and direct HTTP guards so callers can see the exact
received value, non-UTF-8 direct HTTP bodies fail closed, and active runbooks
show UTF-8-safe PowerShell JSON-RPC examples.

### Scope
- Add an echo diagnostic for received `open_link` and other Cyrillic arguments.
- Flag replacement-character/question-mark mojibake in echoed values.
- Reject non-UTF-8 direct HTTP JSON bodies before tool dispatch.
- Update active Windows/PowerShell JSON-RPC examples.

### Acceptance
- Echoing `e1cib/list/Справочник.Валюты` returns the same received value.
- Echoing `e1cib/list/??????????.??????` returns the value with a mojibake warning.
- Direct HTTP requests with a non-UTF-8 charset or invalid UTF-8 bytes receive a clear JSON error before tool dispatch.
- Active Windows JSON-RPC examples use UTF-8 bytes and `application/json; charset=utf-8`.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-07-jsonrpc-navlink-utf8-hardening/`

### Notes For `$openspec-ff-change`
- The Docker model-B external HTTP path is owned by `ai-mcp-proxy`; this change hardens qa-mcp's direct HTTP path and adds a tool-level echo diagnostic that remains useful behind the proxy.

## Log
- 2026-07-07 filed from #9; part of a recurring Windows/Cyrillic/UTF-8 theme.
- 2026-07-07T19:59:29Z artifacts prepared for `jsonrpc-navlink-utf8-hardening`; moved to `2.todo`.
- 2026-07-07T20:02:19Z retained evidence under `.artifacts/openspec/jsonrpc-navlink-utf8-hardening/20260707T200219Z/`; Windows model-B smoke recorded as N/A for this Linux workspace.
- 2026-07-07 delivered, synced specs, and archived as `openspec/changes/archive/2026-07-07-jsonrpc-navlink-utf8-hardening/`.
- 2026-07-07 published with commit subject `feat(mcp): harden json-rpc utf8 diagnostics`.
