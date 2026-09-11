# 116. P3 — version-conditional protocol code (CONDITIONAL on P2's diff)

## Status
4.done

## Order Index
116

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Parent epic 112. **Conditional** phase — its size is determined by P2's (115) 8.5-vs-8.3 decode/diff report.
  Expected to be small or empty: the protocol code is data-driven and the wire markers are believed structural
  (version-invariant), so a major-version bump that moves handshake/template CONTENT is handled by data alone.

## Summary
If — and only if — P2 shows that 8.5 changed the wire **structure** (not just captured content), add the
minimal version-conditional logic to the decode/render path; then wire the P0 resolvers to actually select and
drive the 8.5 set.

## Scope
- **If data-only (expected):** no protocol-code change. Confirm the P0 version-aware resolvers select the 8.5
  set and the engine drives 8.5 open/read/write with the 8.5 captures unchanged.
- **If structure moved:** add a version-keyed wire-constant layer for the moved markers/offsets/codecs (a
  natural pairing with card 111 item 5's `wire_constants.py` registry — do the registry here if it lands). Keep
  the change surgical and table-driven (version → constants), not branching scattered through the code.
- Either way: a single switch (the active version) drives both data selection and any conditional codec.

## Acceptance
- With the 8.5 asset set selected, the engine drives a full open → read → write → assert cycle on a live 8.5
  TestClient end-to-end.
- No 8.3 regression: the 8.3 path drives the same cycle unchanged; offline suite green.

## Dependencies
- P2 (115) — the diff report sizes this phase. P0 (113) — the resolver hooks.

## Verify
- A live 8.5 write+read roundtrip via the product (the card-105-style UI→DB proof, on 8.5); 8.3 roundtrip
  unregressed.

## Archive
- not started

## Result
- **✅ DELIVERED — minimal version fixes (epic 112).** P2's full re-capture proved unnecessary (the 8.5 wire is
  byte-structurally identical to 8.3); the only code needed was version-awareness: TWO one-field LIVE-version
  injections (synthesized bootstrap + card-101 foreground replay) + a clean-state Escape sweep before XTEST
  writes. Commits `cead89c` (version-aware synth bootstrap) + `897806d` (version-aware foreground replay) +
  `2c0fab7` (e2e write green on 8.5). In `main`.

## Log
- 2026-06-25 created under epic 112. Thin/conditional; size finalized after P2.
- 2026-06-29 board hygiene: moved 1.backlog → 4.done (the minimal version-conditional code shipped).
