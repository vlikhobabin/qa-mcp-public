# Card 78 Phase A — live spike PASSED (2026-06-14)

An ACTION executed in a synthesized (capture-free, no Vanessa) session:
- open_and_bootstrap (synthesized) + run_segment nav to the fixture form (active-window ok, form-summary 6 frames ok).
- live managed_form_guid 5ffee762-... (vs captured 4451d8b2-...) -> rebind required + applied.
- handle.run_action(input command, rebinder): sent 287B, recv 665B, accepted=true (no reset).

Proves actions integrate into the synthesized SessionHandle. Also fixed a real bug: the uint16 sequence
fields (templates.py render_frame5/render_single_block_frame/uint16_le) overflowed for large message
counters (frame4_sequence=80300 > 65535) -> now wrapped mod field width. This affected single_session_proof too.
