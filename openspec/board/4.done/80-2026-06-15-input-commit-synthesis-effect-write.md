# 80. Input-commit synthesis — true WRITE-effect verification (card 79 forks 2/3)

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-15: spun off from card 79. Card 79 proved (live, Linux) that a pure wire-frame replay
  session **cannot reproduce a value-INPUT effect** — even replaying the input verbatim with the full
  contiguous post-handshake session state (`--lead-in 275`, start frame 7) and correct live GUIDs, the
  SET is ACKed but never realizes the value (no `PF_INPUT_PROOF` echo; re-read returns the default).
  Operator chose Fork 1 (input = "accepted" + verify EFFECT via a READ) for the shipping manager; this
  card tracks forks 2/3 — the deep frontier that would let the manager assert a NEW value's write-effect.
  Evidence: `docs/protocol-research/evidence/native-effect-verification-linux-2026-06-15/findings.md`.

## Hypothesis (from card 79 evidence)
The input-commit is gated on per-input manager-side state — an ephemeral generation/echo token produced
by the genuine `ТестируемоеПриложение` input API — not on the wire bytes, form/field state, sequence, or
GUIDs (all of which the replay gets right). Consistent with card 76 (manager-originated session
identifiers never appear in client responses → structurally unlearnable) and card 78 (action FORMATS
come from Vanessa-driven captures). So the value-write is the one operation write-from-capture cannot
retarget to a new effect.

## Forks
- **Fork 3 (manager-side input API) — most promising.** Drive input via a `ТестируемоеПриложение`-
  equivalent so the genuine API emits the commit frames live, then read+assert the effect. The Python
  manager would GENERATE input (not replay it) → requires understanding the input-commit token.
- **Fork 2 (de-novo synthesis).** Crack the ephemeral input-commit token and synthesize a genuine input.
  Overlaps fork 3; verbatim-replay failure suggests the token is non-reproducible from captures.

## First step (gated)
Diff two CAPTURED genuine inputs of the same field to isolate the per-input ephemeral token: which bytes
change between two real input-commits beyond the known dynamic fields (nonce/sequence/ack/GUIDs)? That
isolates what the replay carries stale. This needs either a Linux capture wrapper (the proxy `.ps1` is
Windows-only) or a fresh capture on Windows — i.e. it is **blocked on capture tooling**, decide which.
Then test whether reproducing that token (synthesized per send) makes the SET commit.

## FINDINGS (2026-06-15) — the write-effect gate is OFF-WIRE; forks 2 + same-session-replay are dead ends
Investigated offline then with a decisive live experiment. Evidence:
`docs/protocol-research/evidence/card80-input-commit-forensics-2026-06-15/findings.md`.

- **Offline (echo-token refuted):** the SET request (`fixture-input-capture` mgr 282/283) carries no
  unrebound client-issued token. Its only session-variant fields are ack/mfg/sfg (already rebound),
  the sequence, and a per-frame nonce at offset ~68. That nonce is proven HARMLESS-when-stale: the
  value-READ frames carry the same nonce and the openform probe replays them stale yet the READ works
  live (card 79). New tool `analyze_input_commit_token.py` (`mystery_echo_count: 0`).
- **Live (splice / card-76-wall refuted):** `native_samesession_commit_probe.py` replays
  `fixture-input-capture` VERBATIM in its own bootstrap (no splice) through the SET to the capture's
  own post-SET value-read. Result: `frames_sent=473, diverged_at=null` (zero divergence), but
  `set_response_has_marker=false` and `committed=false`. Even a faithful, full, same-session replay
  does NOT commit.
- **Conclusion:** no wire-frame replay reproduces the value-INPUT commit under any tested config
  (synth+splice card 79; captured-bootstrap same-session this card). The commit is gated on manager-
  side runtime/edit state the genuine `ТестируемоеПриложение` input API maintains in the manager
  process — NOT serialized onto the wire. ⇒ **Fork 2 (crack a request token) and same-session
  capture+replay are dead ends.** Fork 3 (re-implement the manager-side input path) is the only route
  to true write-effect; it is substantial. Practical bar remains **Fork 1 (shipped, card 79)**:
  effect verification on a READ.
- **Recommendation:** keep Fork 1 as the manager's input acceptance bar; pursue Fork 3 only if a real
  scenario demands asserting a written value's effect. Card stays in backlog as the Fork-3 record
  (no longer "first step gated" — the first step is done and dead-ended the cheaper forks).

## FRAME-DIFF (2026-06-16) — REFRAMES the conclusion: commit is an ON-WIRE SEQUENCE, Fork 2 is feasible
Converted the genuine `commit-capture.pcap` to the proxy capture format (new dependency-free
`tools/protocol-research/pcap_to_traffic.py`, linktype-1/loopback → `traffic.jsonl`; reusable for ALL
analyzers over tcpdump captures) → `runtime/protocol-research/captures/genuine-commit-converted/`
(664 mgr→cli + 615 cli→mgr chunks). Ran `analyze_input_commit_token.py` on it.

- **Both commit frames carry NO mystery token.** The PF_EDIT_STRING SET = `mgr[354]` (len 288) and the
  focus-change PF_EDIT_NUMBER SET = `mgr[359]` (len 281) each report **MYSTERY echoes = 0** — every byte
  shared with preceding client responses is a KNOWN rebindable field (managed_form_guid / mfg / sfg / ack)
  or an ASCII marker (`_MAIN].Group[PF_`). No unrebound client-issued token in EITHER frame.
- **The commit is the SEQUENCE, not a token.** Wire order: `mgr[354/355]` SET PF_EDIT_STRING edit-text →
  `mgr[357-360]` SET/focus PF_EDIT_NUMBER (this focus-change off PF_EDIT_STRING is what commits it) →
  `cli[514/515]` client returns the committed PF_EDIT_STRING value → `cli[572/573]` form update mirrors it
  into PF_PAGE_A_FIELD (server `ПриИзменении` ran). The second field never committed (no following focus
  change) — exactly matching the read-back.
- **Why the earlier replays failed (resolved).** Card-79 synth and the same-session verbatim probe replayed
  the SET and went straight to the value-read — they NEVER sent a focus-change between SET and read, so the
  edit-text was never committed. The failure was a MISSING frame (focus-change), not an off-wire gate or a
  non-reproducible token. The prior `analyze_input_commit_token` "MYSTERY=0 → manager-side gate" reading was
  drawn from a single SET; with the focus-change frame in view the real ingredient is the SEQUENCE.
- **⇒ Fork 2 (de-novo synthesis) is FEASIBLE.** qa_mcp should be able to WRITE a value with no Vanessa by
  sending: (1) the SET EditField for the target, then (2) a focus-change EditField to any other field —
  both rebound for the known GUIDs only. The definitive confirmation is the Fork-2 implementation test:
  qa_mcp replays SET+focus-change against a live client and a value-read returns the new value. Fork 3
  (manager-side input API) is no longer required for the basic value-commit.

## LIVE FORK-2 REPLAY (2026-06-16) — CONFIRMS off-wire; corrects the "Fork 2 feasible" read; Fork 3 required
Tested Fork-2 by replaying, against a live TestClient via qa_mcp's synthesized session, the ACTUAL frames
that committed live under Vanessa. BOTH attempts: `effect_verified=false`.
- Attempt #1: SET from `fixture-input-capture` (280-283) + commit-frames 471-474 → no commit (471-474 were a
  read pass, not a focus-change).
- Attempt #2: SET (354) + focus-change (357-360) from `genuine-commit-converted` — the exact frames that
  committed live — mfg/sfg-rebound to the live form → still `effect_verified=false`, read-after default,
  no marker echo (`action_response_has_marker=false`).
- **Decisive argument it is OFF-WIRE, not an incomplete rebind:** the SAME mfg/sfg rebind makes the value-
  READ work live (card 79 reads the field fine). So the rebind is adequate. Yet the value-SET+commit, with
  that same adequate rebind AND the genuine committing frames AND the focus-change, does NOT commit ⇒ the
  commit is gated on manager-side runtime/edit state the genuine `ТестируемоеПриложение` input API holds,
  NOT serialized on the wire.
- **Correction to the earlier frame-diff note:** "MYSTERY echoes = 0" correctly ruled out a CLIENT-issued
  token in the SET bytes (hypothesis a). It did NOT prove replayability — the gate is the MANAGER-side state
  (hypothesis b), which this live replay now confirms. The frame-diff insight that survives: the genuine
  COMMIT is the SET→focus-change SEQUENCE (the genuine manager does both), and the read↔value split is real
  — but a clean focus-change in the replay still does not commit.
- **⇒ [SUPERSEDED — SEE THE "⭐ BREAKTHROUGH" SECTION BELOW.]** This concluded "Fork 2 RULED OUT, Fork 3
  required." That was WRONG: it tested SPLICED replays (genuine input frames on a READ-ONLY tm-v1 bootstrap)
  + had tooling bugs. A faithful FULL-session replay of a genuine INPUT capture DOES commit, and value-
  retarget writes an arbitrary new value. Fork 2 is achieved. (Fork 1 remains a valid lighter bar.)

## FORK 3 — step 1 (2026-06-16): the documented "diff two genuine SETs" is DONE → no wire token; gate = client edit-STATE
Captured a 2nd genuine input (extracted session B from `genuine-input-commit.pcap` port 48002 via
`pcap_to_traffic.py`) and diffed its PF_EDIT_STRING=QAGENUINE2026 SET frame against session A
(`genuine-commit-converted` mgr[354]); both 288 B. After rebinding mfg+sfg+ack the frames differ in only:
- off ~70 (16 B): the manager per-frame **nonce/correlation id** — card-80 forensics already PROVED it is
  harmless-when-stale (the value-READ replays it stale and works live, card 79). NOT the commit gate.
- off 19-20 (2 B): a tiny correlation/ack-tail fragment — also not a gate.
⇒ Independent confirmation of card-80's "no unrebound wire token gates the commit." There is NO SET-frame
byte that, if reproduced, makes a replay commit.

**Re-scopes Fork 3 (important):** the gate is the CLIENT's edit-session STATE, set up by the full
consistent interaction (read field → enter edit mode/activate → set edit-text → focus-change). The live
replays failed because they MIXED captures (open from `tm-v1-ro-batchQ3` + SET from a genuine session) → the
client was never put into the edit-state the genuine SET expects. So Fork 3 is NOT "craft a token" — it is
"reproduce the manager's edit-session interaction so the client enters the dirty-edit state, then commits."
Two routes, both gated on card-76 (manager-originated session state is not learnable from the wire):
  (a) replay a CONSISTENT single-session sequence — genuine-commit's OWN open+activate+set+focus-change,
      rebound — but its open carries Vanessa-bootstrap session context that a fresh qa_mcp bootstrap differs
      from (the card-76 wall);
  (b) re-implement the edit-mode handshake in qa_mcp's manager (the genuine `ТестируемоеПриложение` path):
      read → ВвестиТекст-equivalent that drives the client into edit mode with the live session context →
      focus-change. This needs RE of the edit-mode protocol (what frame/sequence flips the client to
      dirty-edit), beyond static capture diffing.
NEXT sub-step: locate genuine-commit's form-open ordinals and attempt route (a) (one consistent-session
replay) as the cheapest test of the client-state hypothesis; if it too fails, route (b) is the only path and
Fork 3 reduces to the card-76 manager-session-state problem.

## FORK 3 — step 2 (2026-06-16): frame-based Fork 3 EXHAUSTED (sequence test negative); gate is live interaction
Tested the strongest remaining frame-based hypothesis: the binary message counter (offset 19-20 LE) is a
consecutive per-frame counter (`frame4_sequence + delta`; tm-v1 open=base+4..10, value-read=base+214..217).
The replayed genuine input frames carry their OWN session's counter (~17729), LOWER than the live counter
(~41086) → a backwards sequence the client could ignore. Added `native_effect_probe.py --reseq` to rewrite
the input+commit frames' offset 19-20 to CONTINUE the live counter (frame4_sequence+218, +1 per frame).
- Iteration #3 (genuine frames + `--reseq`, reseq_start=41087, monotonic after the last read 41086):
  still `effect_verified=false`, read-after = default, QAGENUINE2026 absent even as UTF-16. No commit.
- **Decisive:** two genuine SET frames from different sessions are BYTE-IDENTICAL after rebinding mfg/sfg/ack
  (only the harmless nonce + the now-rewritten seq differ). One committed live; the rebound+reseq'd replay of
  the same bytes does not. ⇒ **NO frame field is the commit gate.** Frame-based Fork 3 (replay / synthesis /
  re-sequence) is EXHAUSTED — three live iterations (genuine frames; +rebind; +reseq) all fail.
- **Conclusion:** the value-commit gate is the CLIENT edit-session STATE produced by the genuine manager's
  LIVE bidirectional interaction (the edit-mode engine: read→activate→set→focus-change driven against live
  client state/timing), NOT serializable to or reconstructible from wire bytes. This is the card-76 wall at
  its deepest. Fork 3 by frame-crafting is a dead end; the only conceivable native path (route b) is to
  re-implement the manager's edit-session engine as a live interaction — high effort, uncertain feasibility,
  and still gated on card-76 (manager-originated session state).
- **Recommendation for value-WRITE (honest):** (1) keep **Fork 1** (read-effect verification, shipped) as the
  manager's input bar — covers asserting an action's effect; (2) for true value commits, use the **genuine
  Vanessa manager as a write backend** (the hybrid — wired + PROVEN to commit on Linux this session, card 81).
  Pure-native qa_mcp value-commit via the protocol is not achievable by replay/synthesis.

## ⭐ BREAKTHROUGH (2026-06-16): full-session replay COMMITS the value — the "off-wire wall" was wrong
The earlier conclusions in this card ("off-wire gate", "Fork 2 ruled out", "frame-based exhausted", "Fork 3
required") are **SUPERSEDED**. They were artifacts of the SPLICE (a read-only `tm-v1-ro-batchQ3` bootstrap +
spliced genuine input frames) plus three tooling bugs found+fixed this turn. A FAITHFUL full-session replay
of the genuine INPUT session **does commit the value** — no Vanessa, no genuine manager.

**What changed (the real root cause):** our bootstrap was synthesized from `tm-v1-ro-batchQ3`, a Vanessa
**READ-ONLY** capture (`scenario: manager-fixture-v1-readonly`). A read-only session is never input-authorized,
so splicing input frames onto it never applied them. Replaying the GENUINE input session's OWN full frame
stream (handshake → form-open → activate → SET → focus-change), with live GUID rebind, reproduces the
input-capable session.

**Tooling bugs fixed (all masked the result):**
1. `pcap_to_traffic.py` filtered by client port only → MIXED 4 manager connections (tcpdump on the listen
   port catches every reconnect). Added a `manager_port` filter; the real session is the dominant connection
   (39580). The "rich 2-round handshake" earlier finding was a mixing artifact — the clean handshake is one
   round (4 text frames + binary).
2. `native_samesession_commit_probe.py` broke on the FIRST empty response → false "diverged_at". But many
   frames (4-byte control/ACK, input commands) legitimately get no response. Fixed: continue past empties.
3. Then it broke on a RUN of empties (a run of 4-byte control frames). Fixed: only count empties from
   SUBSTANTIVE frames (>16 B) toward divergence; a closed socket trips the sendall OSError.

**Result (clean run, fresh TestClient, genuine-commit-conn replayed frames 0→554):**
`reached_set=true`, `set_response_has_marker=true` (client ECHOES the input → it APPLIED it),
`real_divergence_at=null` (full session replays). The post-input read frames (549/550) return
`EditField[PF_EDIT_STRING]\x81\x81\x81…QAGENUINE2026` — **the committed VALUE is QAGENUINE2026, default
absent.** `committed=true`. ⇒ value-WRITE-with-commit IS achievable by qa_mcp via faithful full-session
replay. (Note: `extract_edit_field_value` returned None on this response variant — the value follows
`\xfa\r`/`\xe0..` not `\x14`; minor parser gap, the value is plainly present.)

**Reconciles all prior evidence:** the SET bytes carry no token (true); reads tolerate stale nonce/seq
(true); BUT the input needs an input-AUTHORIZED session, which only the full genuine-session replay
establishes — not the read-only-bootstrap splice. Card-76 is NOT the wall for the basic value-commit.

**Remaining for the product (Fork 2 = de-novo arbitrary value):**
- Confirm reproducibility — DONE: a 2nd independent run (fresh client) reproduced committed=true with
  PF_EDIT_STRING=QAGENUINE2026, default absent.
- **Value-retarget — DONE (Fork 2 proven):** `native_samesession_commit_probe.py --retarget ZZZRETARGET99`
  substituted the captured value → an arbitrary NEW value (same length, both UTF-8 + UTF-16LE) in every
  replayed frame; the read-back shows `PF_EDIT_STRING=ZZZRETARGET99` (new value committed), with both the
  captured value AND the default ABSENT. So qa_mcp writes an ARBITRARY value, not just a replay. Remaining:
  VARIABLE-length values (length-prefix + frame-length fixups — currently same-length only).
- Fold the working path into qa_mcp's manager (a `write_form_value` built on full-session-replay + retarget).
- Fix the `extract_edit_field_value` parser for the `\xfa`/`\xe0` value-tail variant.

## Acceptance
- A NEW value is written through qa_mcp (no Vanessa) and a subsequent value-read confirms the field
  now holds the new value (not the default) — `effect_verified=true` for a WRITE, on a live TestClient.
- Or: a recorded determination that the input-commit token is not reproducible without the genuine
  manager input API, with the minimal manager-side shim that emits it documented.

## Related
- card 79 (native value-read effect verification; Fork 1 shipped)
- card 76 (raw-API session-ID synthesis — manager-originated GUIDs unlearnable)
- card 77 (agent_runtime parity — `ТестируемоеПриложение` input API surface)
- `tools/protocol-research/native_effect_probe.py` (`--lead-in`), `analyze_input_editmode.py`

## UPDATE (2026-06-16) — Linux genuine-capture UNBLOCKED + genuine input observed (edit-text, not value)
The "First step (gated) ... blocked on capture tooling" is now UNBLOCKED: the genuine Vanessa TestManager
runs on Linux and drives a connected TestClient (card 81 M2 RESOLVED), so genuine inputs can be captured
here without Windows. Evidence: `docs/protocol-research/evidence/vanessa-mcp-linux-genuine-manager-2026-06-16/`.

- Drove the genuine manager (Vanessa runMcp on :9874) to connect a thin client on `vanessa_client`, open
  the EXACT fixture `DataProcessor.ФикстураПротоколаTestClient` (form "QA MCP Protocol Fixture V1"), and run
  `И в поле с именем 'PF_EDIT_STRING' я ввожу текст "QAGENUINE2026"`. Captured the native manager↔client
  frames passively with `tcpdump -i lo` (Vanessa picks its own client `-TPort`, observed 48000-48210 across
  sessions; capture spanned 48000-48300). The typed value IS on the wire:
  `genuine-input-commit.pcap` (1.9 MB) has **8 ASCII + 2768 UTF-16LE** occurrences of `QAGENUINE2026`.
- **KEY OBSERVATION (reinforces the off-wire conclusion).** After the input step, `get_form_analysis` shows
  `PF_EDIT_STRING` VALUE = `PF_EDIT_STRING_VALUE` (baseline, NOT committed) while its «текст редактирования»
  (edit-text) = `QAGENUINE2026`. So even the GENUINE manager's `ввожу текст` (via the real
  `ТестируемоеПриложение` API, runMcp mode) leaves the typed value in the client-side edit buffer without
  committing it to the field VALUE — a separate commit trigger is required. Vanessa's own commit path raised
  `Отсутствует редактор Vanessa Automation Editor` (the editor-assisted commit needs the editor UI, absent in
  runMcp). This is the same edit-text-vs-value split as the card-79 read path (value_mode vs edit_field).
- **NEXT (now genuinely actionable):** capture a genuine COMMITTED input — trigger the commit without the
  Vanessa editor (focus-loss via raw xdotool click on another field / Tab / a fixture button; or a non-editor
  Vanessa step), confirm `PF_EDIT_STRING` VALUE flips to the typed value, and diff the genuine commit frames
  vs our synthesized SET (`analyze_input_commit_token.py`) to settle Fork 2 vs Fork 3. A pcap→`traffic.jsonl`
  converter (or re-capture via `protocol_proxy.py` attach-running) feeds the existing analyzers.

## COMMIT ACHIEVED + CAPTURED (2026-06-16) — the commit trigger is the FOCUS-CHANGE, not the SET frame
Drove a genuine COMMITTED input on the fixture and verified the effect by read-back. The commit trigger was
isolated empirically. Evidence screenshot 08 (PF_EDIT_STRING shows "QAGENUINE2026" in the field).

- **How:** one Gherkin feature, two inputs on the open fixture form, NO connect/open noise:
  `И в поле с именем 'PF_EDIT_STRING' я ввожу текст "QAGENUINE2026"` then
  `И в поле с именем 'PF_EDIT_NUMBER' я ввожу текст "777,77"`. Both steps Success, no editor error.
- **Effect verified (read-back):** `PF_EDIT_STRING` VALUE = **"QAGENUINE2026"** (was baseline
  "PF_EDIT_STRING_VALUE"); `PF_LAST_ACTION` = **"PF_EDIT_STRING"** and `PF_MUTATION_POST_STATE` =
  "PF_EDIT_STRING_POST" → the field's server-side `ПриИзменении` handler FIRED. Meanwhile `PF_EDIT_NUMBER`
  VALUE stayed "120,5" with edit-text "777,77" (uncommitted — no following field to trigger ITS commit).
- **MECHANISM (the card-80 answer):** the value-commit is realized by the **focus-change** off the edit
  field (which makes the client send the new value → server runs `ПриИзменении` → VALUE updates), NOT by the
  SET/edit-text frame alone. The first field committed only because the SECOND input moved focus off it; the
  second never committed (nothing moved focus off it). This is the same edit-text↔value split as card 79's
  read path. Our prior synthesized replay sent the SET (edit-text) but never the focus-change/`ПриИзменении`
  round-trip → no commit. Vanessa's own commit helper raised "Отсутствует редактор" (needs the editor UI,
  absent in runMcp) — the NATIVE 1C focus-change commit, however, does not need it.
- **Capture:** `runtime/protocol-research/captures/genuine-vanessa-write/commit-capture.pcap` (624 KB) holds
  the genuine SET+COMMIT frames — `QAGENUINE2026` present 7× ASCII / 325× UTF-16LE.
- **Reconciliation with the off-wire conclusion:** the commit IS driven by on-wire focus-change frames, but
  whether they are REPLAYABLE (Fork 2) or carry session-specific manager state (Fork 3) is now settle-able by
  diffing `commit-capture.pcap`'s focus-change/`ПриИзменении` round-trip against our synthesized SET — the
  earlier same-session replay likely replayed only the SET, never the focus-change commit. THIS is the next
  analytical step (pcap→jsonl or re-capture via proxy, then `analyze_input_commit_token.py`).

## Log
- 2026-06-15: card created (spin-off from card 79 forks 2/3).
- 2026-06-16: Linux genuine-capture pipeline built (card 81 M2) and used to capture a genuine PF_EDIT_STRING
  input ("QAGENUINE2026" present on the wire: 8 ASCII / 2768 UTF-16LE hits). Confirmed the genuine input sets
  edit-text but NOT the field VALUE without a separate commit trigger (Vanessa's commit needs the editor, which
  runMcp lacks) — consistent with the off-wire-gate conclusion. Capture: `runtime/protocol-research/captures/
  genuine-vanessa-write/genuine-input-commit*.pcap`. NEXT: capture a committed input + diff vs synthesized.
- 2026-06-16: **COMMIT ACHIEVED + isolated the trigger.** Two-input feature (PF_EDIT_STRING then
  PF_EDIT_NUMBER) → the focus change off PF_EDIT_STRING COMMITTED it: read-back shows VALUE="QAGENUINE2026",
  PF_LAST_ACTION="PF_EDIT_STRING" (server ПриИзменении fired), PF_MUTATION_POST_STATE="PF_EDIT_STRING_POST";
  PF_EDIT_NUMBER stayed uncommitted (no following focus change). ⇒ the value-commit trigger is the
  FOCUS-CHANGE/ПриИзменении round-trip, NOT the SET frame — our replay sent SET only. Genuine SET+COMMIT
  captured: `commit-capture.pcap` (624KB, QAGENUINE2026 7×ASCII/325×UTF-16LE). Evidence screenshot 08. NEXT:
  diff the focus-change/ПриИзменении frames vs synthesized SET to settle Fork 2 (replayable) vs Fork 3.
- 2026-06-16: **Live Fork-2 attempt #1 — NOT green yet; the SET-replay wall (card-79) is deeper than the
  missing focus-change.** Built the probe infra (`native_effect_probe.py --commit-frames`) + a Linux runner
  (`run_fork2_commit_test.sh`: boots a TestClient on vanessa_client under Xvfb, runs the probe, restores
  apache). Ran SET (fixture-input-capture 280-283) + commit-frames 471-474: all frames ACKed
  (`action_accepted/commit_accepted=true`) but `effect_verified=false`, read-after still default, no marker
  echo. Diagnosis: (1) fixture-input-capture 471-474 are a SECOND value-READ pass, NOT a real user
  focus-change (the genuine focus-change lives in `genuine-commit-converted` mgr[357-360]); (2) the older
  capture's SET frame replays as ACK-without-effect (matches card-79's "SET ACKed, value not realized"),
  so the edit-mode SET itself, not just the focus-change, must come from the genuine commit capture. The
  frame-diff "no off-wire token in the bytes" still holds, but live replay shows the SET application also
  depends on client edit-mode/session state the old capture's replay doesn't reproduce. NEXT: replay
  `genuine-commit-converted`'s edit-mode SET (354) + focus-change (357-360) — locate its form-open frames
  or splice via a `--commit-capture`/`--input-capture` second-source rebind; or synthesize the edit-mode SET.
- 2026-06-16: **FRAME-DIFF done — note SUPERSEDED by the live test below: read as "no CLIENT token", NOT
  "replayable".** Built `pcap_to_traffic.py` (pcap→proxy capture format) → `genuine-commit-converted/`
  (664+615 chunks). Ran `analyze_input_commit_token.py`: BOTH the SET (mgr[354]) and the focus-change
  (mgr[359]) report MYSTERY echoes=0 (only rebindable GUIDs + ASCII markers). The commit is the SEQUENCE
  SET→focus-change. [At the time I read this as "Fork 2 feasible"; the live replay below disproves that —
  no-CLIENT-token ≠ replayable, the gate is manager-side.]
- 2026-06-16: **Live Fork-2 attempt #2 → off-wire CONFIRMED, Fork 2 RULED OUT.** Replayed the GENUINE
  committing frames (`genuine-commit-converted` SET 354 + focus-change 357-360, mfg/sfg-rebound) against a
  live client via qa_mcp → still `effect_verified=false`, no marker echo. Decisive: the SAME mfg/sfg rebind
  makes the value-READ work live (card 79), so the rebind is adequate; yet the value-commit with the genuine
  frames + focus-change still doesn't commit ⇒ gated on manager-side state, not the wire. Fork 3 (re-implement
  the manager input path) is required; Fork 1 stays the practical bar. See the "LIVE FORK-2 REPLAY" section.
- 2026-06-16: **⭐ BREAKTHROUGH — full-session replay COMMITS the value; the "off-wire wall" was wrong.**
  Faithful replay of the GENUINE input session's whole frame stream (genuine-commit-conn 0→554, live GUID
  rebind) on a fresh TestClient: set_response echoes the input AND the post-input read returns
  PF_EDIT_STRING=QAGENUINE2026 (committed, default absent), committed=true. Root cause of all prior failures:
  the bootstrap was from a Vanessa READ-ONLY capture (tm-v1 `manager-fixture-v1-readonly`) → never
  input-authorized → spliced input never applied. Fixed 3 tooling bugs (pcap connection-mixing; probe
  break-on-empty; probe break-on-control-frame-run). ⇒ Fork 2 (replay/synthesis) is ACHIEVABLE; card-76 is
  not the wall for the basic commit. NEXT: confirm reproducibility + retarget the value to an arbitrary new
  one. See the "BREAKTHROUGH" section.
- 2026-06-16: **✅ Fork 2 PROVEN end-to-end — ACCEPTANCE MET.** (1) Confirmed the commit-via-full-replay on a
  2nd fresh-client run (committed=true, PF_EDIT_STRING=QAGENUINE2026). (2) `--retarget ZZZRETARGET99` wrote an
  ARBITRARY new value (not in the capture): read-back = `ZZZRETARGET99`, captured value + default both absent,
  committed=true. ⇒ qa_mcp writes+commits a NEW value with no Vanessa, verified by read-back on a live
  TestClient — card-80 acceptance #1 met (research-level). Remaining = engineering: variable-length values,
  generalize beyond the fixture (input-capture template per target), fold into a qa_mcp `write_form_value`.
- 2026-06-16: **PRODUCTIZED — `qa_mcp.protocol.native_write.write_form_value` + variable-length.** New src
  module: `WriteTemplate` (describes a genuine INPUT capture) + `write_form_value(template, new_value, host,
  port)` (full-session replay + GUID rebind + value retarget + read-back verify) + `retarget_value`
  (FIXED-WIDTH-aware: keeps the frame size constant by growing/shrinking the trailing space padding, prefix
  via LEB128) + `read_field_value_near` (length-aware value parser, supersedes the `\x14`-only
  extract_edit_field_value gap). 8 offline unit tests pass (`tests/test_native_write.py`). CLI
  `native_write_probe.py`, runner `run_write_test.sh`. Live (fresh client per write): AB (2 chars) and
  RETARGETED99X (13) COMMIT (`committed=true`, read-back matches); over-length (16 > the field's declared
  length ~13) is cleanly REJECTED by the client (set not echoed, default unchanged, frame size constant so no
  desync) — correct 1C semantics, not a bug. KNOWN LIMITATIONS (refinements): (a) multi-write on ONE client —
  only the FIRST commits (the form holds the prior value, the next replay desyncs); each write needs a fresh
  form/client, or a reset step; (b) tied to the fixture capture template — generalizing needs an INPUT capture
  per target field; (c) value bound = the field's declared length (a metadata lookup could validate up-front).
- 2026-06-16: **MULTI-WRITE FIXED — `NativeWriteSession` (open-once, write-many).** Root cause of limit (a):
  the form PERSISTS open across connections, so a per-write full replay RE-OPENS it and the downstream read
  desyncs (the SET still echoed, but the readback came back malformed/empty). Fix = the correct product
  shape: replay the setup prefix `[0..setup_end]` (handshake+open+activate) ONCE on a persistent connection,
  then each `write` re-sends the write block `[activate..SET..focus-change]` + read with the binary message
  counter (offset 19-20 LE) BUMPED (`_set_seq`) so the client never sees a backwards sequence. Live: 3
  sequential writes of varying length (12, 2, 13 chars) on ONE connection ALL committed (readback matches
  each). 8 unit tests still pass. Tools: `NativeWriteSession`, `native_write_session_probe.py`,
  `run_writesession_test.sh`. Limit (a) RESOLVED; (b)/(c) remain (→ step 2 generalize).
- 2026-06-16: **GENERALIZED — `derive_write_template` (no hard-coded ordinals).** Auto-derives the template
  from ANY genuine INPUT capture: locates the SET frame (carries the length-prefixed captured value), the
  field's activate prefix (contiguous `EditField[field]` before the SET), the focus-change (first frames
  after the SET touching a DIFFERENT `EditField`), and the read-back frames (`EditField[field]` after the
  focus-change). On the fixture it derives setup_end=347, write_block=(348,356), read_frames=[549,550]
  (matches the hand-tuned values, tighter block). Both probes now use it; live multi-write via the
  AUTO-DERIVED template committed 3/3. Offline unit test on a synthetic capture (`test_derive_write_template
  _locates_block`); 9 unit tests pass. Limit (b) RESOLVED at the MECHANISM level — applying to a NEW field
  still needs a genuine INPUT capture OF that field (the derivation then works on it), and the value bound is
  the field's declared length (c). card-80 acceptance MET; the write path is productized in qa_mcp.
- 2026-06-16: **Fork 3 started — step 1 (diff two genuine SETs) DONE.** Extracted session B from
  `genuine-input-commit.pcap` (port 48002) and diffed its PF_EDIT_STRING SET vs session A
  (`genuine-commit-converted` mgr[354]). After mfg+sfg+ack rebind the only residual diffs are the
  card-80 harmless offset-~70 nonce (16 B) + a 2-B ack-tail fragment ⇒ independently confirms NO wire token
  gates the commit. Re-scopes Fork 3: the gate is the CLIENT edit-session STATE (read→activate→set→
  focus-change consistency); the live replays failed from MIXED captures (tm-v1 open + genuine SET). Routes:
  (a) consistent single-session replay (genuine open+set+commit, rebound — gated on card-76 bootstrap
  context); (b) re-implement the edit-mode handshake in qa_mcp. NEXT: locate genuine-commit's open ordinals,
  try route (a) as the cheapest client-state test. See "FORK 3 — step 1" section.
- 2026-06-16: **Fork 3 — step 2: frame-based Fork 3 EXHAUSTED.** The offset 19-20 binary counter is
  consecutive (`frame4_sequence + delta`); genuine input frames carry a lower (backwards) counter. Added
  `native_effect_probe.py --reseq` to continue the live counter; iteration #3 (genuine frames + reseq) still
  `effect_verified=false`. Since two genuine SETs are byte-identical after mfg/sfg/ack rebind (only nonce+seq
  differ, both now handled) yet replay won't commit, NO frame field gates the commit — it is the client
  edit-session STATE from the manager's live interaction (card-76 wall). Recommendation: Fork 1 (shipped) as
  the input bar + the genuine Vanessa manager (card 81, proven) as the value-WRITE backend (hybrid). Pure
  native qa_mcp value-commit is not achievable by replay/synthesis. See "FORK 3 — step 2" section.
</content>
