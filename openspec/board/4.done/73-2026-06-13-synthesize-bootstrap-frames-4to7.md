# 73. Synthesize Session Bootstrap Frames 4..7 + resolve config constants

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-13 follow-on to card 62 (frames 1..3 synthesized); extend to 4..7 and resolve
  whether the residual config-constant GUIDs are manager-free-choice or client-validated.

## Summary
Card 62 synthesized bootstrap frames 1..3 without captured bytes. This card extends the same
in-repo-template approach to frames 4..7 (the rest of the captured-derived bootstrap; frames 8+
were already JSON-template-rendered) and resolves the portability constants left open by card 62.

## Acceptance
- Frames 4..7 render from the in-repo template (no captured bytes); a single message-counter
  base threads through frames 1..7. DONE.
- A fresh TestClient session with frames 1..7 fully synthesized passes active-window-context.
  DONE (run 20260613-200118: base 58102, frame4_sequence 58105, status=ok, .HomePage).
- The residual config constants are resolved: which are manager-free-choice vs client-validated.
  DONE — per-constant matrix (fresh client boot each): `none`=ACCEPTED; `session_guid`,
  `token_7f`, `guid2` each = REJECTED. So all three identity GUIDs are **client-validated /
  config-required**; only the counter base + frame-3 ticket GUID are free.

## Change Set
- `src/qa_mcp/protocol/bootstrap_frames_1to3.json` — frames 4..7 + frame4/constants specs
- `src/qa_mcp/protocol/bootstrap_synth.py` — frame4 renderer, templates_4to7, randomize_constants
- `src/qa_mcp/protocol/session.py` — synthesized path for frames 4..7
- `tools/protocol-research/python_manager_probe.py` — `--randomize-constant[-names]`
- `tools/protocol-research/bootstrap_synth_proof.ps1`, `bootstrap_const_resolve.ps1`
- `tests/test_bootstrap_synth.py` — frame-4 round-trip
- `docs/protocol-research/evidence/session-bootstrap-frames-1-3/` — analysis + proof_1to7_* +
  constant_resolution_matrix.json

## Result
DONE 2026-06-13 — frames 1..7 synthesized without captured bytes (offline + live proof); the
3 identity GUIDs (session_guid/token_7f/guid2) proven client-validated config constants (kept in
the template for this lab). Residual for full cross-config portability: source those 3 GUIDs from
the target config rather than randomizing them.

## Next
- (optional, future) source session_guid/token_7f/guid2 from the target infobase/config for
  cross-build portability; everything else in the bootstrap is now synthesized.

## Log
- 2026-06-13: frames 4..7 synthesized; full 1..7 live proof passed; per-constant matrix resolved
  (all 3 identity GUIDs client-validated). DONE.
