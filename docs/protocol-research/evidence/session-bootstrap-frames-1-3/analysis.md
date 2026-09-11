# Session bootstrap frames 1..3 — structure analysis (card 62)

Date: 2026-06-13. Captures diffed: `tm-v1-ro-batchQ3` (A) vs `tm-v1-ro-batchP` (B)
(two independent TestClient sessions, same lab platform 8.3.27.2130 / vanessa_client).

## Current behaviour (the debt)
`TestClientSession.render_initial_ui_frame` (`src/qa_mcp/protocol/session.py:242`)
sends manager frames **1, 2, 3 verbatim** from a baseline capture
(`source="captured"`). Only frame 4+ are template-rendered. So every Python-manager
session is pinned to a baseline capture's bytes and to the exact platform build.

## Frames 1..3 are ~99% static
Byte-diff of manager frames 1..3 between two independent sessions:

| frame | length | differing bytes | differing offsets |
| --- | ---: | ---: | --- |
| 1 | 548 | 4 | 43, 45-47 |
| 2 | 580 | 4 | 43, 45-47 |
| 3 | 612 | 26 | 43, 45-47, **421-442** |

Everything else is byte-identical across sessions → protocol/config invariants.

## The only per-session dynamic fields
### 1. Decimal message counter (all three frames; offsets ~43-47)
Header text: `...{0,e23134a2-14ff-4160-ba5f-ccef04e3786f,<COUNTER>,4,7f58f27d-...`
- A: frame1=26847, frame2=26848, frame3=26849  → **+1 per frame**
- B: frame1=16076, frame2=16077, frame3=16078
- Session base differs (26847 vs 16076); increments by 1 each frame.
- **Manager-chosen** (not echoed from the client). Synthesize: pick a base, increment.

### 2. Frame-3 ticket token (offsets 421-442, inside an 82-byte base64 block)
Frame 3 carries a base64 token `UAAD...==`. Decoded (82 bytes):
`50 00 03 00 | 0000000000005800... (six 0x58 array slots) | <8-byte field> | 00 00 00 0f | <16-byte GUID>`
- The **8-byte field** (`35c288e20a00f465` in A) and the **16-byte GUID**
  (`10d84667c149a3fe183a5bea7b808681` in A) are the per-session tail (offsets 421-442).
- The 16-byte GUID is the **ACK GUID** the client echoes back in its response to frame 3
  (already extracted downstream as `ack_guid`).
- **Manager-generated.** Synthesize: fresh 16-byte GUID (+ the 8-byte field — likely a
  tick/handle; needs confirmation whether random is accepted).

## Invariants that are NOT client-echoed (portability caveat)
- Session/manager GUID `e23134a2-14ff-4160-ba5f-ccef04e3786f` — **identical across both
  sessions** and **absent from the client's initial frames** → a fixed manager/config
  identifier (lab/platform-specific). The client's own GUID is different
  (`671507fd-50a9-4b63-b70e-58b3d364f48f`, sent in client frame[1]).
- Token `7f58f27d-...` — same story (invariant, manager-side).
- These are the **version/config portability dependency** card 62 calls out: they are
  constant for this lab build but may differ on another platform/config. For a first
  synthesized bootstrap they can be treated as constants; full portability needs them
  proven manager-free-choice or config-derived.

## The handshake is ticket-based (V8 intro ticket)
The client's initial frames include a base64 **`V8IntroTicketAck`** ticket that decodes to
`V8IntroTicketAck \x00 HISTORICAL-LAB-HOST\historical-user \x00 Neg...` (workstation\user + negotiation).
Frame 3's 82-byte token is the manager's side of this negotiation.

## OPEN QUESTION — RESOLVED (2026-06-13): frame-3 GUID is independent random
Live proof `bootstrap_synth_proof.ps1` ran a fresh TestClient session with **synthesized**
frames 1..3 using a brand-new counter base `35320` and a brand-new 16-byte ticket GUID
`cde28f640a2752c646f3713f206d9872` (neither from any capture). The client **accepted** the
synthesized frame 3 (responded with a valid ACK `b6d95014-c85a-4928-896f-2d2335cc1ddf`) and the
session completed `active-window-context` → `status=ok`, `active_window_ref=.HomePage[…]`. So the
frame-3 ticket GUID is a **manager-chosen independent random** that the client does not validate
against the intro ticket; the 8-byte field decoded as static and was kept from the template.
Evidence: `proof_manifest.json`, `proof_result.json` (this dir).

## CARD 73 — frames 4..7 synthesized + constants resolved (2026-06-13)
**Frames 4..7** are now synthesized too (no captured bytes for 1..7):
- frame 4 (text): ack_guid@6 + the message counter@43 (= base+3) injected into the static
  template; deterministic round-trip vs an independent session (test).
- frames 5..7 (binary): the proven `BootstrapFrameRenderer` fed the stored template bytes
  (ack_guid uuid_le@2, sequence uint16@19 = base+3+delta, fresh nonces).
- **Live proof**: a fresh session with frames **1..7** synthesized (fresh base 58102 threaded
  through all frames → frame4_sequence 58105 = base+3, fresh ticket GUID) passed
  active-window-context (`status=ok`, `.HomePage[…]`). Evidence `proof_1to7_*.json`.

**Constant-resolution matrix** (`bootstrap_const_resolve.ps1`, a fresh TestClient boot per row,
randomizing one config-constant GUID at a time):

| randomized | result |
| --- | --- |
| none (control, real constants) | ACCEPTED (status=ok) |
| `session_guid` (e23134a2, frames 1-3 @6) | REJECTED (no session) |
| `token_7f` (7f58f27d, frames 1-3 @51) | REJECTED (no session) |
| `guid2` (102301e1, frame 4 @51) | REJECTED (client reset) |

**Resolution:** the counter base and the frame-3 ticket GUID are **manager-free-choice** (fresh
values accepted). The three identity GUIDs are **client-validated / config-required** — the
client rejects any fresh value. So frames 1..7 synthesize without captured bytes, but carry
**three config-constant GUIDs that must match the target build/config** (baked into
`bootstrap_frames_1to3.json` for this lab). Full cross-config portability requires *sourcing*
these three GUIDs from the target config (a one-time read per config), not randomizing them —
the precisely-characterized residual dependency (3 GUIDs, exact offsets above). A rejected
session also kills the TestClient (it does not survive a bad handshake to serve the next).

## CARD 62 — DONE
`qa_mcp.protocol` can bootstrap frames 1..3 without reading capture bytes (`bootstrap_synth.py`
+ `bootstrap_frames_1to3.json`); proven offline (round-trip vs an independent session, 4 tests)
and live (synthesized fresh-session active-window). **Portability note:** the session/manager
GUID `e23134a2-…` and `7f58f27d-…` token remain template constants for this lab build; they are
the residual version/config dependency for frames 1..3 (the counter + ticket GUID are now fully
synthesized). Frames 4+ are still captured-derived — a separate, future scope.

## Synthesis plan (card 62 acceptance)
1. Template frames 1..3 from the invariant byte layout + two inputs: the counter base and
   the frame-3 ticket GUID (+ 8-byte field). Generate both fresh per session.
2. Keep the `e23134a2`/`7f58f27d` identifiers as documented constants for now (portability
   caveat recorded above).
3. Prove: a fresh TestClient session bootstrapped from synthesized frames 1..3 (no captured
   bytes) completes the handshake and passes an already-accepted read-only op
   (e.g. active-window context).
4. If the frame-3 token must derive from the client ticket, document the negotiation and the
   exact transform.

## Repro
`python -c "from qa_mcp.protocol.bootstrap import CaptureBootstrap; ..."` diff of
`captured_frame(1..3)` across two capture dirs (see this session's transcript).
