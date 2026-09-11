# 79. Native value-read — make the runner verify action EFFECTS (not just acceptance)

## Status
4.done

## RESOLVED — native value-READ works (2026-06-14); effect-loop input-commit is the remaining gap
- **Native value-read PROVEN (no Vanessa).** `native_openform_probe` opens the fixture form (replay
  tm-v1's CIButton "qa mcp protocol fixture v1" click, frames 8-17) then reads PF_EDIT_STRING. Response is
  byte-exact to the original: `EditField[PF_EDIT_STRING]\x81\x81\x81\xfa\x14PF_EDIT_STRING_VALUE` — value
  mode 0x81 (was the no-value 0x88), real field value surfaced. Commit `773d009`.
- **The two fixes:** (1) OPEN the form first (the synth session was stuck on HomePage); (2) rebind the
  **SecondaryFrame GUID** (session-specific — the live form opened as e.g. SecondaryFrame[01446e1f], not
  the captured 73c822ff). Added `secondary_frame_guid` rebinding to the protocol module + action rebinder.
- **Effect loop (`native_effect_probe`): open ✓ → read default ✓ (PF_EDIT_STRING_VALUE) → input ✗.** The
  input frames replay & are accepted, but the value does NOT change: the input's own response carries no
  marker (vs the capture's cli 284 which shows PF_INPUT_PROOF), and the re-read still returns the default.
  Tried: single input frame; the 283/284 commit pair (they differ at off 47/257/258 — 0x88 set + 0x81
  commit); the full lead-in 280-284 (focus `pf_edit_string` + read pair + commit pair) with GUID rebind —
  none commit the value.
- **Remaining gap (next):** _(2026-06-15 UPDATE: the EDIT-MODE-activation guess in this bullet is REFUTED —
  there is no skipped activation frame, and the GUID rebind is correct; see "Linux continuation
  (2026-06-15)" below. The gap is cumulative form state.)_ the input-commit needs form/field state our
  minimal session lacks — likely the
  field must be put into EDIT MODE (a click/activate on PF_EDIT_STRING, not just the focus frame 280), or
  the captured input depends on session state from the original's ~280 preceding frames. Same shape as the
  form-open discovery, but for input. Investigate what activates edit mode (compare the field's state in
  the capture right before 280 vs our session), then replay that activation before the input.
  Artifacts: `tools/protocol-research/native_effect_probe.{py,ps1}`, `native_openform_probe.{py,ps1}`,
  merged template `runtime/.../templates/tm-v1-open-plus-valueread/`.

## Cross-machine handoff (continuing on Linux, 2026-06-15)
- **Reproducible template build:** `tools/protocol-research/build_tm_v1_open_template.py` regenerates the
  merged open+value-read template from the capture (the template under `runtime/.../templates/` is
  gitignored). Run it first on the new machine. It extracts open frames 8-17 + value-read 218-221 and
  injects the rebindable `secondary_frame_guid_ascii` field.
- **Gitignored inputs (NOT in git — must be present/synced separately):** the captures
  `runtime/protocol-research/captures/{tm-v1-ro-batchQ3, fixture-input-capture}` and all
  `runtime/.../templates/`. The repo lives under a YandexDisk-synced folder on Windows; ensure the same
  `runtime/` content is available on Linux (sync the folder, or re-capture).
- **Live-test harness is Windows-only:** the `.ps1` wrappers launch `1cv8.exe /TESTCLIENT` and use
  `Get-NetTCPConnection`. On Linux they won't run as-is. The Python probe cores (`native_*_probe.py`) are
  portable and only need `--host/--port` pointing at a running 1C TestClient listener; the static capture
  analysis (the bulk of the next step) is fully portable. To run live on Linux you'll need a reachable
  1C TestClient (Linux 1C server, or point at the Windows box's port) and a small shell launcher replacing
  the `.ps1`.
- **Start here next session:** read the field's state in `tm-v1-ro-batchQ3` (or `fixture-input-capture`)
  immediately BEFORE the input focus frame (fixture-input-capture mgr ~280) to find what puts the field
  into EDIT MODE; replay that activation before the input pair (283/284), then re-run `native_effect_probe`
  expecting `read_after_input_value == PF_INPUT_PROOF`.

## Linux continuation (2026-06-15) — input-commit forensics: two cheap hypotheses refuted
Reproduced the static-analysis environment on Linux (confirms the handoff's "static analysis is fully
portable" claim): synced the gitignored captures `tm-v1-ro-batchQ3` + `fixture-input-capture` from the
Windows box via scp, and the probe/analysis cores run under plain `python3` with `PYTHONPATH=src` (the
`qa_mcp.protocol` / `replay_probe` modules are pure stdlib). New portable tool committed:
`tools/protocol-research/analyze_input_editmode.py`.

Pinned the PF_EDIT_STRING input sequence in `fixture-input-capture` (manager ordinals): `M279 focus
(lowercase ui-id pf_edit_string) → M280/281 read pair (req mode 0x88/0x81) → M282/283 SET (carry
PF_INPUT_PROOF; the capture's response echoes the marker at mode 0x81)`. The effect-probe replays
`[ordinal-3 .. ordinal+1] = 279..283` — i.e. it already sends the focus, the read pair AND the set pair.

- **"a skipped edit-mode activation frame" — REFUTED.** `pf_edit_string` (the lowercase ui-id used by
  focus/activate commands) appears in exactly ONE manager frame, M279, already replayed. Nothing edit-mode
  is skipped before the lead-in. M276–278 (len 375) are reads of a DIFFERENT field
  (`Group[Группа1].EditField[Контрагент]`), correctly excluded.
- **"wrong GUID rebind" — REFUTED.** The probe's extraction yields `ManagedForm 4451d8b2 /
  SecondaryFrame d848f317`, matching the input frames exactly; the capture carries a single ManagedForm
  GUID (486 refs) → no ambiguity. Rebind targets are correct.
- **Macro-structure:** `fixture-input-capture` has the fixture form ALREADY OPEN (`SecondaryFrame[d848f317]`
  from frame 11; zero HomePage frames; no CIButton). It cannot be replayed standalone to OPEN the form, so
  the cross-capture splice (open from `tm-v1-ro-batchQ3`, input from `fixture-input-capture`) is
  structurally necessary — two sessions, two form GUIDs (rebound).

**Conclusion:** the write-commit failure is NOT a single missing frame and NOT a GUID bug. The remaining
explanation consistent with all evidence is that the SET (M282/283) is **cumulative-state-gated** — it
commits only when the client form/field carries the state built by `fixture-input-capture`'s ~278
preceding frames (the early PF_EDIT_STRING reads at 193–196, Контрагент/V4 navigation, …), which the
open-then-jump synth session never builds. Same shape as the value-READ being gated on the form actually
being open (the resolved part of this card), one layer deeper.

**Next experiment (needs a LIVE TestClient — blocked on this Linux host, no runtime here):** test the
cumulative-state hypothesis by replaying a wider CONTIGUOUS pre-input prefix before the commit. Added a
`--lead-in N` knob to `native_effect_probe.py` (default 3 = unchanged) so it is a one-flag sweep, e.g.
`--lead-in 30` / `--lead-in 90`. If a contiguous prefix makes the SET response carry `PF_INPUT_PROOF`
(value-mode 0x81), the effect loop closes; if even full contiguity from the open fails, escalate the
acceptance-bar scope decision (is "action accepted" sufficient, or keep a value-oracle for the assert).
Re-run on a host with a reachable TestClient: `analyze_input_editmode.py` first (re-pins the frames), then
`native_effect_probe.py --lead-in <N> --manager-templates <combined-open+valueread template>`.

## Linux LIVE sweep (2026-06-15) — cumulative-state-prefix hypothesis REFUTED; decision needed
Ran the queued `--lead-in` experiment LIVE — first native TestClient runtime on the migrated Linux
contour (`xvfb-run` gives the thin client a DISPLAY; the portable `native_*_probe.py` cores run under
`python3 PYTHONPATH=src` against the Linux-booted client on port 15381). Full evidence:
`docs/protocol-research/evidence/native-effect-verification-linux-2026-06-15/findings.md`.

- **Linux runtime milestone (read path) PROVEN:** boot → synth handshake → open fixture form → native
  value-READ all work live on Linux. `native_openform_probe` returns `secondary_frame_opened=true`,
  `value_mode_on=true`, `pf_edit_string_value_seen=true` (live `SecondaryFrame[030a5414]` rebound from
  captured `73c822ff`). The card's "native value-READ works" part is reproduced on Linux (was Windows-only).
- **Effect sweep — REFUTED.** `native_effect_probe --lead-in {3,15,30,60,90,150,270,275}` all: SET
  `accepted`, response has NO `PF_INPUT_PROOF`, re-read == default → NOT committed. `--lead-in 275`
  (start frame 7) replays the ENTIRE post-handshake `fixture-input-capture` session (268 frames, full
  cumulative state) rebound to the live form, input replayed verbatim — still no commit. `--lead-in ≥278`
  (start ≤6) hits the capture's own 7-frame handshake → BrokenPipe (client reset), so start=7 is the
  widest possible contiguity. Widening 3→275 changed nothing.
- **Conclusion:** a pure wire-frame replay session **cannot reproduce a value-INPUT effect**, even with
  verbatim input + full contiguous session state + correct live GUIDs. The input-commit is gated on
  per-input manager-side state (an ephemeral generation/echo token from the genuine `ТестируемоеПриложение`
  input API), not on wire bytes / form state / sequence / GUIDs. Consistent with card 76
  (manager-originated identifiers are unlearnable) and card 78 (formats come from captures). This is the
  boundary of write-from-capture for input-commit.

### DECISION NEEDED — acceptance bar for input/effect verification (pick one; the rest of the card is unblocked-read)
Value-READ effect verification (read a field's live value + assert) is PROVEN live. Only the
*replay-driven write of a NEW value with a verified effect* is blocked. Forks:
- **(1) Accept "action accepted" as the input acceptance bar** — the runner verifies inputs are accepted,
  asserts on READS (which return live values). Vanessa-free, ships now; weaker effect guarantee for inputs.
- **(2) De-novo input synthesis** — crack the input-commit ephemeral token and synthesize a genuine input
  (the deep frontier; verbatim replay failing suggests the token is non-reproducible from captures).
- **(3) Manager-side input API** — drive input via a `ТестируемоеПриложение`-equivalent call (card 77
  `agent_runtime`) so the genuine API emits the commit frames live; then read+assert the effect. Most
  likely the real path to a true effect-verifying input, but it means the Python manager generates input
  (not replays it) → needs the input-commit protocol understood (overlaps fork 2).

## RESOLUTION (2026-06-15) — Fork 1 chosen, implemented + demoed LIVE; ready for done
Operator chose **Fork 1**: input actions assert "accepted"; the EFFECT is verified by a subsequent
READ of the field's live value. Implemented and proven live on Linux, no Vanessa:
- New native capability `read_form_value` — open the fixture form + run the value-read + parse the
  field's LIVE value (0x81 value mode). Wired into `SessionHandle`, the `ScenarioRunner`
  single-session dispatch, the model step kinds, the Gherkin transpiler (`значение поля '…' содержит
  '…'`), and a `form-value-read` read-only descriptor. New value-read parser
  `extract_edit_field_value` / `value_mode_present`.
- **Live `.feature` demo PASSED** (`effect_read.feature` → runner → live TestClient, no Vanessa):
  open form → `read_form_value PF_EDIT_STRING` asserts the live value contains `PF_EDIT_STRING_VALUE`
  (value_mode_on=True, value extracted) → `input_text` accepted. Evidence:
  `docs/protocol-research/evidence/native-effect-read-verification-2026-06-15/`.
- 160 offline tests pass.
- Forks 2/3 (de-novo / manager-side input-commit so a NEW value's write-effect can be asserted) are
  spun out to **card 80**. This card's actionable scope is complete → move to `4.done` via the OPSX
  publish flow.

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-14: spun off from card 78 direction 2. The flagship runner drives actions and asserts on
  reads, but action steps only assert "accepted" (the command was sent + the client responded). A real
  test manager (Vanessa's role) must verify EFFECTS: after an action, read the affected field's VALUE
  and assert it changed. This card closes that gap.

## Findings (card 78 dir2, 2026-06-14)
- The read-after-write MECHANISM works: a post-action template read (frames 101..106, > the linear
  cursor) succeeds in the synthesized session (`native_action_session_spike.py --verify-value`).
- BUT no current read exposes a field's DATA VALUE:
  - the action response is a bare protocol ACK (no state echo — checked PF_INPUT_PROOF / PF_EDIT_STRING
    / PF_LAST_ACTION / PF_ACTION_COUNTER, none present);
  - `form_summary` and element-details (101..106 via `extract_element_details`) expose element
    STRUCTURE (names / captions / paths / ui_identifiers), NOT the field's current value;
  - the field VALUE (`ПолучитьПредставлениеДанных`) is only read via the raw-API command_kind path
    (manager-fixture-v1 `element_state`), i.e. manager-side BSL — NOT a wire frame the Python
    synthesized session sends.
- So the Python synthesized-session runner can read STRUCTURE but not VALUES; verifying a field's
  value-change needs a CAPTURED `ПолучитьПредставлениеДанных` value-read wire frame to replay.

## Plan
- Capture a value-read wire flow: an action manifest / read that issues `ПолучитьПредставлениеДанных`
  on PF_EDIT_STRING (the read_only `element_state` command already does this manager-side — capture its
  WIRE exchange through the proxy), so the value-read frames are in the corpus.
- Add a `read_value` operation to `SessionHandle` (replay the captured value-read frames, rebind mfg,
  parse the returned data presentation string).
- Verification scenario: read_value(PF_EDIT_STRING)=default → input_text(PF_EDIT_STRING ← new) →
  read_value(PF_EDIT_STRING)=new → assert changed. Safe (in-memory fixture field, no DB mutation).
- Wire `read_value` + assertion into `run_single_session` / the runner so a `.feature` can express
  "результат содержит '<new value>'" after an input.

## Acceptance
- A scenario runs end-to-end through qa_mcp (no Vanessa): input a value → read the field's live value
  → assert it equals the input (and differs from the default). status=passed, effect verified.

## Investigation (2026-06-14) — value-read frames pinned; the real blocker is the template
- The field VALUE **is** present in a wire response as UTF-8: in `tm-v1-ro-batchQ3` (the synthesized
  session's own template capture) the manager value-read for PF_EDIT_STRING is at **manager frames
  218-221** (they reference `PF_EDIT_STRING`) and the client responses at **client ord 220/221 contain
  `PF_EDIT_STRING_VALUE`**. (Also present in tm-v1-ro-batchA/B/C3/D, fixture-input-capture.)
- BUT `run_segment` renders frames from `manager_frame_templates.json` (covers frames **8-106** only) →
  `RuntimeError: Manager template 218 not found`. The value-read frames are NOT templated. And the
  templated element-details read (101-106) carries STRUCTURE, not the value (confirmed: grep of the
  101-106 response found neither the value nor the default).
- **So the precise blocker:** the value-bearing read (frames ~218-221) is outside the template's
  coverage. Two paths: (a) extend `manager_frame_templates.json` to include the value-read frames
  (re-run the template-extraction tooling that built the 8-106 template, widened to the value-read
  range, with the right dynamic-field offsets for ack_guid/sequence/managed_form_guid), then
  `run_segment` can render them; or (b) raw-replay manager_chunks[218..221] from the capture via a
  run_action-style send with sequence/GUID rewriting. (a) is cleaner + reusable.
- The spike (`native_action_session_spike.py`) gained `--verify-frames a-b`; the read-after-write
  control flow is in place — only the renderable value-read template is missing.

## Log
- 2026-06-14: card created (spin-off from card 78 dir2); read-after-write mechanism proven, value-read
  gap identified — template reads give structure, the field value needs a captured ПолучитьПредставлениеДанных flow.
- 2026-06-14: value-read frames pinned (tm-v1-ro-batchQ3 mgr 218-221, value in client resp 220/221);
  blocker = those frames are outside manager_frame_templates.json (8-106). Next: extend the template to
  the value-read frames (or raw-replay 218-221), then assert PF_EDIT_STRING value == input after the action.
- 2026-06-14 (template-extension path DONE; deeper finding): `extract_manager_templates.py tm-v1-ro-batchQ3
  --frames 218-221` → merged into a combined template (`runtime/.../templates/combined-8-106-plus-valueread/`).
  The synthesized session now RENDERS + SENDS frames 218-221 successfully (spike `--TemplatesPath`,
  `--verify-frames 218-221`, status=ok — no "template not found", no divergence). **BUT the response is a
  STRUCTURE read, not a value:** it contains element PATHS (`SecondaryFrame[…].ManagedForm[…].Group[PF_GROUP_EDITS]
  .EditField[PF_EDIT_STRING]`) — NOT the data value. So frames 218-221 are an element-tree/summary read
  (like 101-106), not `ПолучитьПредставлениеДанных`. The value `PF_EDIT_STRING_VALUE` seen in the ORIGINAL
  capture's client resp 160/220/278 is not surfaced by replaying these structure-read frames.
  **Revised blocker:** the actual VALUE-read wire op (ПолучитьПредставлениеДанных) is not yet isolated —
  needs frame-level analysis of which exchange carries the data value (vs the structure tree), likely a
  dedicated capture of an `element_state` read with byte-level diffing. Template-EXTENSION machinery is
  proven (any frame range can now be made renderable); the remaining work is identifying the right frames.
- 2026-06-14 (FULL root-cause): the value-read RESPONSE format IS now identified — in the original
  capture cli[220] = `EditField[PF_EDIT_STRING]\x81\x81\x81\xfa\x14PF_EDIT_STRING_VALUE` (element path +
  byte 0xfa + length 0x14=20 + the value). So frames ~220 ARE the value-read (frame 218-221 reference
  PF_EDIT_STRING by name → self-contained find+get). BUT our REPLAY of 218-221 returns
  `EditField[PF_EDIT_STRING]\x88\x81\x81…` (byte 0x88, binary, NO length-prefixed value) — a generic
  STRUCTURE, not the value. **Likely root cause = sequence mismatch:** the template frame 218 carries
  `delta_from_frame4_sequence ≈ 214` (its position in the original 304-frame batch), but our synthesized
  session has only sent ~18-23 frames before the value-read (bootstrap 1-10 + frame 11 + 12-17 + the
  action) → the renderer emits sequence = base+214 while the client expects ≈ base+20, so the client
  returns a generic structure instead of the requested field value. (Single actions tolerated sequence
  because run_action sends RAW captured frames, not re-rendered ones.)
  **Concrete fix (next session):** re-number the value-read frames' `delta_from_frame4_sequence` to match
  their actual send position in the synthesized session (small delta, contiguous with the reads), then
  re-run — expect the response to carry `\xfa\x14<value>`; after the input, the value should be the new
  one (PF_INPUT_PROOF). Possibly also send a contiguous block (not skip) or use run_action raw-send for
  the value-read to sidestep delta entirely. ARTIFACTS in place: combined template
  `runtime/.../templates/combined-8-106-plus-valueread/`, spike `--TemplatesPath/--verify-frames`.
- 2026-06-14 (SEQUENCE HYPOTHESIS REFUTED — corrected root-cause). Ran the queued fix: renumbered the
  value-read frames' delta to contiguous (218→14, 219→15, 220→16, 221→17) in
  `runtime/.../templates/combined-valueread-contiguous/` and re-ran the spike live (run 20260614-212149).
  **Result: byte-identical `0x88` no-value response** (`EditField[PF_EDIT_STRING]\x88\x81\x81\xe1…`,
  verify_resp len 947, same segments as the delta-214 run). Sequence is NOT the discriminator.
  Supporting static evidence:
  - The value-bearing requests are manager frames **219 and 220** (NOT 218-221). Aligned by global chunk
    order: mgr219(len268)→cli VALUE, mgr220(len271)→cli VALUE, mgr221(len268)→cli structure, mgr218 is a
    DIFFERENT field (PF_V4_SUPPORTED_SCENARIOS). Frames 219 and 221 are byte-identical except sequence +
    nonce, yet 219→value / 221→structure — so the request content/sequence does not decide it.
  - The request frames replay **byte-correctly**: the 16 "unknown" bytes at body offset 51-66 (not a
    template dynamic field) are **identical across two independent capture sessions** (tm-v1-ro-batchQ3 vs
    fixture-input-capture) → protocol constants, safe to replay verbatim. Every session-variant field is
    correctly rebound (ack_guid, nonce, ManagedForm GUID).
  - **SecondaryFrame[73c822ff-…] is a session-INVARIANT constant** — the live client echoes the exact same
    GUID. The element path is correctly addressed; the client finds the field but returns "no value".
  - **Response-mode mismatch:** in the ORIGINAL capture the byte after `EditField[…]` in client responses
    is `0x81` (205×, value-bearing) or `0x8b` (8×) — **never `0x88`**. Our synth-session replay produces
    `0x88` (the "no-value/structure" mode) which **never occurs anywhere in the original capture**.
  - The client tolerates large sequence gaps for both reads (frames 101-106 render at delta 97, a jump
    from 13) and actions (the raw input frame carries seq 13858, wildly off the synth base) — it does not
    reset on non-monotonic sequence.
  **TRUE ROOT CAUSE: the value read is a STATEFUL DELTA/DIFF protocol.** The client emits a field's data
  value (`0x81 … 0xfa <len> <value>`) only when its internal session/generational state says the value is
  new/changed relative to what the manager has already been told. Our frame-skipping synth session
  (bootstrap 1-10 → frame 11 → frames 12-17 → raw action → jump to 218-221) reaches a client state that
  never existed in the original capture, so the client returns the no-value `0x88` structure response.
  The value is gated on the cumulative state built by the SKIPPED frames 18-217, NOT on the request bytes
  or the sequence number. ⇒ Pure frame-skipping replay cannot surface a field VALUE.

## Revised options (2026-06-14) — sequence path is dead; these are the real forks
- **(A) Full-contiguity replay** — template frames 18..220 and send them all so the client's delta-state
  matches the original at 219/220. Machinery exists (extract_manager_templates proven on any range). BUT
  the original frames 18-217 re-enact the recorded session's OWN actions (dialog-recovery, mutation-v3,
  etc.), so the value read would reflect the ORIGINAL scenario's state, not necessarily OUR input's
  effect — weak as effect-verification, and heavy.
- **(B) Full-snapshot text read instead of delta read** — the original has a bulk frame (mgr 159/160)
  whose response is a plain-text dump `…PF_EDIT_STRING=PF_EDIT_STRING_VALUE->…`. A snapshot/dump read (vs
  the 218-221 delta read) may return values independent of delta-state. Needs isolating that frame's
  request shape and confirming it generalises to PF_GROUP_EDITS. Most promising for a clean value read.
- **(C) Pivot the effect oracle off the wire** — verify the value via the proven manager-fixture-v1
  `element_state` (ПолучитьПредставлениеДанных) read. PROBLEM: the synth-session input is in-memory on the
  synth socket; a separate read connection would not see it (non-persistent). Only works if the read runs
  on the SAME socket — i.e. back to the wire approach.
- **Recommendation:** pursue (B) — isolate the snapshot/dump value-read frame; it sidesteps the delta-
  state requirement that (A) cannot cleanly satisfy and that (C) cannot observe. If (B) also turns out to
  be delta-gated, escalate the scope decision (is "action accepted" a sufficient acceptance bar, or do we
  keep Vanessa as the value-oracle while the action path stays Vanessa-free?).

## TRUE ROOT CAUSE (2026-06-14, option-B investigation) — the fixture form is never OPENED
Investigating B surfaced the actual root cause, which **overturns every prior hypothesis** (sequence,
delta protocol, value-realization mode — all were symptoms):
- **Our synth session never opens the fixture form.** It lands on the infobase **`HomePage`** and stays
  there. Diagnostic `native_valuemode_probe.py` (send 11→17→18-106 contiguous→218-221): every response in
  frames 11-17 references `HomePage[6ca75e50-…].ManagedForm[8a70389c-…]`; frames 18-106 also HomePage; the
  value-read 218-221 returns `0x88` no-value stubs.
- **The original capture has the fixture form open as a `SecondaryFrame` by frame 16.** First SecondaryFrame
  appears at original cli ord 16 / mgr frame ~15-16 (a HomePage→SecondaryFrame transition: cli 1-15 have no
  SecondaryFrame, cli 16+ do). The template frames 12-17 were captured WHILE that SecondaryFrame was open,
  so they *assume* it is open.
- So our replay sends value-reads addressed to `SecondaryFrame[73c822ff-…].ManagedForm[<rebound>]` — a form
  that **does not exist** in our HomePage-only session. The client echoes the requested path but returns the
  generic `0x88` stub (never a value). That is why EVERY EditField read in our session is `0x88` while the
  original is `0x81` everywhere from frame 40 on, why sequence renumbering changed nothing, and why no
  "snapshot" read exists — there is no realized form to read from.
- `SecondaryFrame[73c822ff-…]` being a session-invariant constant is consistent: it is the fixture form's
  stable window id; replaying it does not OPEN the form, it just names it.

**Corrected blocker / next step:** OPEN the fixture form (the `SecondaryFrame` carrying `PF_GROUP_*`) in the
synth session BEFORE reading. The original opens it at ~mgr 15-16 (HomePage→SecondaryFrame). This is
card-78-style navigation/open-action work (open_list / click_button were already proven live in the synth
session). Identify the open-form command frame, synthesize/replay it (adapting to our HomePage state), and
confirm the active form flips to the SecondaryFrame; THEN the existing value-read frames should return
`0x81 … 0xfa<len><value>` because there is finally a realized form to read. Diagnostic artifacts:
`tools/protocol-research/native_valuemode_probe.{py,ps1}`, run `runtime/.../valuemode-probe/20260614-213631`.

### Mechanism pinned + implementation plan (2026-06-14)
- **Why our template never opens the form:** the 8-106 manager template was extracted from a DIFFERENT
  capture (`20260602-frames08-106-utf16-managedform`) that sat on the **HomePage** — combined template
  frame 12 body = `HomePage[6ca75e50-…]`. tm-v1-ro-batchQ3 (the fixture session) instead frame 12 =
  `MainFrame[6ca75e50-…].CI`. We replay the HomePage template's nav then try to read fixture fields → the
  fixture SecondaryFrame is never opened. (Two captures, two different active forms, mixed together.)
- **How tm-v1-ro-batchQ3 opens the fixture form (frames ~9-16):** read `MainFrame[6ca75e50].CI`
  (command interface) → locate `CIButton[0b8e3358-2a9d-4692-a55d-c2f776d98083:085a8c57-…]` → execute the
  command captioned **"qa mcp protocol fixture v1"** → the form opens as
  `SecondaryFrame[73c822ff-…].ManagedForm[fa3103a3-…]` "QA MCP Protocol Fixture V1" (cli ord 16+).
- **Stable GUIDs (replay-safe):** `MainFrame 6ca75e50` is constant — it equals our live HomePage GUID;
  `SecondaryFrame 73c822ff` is constant (live client echoes it); `CIButton 0b8e3358:…` is config-derived
  (command/section metadata) so expected stable. The fixture **ManagedForm GUID is assigned at open time**
  (HomePage got `8a70389c` live) → observe it from the open response and rebind the value-read frames to it
  (existing `extract_managed_form_guid` + action-resolver rebinder already do exactly this).
- **Plan:** (1) `extract_manager_templates.py tm-v1-ro-batchQ3 --frames 8-17` (the CIButton-click open
  sequence) with correct dynamic fields (ack_guid / sequence / any per-session GUIDs). (2) New runner:
  synth bootstrap 1-10 → send the tm-v1 open sequence (8-17) → assert active form is now the SecondaryFrame
  (capture its live ManagedForm GUID) → run the value-read 218-221 rebound to that GUID → expect `0x81 …
  0xfa\x14PF_EDIT_STRING_VALUE`. (3) Then the full effect loop: read default → input → read new value.
