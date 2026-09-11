# 115. P2 — re-capture the genuine protocol corpus on 8.5 (the long pole)

## Status
5.canceled

## Order Index
115

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Parent epic 112. The empirical probe (2026-06-25) proved the 8.3 captures fail on 8.5 at the handshake
  (`client ACK GUID not found after manager frame 3`) → the genuine corpus must be re-recorded on 8.5. This is
  the critical-path phase and the one that ANSWERS the data-only-vs-code question (P3).

## Summary
Re-run the documented capture-refresh pipeline (`docs/capture-refresh-runbook.md`) end-to-end on the 8.5 lab
(P1) to produce the full 8.5 protocol asset set, and decode/diff it against the known 8.3 shapes to size P3.

## Scope
1. **Irreducible handshake** — capture the genuine connect/bootstrap on 8.5 (the `genuine-commit-conn`
   equivalent) → `traffic.jsonl`; verify the engine connects to a live 8.5 client with it.
2. **Frame templates** — capture + rebuild the manager-frame templates (open frames 8-106 + value-read
   218-221) via `build_tm_v1_open_template.py` on 8.5 traffic → `manager_frame_templates.json` +
   `value_read_templates.json` for 8.5.
3. **Action/foreground captures** — re-record the bundled set on 8.5 (the 13 `genuine-card9x` captures: demo
   write, list-read, nextrow/-flat/rowbyvalue, the card97 dynlist set, multiaction, foreground/date-cell).
4. **accepted_mappings** — re-derive the read-only operation evidence on 8.5.
5. **Decode + diff 8.5 ↔ 8.3** — use the compare tooling to classify what moved: is it ONLY handshake/template
   CONTENT (GUIDs/sequence/offsets within the same structure → data-only), or did the wire STRUCTURE change
   (markers `TAIL_MARKER`/`0xE0`/`0xFA`/`0x81`, GUID patterns, value envelopes, codecs → needs P3 code)? Emit a
   written 8.5-vs-8.3 drift report — this is the gate for P3's size.
6. **Drop into the P0 layout** — populate `src/qa_mcp/_bundled/8.5/…` via the parametrized
   `bundle_runtime_assets.py`.

## Acceptance
- A complete 8.5 asset set exists and is bundled under `_bundled/8.5/`; the 8.5 handshake replays (the engine
  connects + bootstraps a live 8.5 TestClient) and a value-read decodes correctly on 8.5.
- A 8.5-vs-8.3 diff report classifies the change as data-only or structure-moved, scoping P3.

## Dependencies
- P1 (114) — the 8.5 lab + capture infra. P0 (113) — the `_bundled/<version>/` layout to populate.

## Verify
- The engine drives an open-form + value-read on a live 8.5 client using the 8.5 set (evidence run); the diff
  report is committed under `docs/protocol-research/` (research, kept in repo per dev-harness policy).

## Archive
- not started

## Result
- **❌ CANCELED — superseded by validate-first (epic 112).** The premise that 8.5 needs a full corpus re-capture
  was a RED HERRING: the original frame-3 break was qa-mcp sending a stale 8.3 version string the 8.5 client
  rejected, NOT a wire change — the genuine 8.5 wire is byte-structurally identical to 8.3. The
  data-only-vs-code question this card was meant to answer was instead answered by the live e2e (7/7 GREEN on
  8.5 with the 8.3 data). A full re-capture is now the LAST resort (re-capture only what goes RED on a future
  platform), so this phase is unnecessary for 8.5. `_bundled/8.5/` remains the fallback slot for a version that
  genuinely moves the wire.

## Log
- 2026-06-25 created under epic 112. Long pole; gates P3/P4/P5. Methodology + 189-script harness already exist.
- 2026-06-29 board hygiene: moved 1.backlog → 5.canceled (superseded by the validate-first outcome; see epic 112).
