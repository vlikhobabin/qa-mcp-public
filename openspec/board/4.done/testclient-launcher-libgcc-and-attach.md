# TestClient launcher: libgcc LD_PRELOAD fix + attach-to-running-client mode

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- e2e retro 2026-06-26 (Claude Code session `17257938-…`), finding **B7**.
- Source report: `/opt/ai-dev-suite-for-1c/docs/retro/2026-06-26-session-retro.md` (§B B7).
- Run card (root board): `openspec/board/1.backlog/e2e-real-dev-contracts-catalog-on-demo10413.md`.
- Memory: `qa-mcp-testclient-launcher-libgcc`.

## Problem
`launch_test_client` spawns `1cv8 … /TESTCLIENT` **without** the libgcc `LD_PRELOAD`
that this box needs, so the client crashes on boot and the launch times out. Even after
self-booting the client with the preload, qa-mcp's capture-replay introspect/write tools
returned empty (against the externally-booted client) — they appear to require the
protocol session that qa-mcp's own launch establishes. Net: the headline interactive
UI verification (create a record → fire the form handler → assert UI→DB) was blocked.

## Evidence (observed this run)
- `launch_test_client {env_file: demo10413/.ai/qa-demo10413.env, port:15381}` →
  error "TestClient TPort 15381 did not start listening within 60s".
- qa-mcp's own evidence shows the cause:
  `qa-mcp/runtime/protocol-research/testclient-lifecycle/20260625-072410/client.out`:
  `1cv8: libgcc_s.so.1: version 'GCC_12.0.0' not found (required by .../libhwy.so.1)`
  (and GCC_13). `grep -r LD_PRELOAD qa-mcp/src` → **no preload handling**.
- Workaround that worked: self-boot with
  `LD_PRELOAD=/lib/x86_64-linux-gnu/libgcc_s.so.1 xvfb-run -a 1cv8 ENTERPRISE
  /IBConnectionString 'File="…/1cd";' /N Администратор /TESTCLIENT -TPort 15381 …`
  → listening in 1s. Then qa-mcp `test_client_status`/`infobase_info` connected and
  `open_list` (retargeted to the new catalog) was **accepted**.
- But `read_form_descriptor {open_link:…, enumerate_live:true}` returned
  `{opened:null, fields:{}}` even for an **existing** form (Контрагенты) — so the
  replay engine doesn't drive the self-booted client.

## Context for opsx-ff (what to rely on)
- The libgcc preload is already applied by `admin-mcp/bin` and `tests/e2e/bootstrap.sh`
  ("The 1cv8 thick client needs a system-grade libgcc … LD_PRELOAD a system libgcc");
  mirror that in qa-mcp's launcher.
- qa-mcp lifecycle/launch code: `qa-mcp/src/qa_mcp/protocol/…` (TestClientProcess,
  TestClientSession). The driving tools connect by `host:port`; `launch_test_client`
  is documented as letting the client "outlive" the call, so an **attach** path is a
  natural fit.
- Connection-probe tools (`test_client_status`, `infobase_info`) already work against
  any listening TPort — so the gap is specifically the session/handshake state the
  replay engine needs.

## Change Set
- `testclient-launcher-libgcc-and-attach` - lifecycle preload, launch diagnostics and attach endpoint.

## Change 1: `testclient-launcher-libgcc-and-attach`

### Why
The Linux TestClient launcher must be reliable on the suite lab host, and failed boots must surface the native
client error instead of an opaque TPort timeout.

### Goal
Teach qa-mcp to preload a system libgcc for Linux `1cv8` launches, return bounded launch diagnostics, and expose
an attach-to-running endpoint handle that can create the same `TestClientSession` entry point without claiming
process ownership.

### Scope
- Modify `src/qa_mcp/protocol/lifecycle.py` and the MCP lifecycle surface.
- Add offline lifecycle/MCP tests.
- Retain live launch/read-only probe evidence only after Linux runtime preflight succeeds.

### Acceptance
- `launch_test_client` boots a working `/TESTCLIENT` on this box (no manual preload).
- After launch or attach, read-only protocol tools can create a session against the listening TPort and drive a
  descriptor/window probe; write/action tools stay within their existing safety gates.
- Failed launches report the underlying client error.

### Depends On
- none

### Related
- `openspec/changes/testclient-launcher-libgcc-and-attach/`

## Verify
- `uv run pytest tests/test_lifecycle.py tests/test_mcp_server.py` - 40 passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode preflight` - passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode archive` - passed.
- Linux runtime preflight passed; retained at `.artifacts/openspec/testclient-launcher-libgcc-and-attach/20260626-deliver/preflight_result.json`.
- Live lifecycle proof passed; retained at `.artifacts/openspec/testclient-launcher-libgcc-and-attach/20260626-deliver/live_lifecycle_result.json`.
- `openspec validate testclient-launcher-libgcc-and-attach --strict` - passed before archive.
- `git diff --check` - passed.

## Archive
- `openspec/changes/archive/2026-06-26-testclient-launcher-libgcc-and-attach/`

## Related
- [[../../../../tests/e2e]] env recipe (bootstrap.sh libgcc preload).
- Retro report §B B7; memory `qa-mcp-testclient-launcher-libgcc`.
- `openspec/changes/testclient-launcher-libgcc-and-attach/`
- publish commit recorded in git history

## Result
Delivered and archived. `launch_test_client` now prepares a system libgcc preload for Linux launches, failed
launches include bounded diagnostics, and `attach_test_client` exposes non-owned endpoint attach semantics for
already-listening TestClient ports. Published in the scoped git commit for this card.

## Next
- run `$opsx-pub openspec/board/4.done/testclient-launcher-libgcc-and-attach.md`

## Log
- 2026-06-26 created from e2e retro (interactive UI verification blocked by this).
- 2026-06-26T16:25:28Z moved to `2.todo` with one apply-ready OpenSpec change.
- 2026-06-26T16:36:36Z implementation verified, specs synced and change archived.
- 2026-06-26T16:41:00Z scoped commit prepared for publish.
