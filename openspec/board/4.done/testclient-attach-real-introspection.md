# Make TestClient attach real: drive introspect/write tools against an out-of-band client

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- Follow-up from the delivery review 2026-06-26 of `testclient-launcher-libgcc-and-attach` (verdict: PARTIALLY SOLVES — 🔴).
- Review: `/opt/ai-dev-suite-for-1c/docs/retro/2026-06-26-delivery-review.md` (§"testclient-launcher… attach is a shim").
- Original card: `openspec/board/4.done/testclient-launcher-libgcc-and-attach.md`.

## Problem
The libgcc preload (item 1, live-proven) and timeout diagnostics (item 3) landed, but the
**attach mode (item 2) is only a status/ownership shim** — no introspect/write/replay tool
consumes the attach handle, so the original B7 blocker (empty introspection against a
client launched out-of-band by TPort: `read_form_descriptor → {opened:null, fields:{}}`)
is unsolved. Attach changes nothing about whether the replay engine can drive a foreign
client.

## Evidence (file:line, from review)
- `src/qa_mcp/protocol/lifecycle.py:500-525` — `attach_test_client()` validates the port, returns `pid=None, owns_process=False, attached=True`; no handshake/bootstrap.
- `src/qa_mcp/.../mcp_server.py:1388,2112-2114,2436-2438,2615-2617` — introspect/write tools each create a fresh `TestClientSession(host,port)` + `open_and_bootstrap()` by host:port, never using the attach handle; `mcp_server.py:504` docstring concedes "protocol tools still connect by host:port".
- design.md: "attach-to-endpoint contract, not a new low-level wire handshake" (de-scoped).

## Proposed direction
- Route the introspect/write/replay tools through the attached session/handle so an
  externally-booted client can be driven; OR
- Diagnose the root cause of empty introspection against a foreign-launched client
  (suspected `open_and_bootstrap` version drift — the proof bundle is 8.3-only) and fix
  the bootstrap so host:port attach actually yields a usable session.
- Add a test that boots a client OUT-OF-BAND (separate process) and then drives
  `read_form_descriptor`/`write_form_value` against it with non-empty results.

## Rough acceptance
- `read_form_descriptor` (enumerate_live) against an out-of-band client returns non-empty
  fields for an existing form.
- A create→fill→save flow can be driven against an attached (not qa-mcp-launched) client.
- Test exercises the out-of-band path (not just qa-mcp's own launch).

## Related
- Original retro `docs/retro/2026-06-26-session-retro.md` (B7); memory `qa-mcp-testclient-launcher-libgcc`.
- Unblocks the headline e2e UI verification (`e2e-real-dev-contracts-catalog-on-demo10413`).
- `openspec/changes/testclient-attach-real-introspection/`

## Change Set
- `testclient-attach-real-introspection` - route real replay-backed tool sessions through the attached out-of-band TestClient endpoint.

## Change 1: `testclient-attach-real-introspection`

### Why
The prior attach endpoint records status and ownership but does not give descriptor/write tools a real attached
session route, so an out-of-band TestClient can still produce empty introspection for existing forms.

### Goal
Make `attach_test_client` establish a reusable MCP-server endpoint context that `read_form_descriptor`, value-read,
scenario and write session factories can use, with explicit attach/bootstrap diagnostics and retained out-of-band
descriptor evidence.

### Scope
- Modify qa-mcp lifecycle/MCP session routing in `src/qa_mcp/protocol/lifecycle.py` and `src/qa_mcp/mcp_server.py`.
- Add focused offline tests in `tests/test_lifecycle.py`, `tests/test_mcp_server.py` and descriptor/write routing tests.
- Retain read-only Linux runtime evidence when preflight passes.
- Keep live mutation proof behind existing write-safety and recovery policy.

### Acceptance
- `attach_test_client` records an active non-owned endpoint that replay-backed MCP tools can resolve by default.
- `read_form_descriptor` against an attached out-of-band client returns non-empty descriptor evidence for an existing form, or a bounded diagnostic naming the failed attach/bootstrap/open/descriptor phase.
- Write/scenario factories can resolve the attached endpoint route while preserving existing write/action safety results.
- External TestClient cleanup remains non-owned: qa-mcp does not kill a process it attached to but did not launch.

### Depends On
- `openspec/changes/archive/2026-06-26-testclient-launcher-libgcc-and-attach/`

### Related
- `openspec/changes/testclient-attach-real-introspection/`

### Notes For `$openspec-ff-change`
- Capability: `qa-mcp-protocol-lab`.
- Include the 1C verification matrix from `design.md` / `tasks.md`.
- Live runtime proof must run the Linux preflight before starting or attaching a 1C process.

## Verify
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode preflight` - passed; retained at `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/matrix-preflight.json`.
- `uv run pytest tests/test_lifecycle.py tests/test_mcp_server.py tests/test_form_descriptor.py` - 75 passed.
- Linux runtime preflight passed; retained at `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/runtime-preflight.json`.
- Out-of-band attach descriptor proof passed; retained at `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/out-of-band-descriptor.json` (`Контрагенты`, 79 elements, active attached endpoint `127.0.0.1:15381`).
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode archive` - passed; retained at `.artifacts/openspec/testclient-attach-real-introspection/20260627-deliver/matrix-archive-gate.json`.
- `openspec validate qa-mcp-protocol-lab --strict` - passed.
- `openspec validate testclient-attach-real-introspection --strict` - passed before archive.
- `openspec validate --all` - passed after archive.
- `git diff --check` - passed.

## Archive
- `openspec/changes/archive/2026-06-27-testclient-attach-real-introspection/`

## Result
Delivered and archived. `attach_test_client` now records an active non-owned endpoint context for the MCP server
process, and replay-backed read/write/session wrappers resolve that attached endpoint by default when callers do
not pass a non-default host/port. Attached descriptor failures now surface as explicit attach/bootstrap/descriptor
diagnostics instead of silently looking like a successful empty form. Live proof launched a TestClient in one
process, attached from a second process, and ran `read_form_descriptor` through the active attached route without
passing host/port. The publish pass updated the consumer tool reference with the attach routing and explicit
host/port override behavior.

## Next
- No follow-up for this card.

## Log
- 2026-06-27 created from delivery review (🔴 — core blocker still open).
- 2026-06-27T05:20:53Z moved to `2.todo` with one apply-ready OpenSpec change.
- 2026-06-27T05:32:04Z implementation verified, spec synced and change archived.
- 2026-06-27T05:37:45Z publish docs updated and final verification passed.
