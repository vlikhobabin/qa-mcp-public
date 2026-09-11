# 62. Synthesize Session Bootstrap Frames 1..3

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-10 project status review and lab-hardening pass
- `docs/protocol-research/status-report-2026-06-03.md` (transport/session
  bootstrap layer: frames `1..3` remain captured-derived)

## Summary
Session bootstrap currently depends on captured bytes for the early handshake
frames `1..3`; only later frames are template-rendered with dynamic fields.
This pins every replay and Python-manager session to the baseline capture and
to the current lab platform build, and it is the main hidden debt under
version/client-mode portability.

Synthesize the bootstrap frames from protocol knowledge: describe their
structure, dynamic fields and invariants, render them without captured bytes,
and prove the synthesized bootstrap by a fresh-session replay or direct
Python-manager session that performs an already-accepted read-only operation.

## Acceptance
- Frames `1..3` have documented structure and dynamic-field evidence, or a
  precise unresolved reason per byte range.
- `qa_mcp.protocol` can bootstrap a session without reading baseline capture
  bytes for frames `1..3`, or the blocker is recorded with evidence.
- A fresh TestClient session bootstrapped from synthesized frames passes an
  already-accepted read-only operation (for example active-window context).
- Compact evidence is published under `docs/protocol-research/evidence/` with
  capture id, frame ranges, dynamic fields and replay/probe status.
- The portability impact (platform build dependence) is restated in the next
  status report.

## Change Set
- `src/qa_mcp/protocol/bootstrap_synth.py` + `bootstrap_frames_1to3.json` — synthesizer
- `src/qa_mcp/protocol/session.py` — optional `synthesized` path for frames 1..3
- `tools/protocol-research/python_manager_probe.py` — `--synthesize-bootstrap`
- `tools/protocol-research/bootstrap_synth_proof.ps1` — live proof runner
- `tests/test_bootstrap_synth.py` (+ fixture) — offline round-trip vs independent session
- `docs/protocol-research/evidence/session-bootstrap-frames-1-3/` — analysis + proof evidence

## Verify
- Offline: `synthesize_bootstrap(base, guid)` reproduces an INDEPENDENT session's frames 1..3
  byte-for-byte (4 tests, all green; 112 total).
- Live: fresh TestClient session with synthesized frames 1..3 (fresh counter base 35320 +
  fresh ticket GUID, no captured 1..3 bytes) → `active-window-context` `status=ok`,
  `active_window_ref=.HomePage[…]`. The client accepted the synthesized frame-3 GUID and
  returned a valid ACK → frame-3 GUID is manager-chosen independent random.

## Archive
- Done. Acceptance met (frames 1..3 documented + synthesized + live read-only proof + portability
  caveat recorded). Residual: session/manager GUID `e23134a2-…` and `7f58f27d-…` token are lab/
  config constants; frames 4+ remain captured-derived (separate future scope).

## Related
- `docs/protocol-research/evidence/session-bootstrap-frames-1-3/analysis.md` (+ proof_*.json)
- `src/qa_mcp/protocol/bootstrap_synth.py`, `bootstrap_frames_1to3.json`
- `src/qa_mcp/protocol/bootstrap.py`, `session.py`

## Result
DONE 2026-06-13 — frames 1..3 synthesized without captured bytes; offline + live proof.

## Next
- (optional, future card) synthesize frames 4..7 + manager templates; resolve the
  `e23134a2`/`7f58f27d` constants to manager-free-choice or config-derived for full portability.

## Change Plan Notes
When the card moves to `2.todo/`, replace this section with ordered changes.

## Log
- 2026-06-10T11:30:00Z card created from the lab-hardening review: bootstrap
  frames `1..3` are captured-derived and block portability

- 2026-06-13: frames 1..3 structure analyzed (99% static; dynamic = counter + frame-3 ticket GUID); synthesizer + tests added; live fresh-session proof passed active-window with synthesized 1..3. DONE.
