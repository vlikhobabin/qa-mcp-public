# Card 80 — input-commit forensics: the write-effect gate is off-wire (2026-06-15)

Card 79 proved a value-INPUT does not commit when replayed via the synthesized bootstrap + a
cross-capture splice (open from `tm-v1-ro-batchQ3`, input from `fixture-input-capture`). Card 80 asks:
is the commit gated on a wire token we fail to rebind, or on something not on the wire at all? Two
investigations — offline forensics, then a decisive live experiment — answer: **off the wire.**

## 1. Offline — the SET request carries no unrebound wire token (hypotheses a / a' refuted)

`analyze_input_commit_token.py` + targeted byte analysis on the one genuine SET capture
(`fixture-input-capture`, SET = manager ordinal 282/283, len 287):

- The only bytes the SET shares with **preceding** client responses are the element-addressing path
  (`SecondaryFrame[…].ManagedForm[…].EditField[PF_EDIT_STRING]`) — i.e. the mfg/sfg GUIDs we **already
  rebind**. No mystery client-issued echo. (echo_token_analysis.json: `mystery_echo_count: 0`.)
- The SET header carries a 16-byte field at offset ~68 that is session-variant and NOT mfg/sfg/ack.
  But it **differs in every frame** (focus `0a102bc9…` ≠ read `754ee15d…` ≠ set `8fed9293…`) and only
  appears in the frame's **own** response (the commit echo at cli[284]), never in a *preceding*
  response — so it is a manager-generated **per-frame nonce / correlation id**, not a learnable token.
- **Proof the nonce is harmless when stale:** the value-READ frames (`tm-v1-ro-batchQ3` mgr 218-221)
  each carry the same kind of session-variant offset-68 GUID; the openform probe replays them with
  offset-68 sent **stale** (it rebinds only sfg) and the value-READ **worked live** (card 79). So the
  client does not validate offset-68 content. It is not the commit gate.

⇒ Every session-variant field in the SET is either already rebound (ack/mfg/sfg), handled (sequence),
or a harmless per-frame nonce. There is **no unrebound wire token** that gates the commit.

## 2. Live — even a faithful SAME-SESSION replay does not commit (splice / card-76-wall refuted)

The remaining suspect was the manager-originated **session identity** (card 76: such GUIDs never
appear in client responses → unlearnable) that the cross-capture splice carries stale.
`native_samesession_commit_probe.py` removes the splice: it replays `fixture-input-capture` **verbatim
in its own bootstrap** (GuidRebinder learns live client GUIDs; manager-originated handshake GUIDs are
replayed as-is, which card 76 showed the client accepts), through the SET and on to the capture's
**own** post-SET value-read (mgr 467-470, whose genuine client response cli[468] carried
`PF_INPUT_PROOF`).

Result (`samesession_commit_result.json`), live on Linux:
- `frames_sent: 473`, `diverged_at: null` — the full contiguous same-session replay ran clean; every
  frame was accepted (zero divergence).
- `set_response_has_marker: false` — the SET's own response did **not** carry `PF_INPUT_PROOF` (the
  genuine cli[283] did).
- No post-SET read (467-470) surfaced the marker; those frames returned generic 476-byte acks (the
  read context did not re-realize either). `committed: false`.

⇒ A faithful, full, contiguous, same-session, zero-divergence replay still does **not** commit. The
splice was not the blocker; the manager-session-identity wall is not the blocker.

## Conclusion — the input-commit gate is manager-side runtime state, not on the wire

No wire-frame replay reproduces the value-INPUT commit under any tested configuration:
synthesized-bootstrap + splice (card 79 `--lead-in` 3…275), and now captured-bootstrap same-session
verbatim (this card). The SET is always accepted but never realizes the value, and the offline
forensics show the SET request carries nothing session-variant that we fail to reproduce. The genuine
`ТестируемоеПриложение` input API establishes **edit-session state inside the manager process** that
the client validates the commit against; that state is built by the API calls, not serialized onto the
frames the manager sends. A replay — however faithful — cannot reproduce it.

### Forks
- **Fork 2 (de-novo synthesis by cracking a request token) — DEAD END.** There is no request token to
  crack; the SET bytes are fully accounted for.
- **Same-session capture+replay — DEAD END.** Faithful same-session replay does not commit either.
- **Fork 3 (genuine manager-side input path) — the only route.** True write-effect verification
  requires the Python manager to DRIVE the actual input mechanism (re-implement the manager half of
  the input-commit protocol that maintains edit state), not replay frames. Substantial.
- **Practical bar: Fork 1 (shipped).** Effect verification on a READ (read a field's live value and
  assert) is proven live, Vanessa-free. Actions assert "accepted". This is the recommended manager
  acceptance bar unless/until Fork 3 is undertaken.

## Artifacts
- `tools/protocol-research/analyze_input_commit_token.py` (offline echo-token analysis)
- `tools/protocol-research/native_samesession_commit_probe.py` (live same-session commit test)
- `echo_token_analysis.json`, `samesession_commit_result.json`
- Captures (gitignored, sync separately): `runtime/protocol-research/captures/fixture-input-capture`,
  `tm-v1-ro-batchQ3`. Live TestClient boot: see memory `linux-native-testclient-xvfb`.
</content>
