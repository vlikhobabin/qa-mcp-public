# Card 79 — native effect verification, LIVE on Linux (2026-06-15)

First live native-TestClient runtime on the migrated Linux contour, and the decisive
`--lead-in` sweep that closes card 79's queued cumulative-state experiment.

## Linux runtime milestone (read path) — PROVEN

The native 1C TestClient now boots and serves the native protocol on Linux, headless:

- **Boot:** `xvfb-run -a /opt/1cv8/x86_64/8.3.27.2130/1cv8 ENTERPRISE
  /IBConnectionString File="/opt/1c-dev/vanessa_client"; /NАдминистратор /TESTCLIENT
  -TPort 15381 /DisableStartupDialogs /DisableStartupMessages` — the thin client needs a
  DISPLAY, supplied by Xvfb. `libEGL … /dev/dri … Permission denied` warnings are benign
  (no GPU under Xvfb; software render). Process listens on `0.0.0.0:15381` (+ IPv6).
- **Read-only smoke (`native_openform_probe.py`):** synth bootstrap → open the fixture
  form (CIButton "qa mcp protocol fixture v1", frames 11-17) → value-read (218-221).
  Result: `secondary_frame_opened=true`, `value_mode_on=true`,
  `pf_edit_string_value_seen=true`, live `SecondaryFrame[030a5414]` correctly rebound from
  captured `73c822ff`. So **boot → synthesized handshake → form open → native value-READ
  all work live on Linux**, reproducing card 79's "native value-READ works" (was
  Windows-only) on Linux.

This closes the AGENTS.md "Linux native TestClient runtime is blocked" caveat **for the
read path** (open + value-read). The capture/preflight `.ps1` wrappers remain Windows; the
portable Python probe cores (`native_*_probe.py`) run under `python3 PYTHONPATH=src`
against a Linux-booted TestClient.

## The effect (input-commit) sweep — cumulative-state-prefix hypothesis REFUTED

Card 79's queued experiment: replay a wider CONTIGUOUS pre-input prefix before the commit
(`native_effect_probe.py --lead-in N` = replay `fixture-input-capture` manager frames
`[ordinal-N .. ordinal+1]`, rebound mfg+sfg → live, where ordinal=282 = the SET). All runs
against the same live Linux TestClient, fixture form re-opened fresh per run.

| lead-in | start frame | client accepts | resp has PF_INPUT_PROOF | read_after_input | verdict |
| --- | --- | --- | --- | --- | --- |
| 3   | 279 | yes | no | PF_EDIT_STRING_VALUE (default) | not committed |
| 15  | 267 | yes | no | default | not committed |
| 30  | 252 | yes | no | default | not committed |
| 60  | 222 | yes | no | default | not committed |
| 90  | 192 | yes | no | default | not committed |
| 150 | 132 | yes | no | default | not committed |
| 270 | 12  | yes | no | default | not committed |
| **275** | **7** | **yes** | **no** | **default** | **not committed** ← widest accepted prefix |
| 278 | 4  | — | — | BrokenPipe | client RESET |
| 280 | 2  | — | — | BrokenPipe | client RESET |
| 282 | 0  | — | — | BrokenPipe | client RESET |

- **Widest meaningful contiguity = start frame 7 (lead-in 275):** the entire post-handshake
  session of `fixture-input-capture` (268 frames — the value-reads at 193-196/218-221, the
  Контрагент/V4 navigation, focus, read pair, SET pair), rebound to the live open form. The
  input is replayed **verbatim** (captured value already == the marker; only GUIDs rebound).
  Still: SET accepted, no marker echoed, re-read = default. **No commit.**
- **start ≤ 6 → BrokenPipe:** action frames 0-6 are the capture's own irreducible 7-frame
  handshake; replaying them into our already-synth-bootstrapped session conflicts and the
  client resets. So start=7 is the maximum, and it is effectively full contiguity.
- Widening the prefix from 3 → 275 frames changed **nothing**. The
  cumulative-state-as-wider-contiguous-prefix hypothesis (card 79's "Next experiment") is
  **refuted live**.

## Conclusion

A pure wire-frame replay session **cannot reproduce a value-INPUT effect**, even when it
replays the input verbatim with the full contiguous post-handshake session state and the
correct live GUIDs. The SET is always ACKed but never realizes the value (the live client's
input response never carries `PF_INPUT_PROOF`; the field re-reads as the default).

This is the boundary of the write-from-capture approach for input-commit. It is consistent
with card 76 (manager-originated session identifiers that never appear in client responses
are structurally unlearnable) and card 78's honest framing (action FORMATS come from
Vanessa-driven captures): the input-commit appears gated on per-input manager-side state
(an ephemeral generation/echo token produced by the genuine `ТестируемоеПриложение` input
API), not on the wire bytes, form state, sequence, or GUIDs — none of which the replay
gets wrong.

Per card 79's own fallback, the next decision is the **acceptance bar for input/effect
verification** (see card 79 "Decision needed"). Value-READ effect verification (read a
field's live value and assert) IS proven live; only the *replay-driven write of a new
value with a verified effect* is blocked.

## Artifacts (runtime/, gitignored — regenerate or sync)

- Probe cores: `tools/protocol-research/native_openform_probe.py`,
  `tools/protocol-research/native_effect_probe.py` (`--lead-in`).
- Template (regenerate): `python tools/protocol-research/build_tm_v1_open_template.py`
  → `runtime/protocol-research/templates/tm-v1-open-plus-valueread/`.
- Captures (sync separately): `runtime/protocol-research/captures/{tm-v1-ro-batchQ3,
  fixture-input-capture}`.
- Run outputs: `runtime/protocol-research/native-openform-proof/20260615-124546/`
  (`openform_probe_result.json`, `effect-leadin-*/effect_probe_result.json`).
</content>
</invoke>
