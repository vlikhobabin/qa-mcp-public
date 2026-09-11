# 76. Raw-API session-ID synthesis for zero-divergence safe_ui replay

## Status
5.canceled

## Cancellation
- 2026-06-17 (board triage): **superseded.** Zero-divergence raw-API *replay* was the goal of the old
  capture-and-replay path; **card 80 Fork-2** (capture-free value-write+commit, productized as
  `qa_mcp.protocol.native_write`) replaced replay with synthesis, and the 6 safe_ui members are accepted
  via the result-contract class meanwhile. There is no remaining product need to raise captured safe_ui
  flows to zero-divergence replay. Diagnosis preserved below as an audit trail.

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-14: spun off from card 75. The direct test-API `command_kind` path (manager-fixture-v1)
  captures safe_ui commands fine, but those captures cannot be replayed at zero-divergence because
  the raw `ТестируемоеПриложение` manager assigns session GUIDs that never appear in client responses,
  so `GuidRebinder` (learns captured→live only from client responses) cannot map them. Card 75 accepts
  the 6 safe_ui members via the result-contract class meanwhile; this card raises them to
  zero-divergence and would also complete the stalled V2 safe-action subsystem.

## Problem (diagnosed on card 75, 2026-06-14)
Probe-replay of `fixture-active-form-activate-cap` diverges at send_index 16: frames mgr[14/15] are
sent `adapted=false` and carry session GUIDs `ae135932-4f94-44df-92c1-c91f15a92848` and
`d450256e-76cf-4404-b8ae-056edd642053` whose **first appearance is in manager→client frames (idx 0)
and which never appear in any client→manager response**. `GuidRebinder.from_client_chunks` /
`observe_response` only learn captured→live pairs from client responses by first-appearance order, so
these manager-originated identifiers are structurally unlearnable; the stale captured values are sent
and the live client rejects the frame (recv 4→0 bytes). Vanessa (action-manifest) captures replay
clean because their session IDs are echoed in client responses. The sequence counter @offset 43
(len 5, see [[session-bootstrap-synthesis]]) is also not normalized by `_normalize_for_form` (offsets
(2,16),(19,2),(68,16)) and may matter.

## Approach (sketch — to be validated)
- Pair captured manager-session GUIDs with the live session's equivalents derived from the live
  handshake, the way `session.py open_and_bootstrap` synthesizes bootstrap frames (counter @43, ticket
  GUID, config constants e23134a2/7f58f27d/102301e1). Either (a) drive these captures through the
  native bootstrap synthesizer + replay only the semantic command frames, or (b) extend the rebinder /
  replay to substitute manager-originated session GUIDs by position against the live handshake.
- Validate on `fixture-form-activate-cap` / `fixture-active-form-activate-cap` (Form.Activate) → expect
  diverged_at=null → then the other safe_ui members + re-confirm V2.

## Acceptance
- A raw-API (manager-fixture-v1) safe_ui capture replays with `diverged_at_send_index=null`.
- The 6 card-75 safe_ui members (Form/Button.Activate, GotoNext/Prev/StartPage, ChooseUserMessage)
  re-accepted at zero-divergence (upgrading their result-contract acceptance).

## Log
- 2026-06-14: card created (spin-off from card 75 diagnosis).
