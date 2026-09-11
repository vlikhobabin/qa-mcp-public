# Card 98 / change 5 (the 🚩 GATE) — 2nd-config validation: WRITE path (read DONE; UTF-16 fix DONE; commit gap found)

**Date:** 2026-06-18. **Card:** 98 change 5 (= old card 94) — validate capture-free synthesis on a 2nd (real,
non-fixture) config; the lab-demo→product boundary, the gate on the "100% test-manager replacement" claim.
**Status:** READ generalizes universally (2 configs). The write deriver was ASCII-only — **FIXED** (UTF-16LE
element paths). On a foreign config the write engine establishes + the field ACCEPTS an arbitrary value
(edit-text echo), but full COMMIT-persistence is **NOT yet reproduced** — the precisely-localized remaining gap.

## What was tested (this session)

Two real, non-fixture configs under the genuine Vanessa manager (Xvfb :77) + native replay clients:
- **`redacted-third-party-config`** (`${QA_MCP_PRIVATE_CORPUS_ROOT}/infobases/dev`, 4.8 GB) — a large real **1С:Бухгалтерия 3.0
  / [redacted third-party configuration]** config; user `[redacted 1C user]`, empty pw. The structurally-different "big config".
- **`demo_1_0_41_3`** (`/opt/1c-dev/demo_1_0_41_3`, 246 MB) — the 1С:БСП demo; user `Администратор`, empty pw.

## ✅ READ generalizes universally (no per-config capture)

`read_active_window` (vanessa_client read-only bootstrap `tm-v1-ro-batchQ3` + GuidRebinder) established a
session and read the active window against **both** foreign configs — `evidence_status=accepted`, no
config-specific capture. (demo proven 2026-06-18 earlier; **third-party-config added this session**:
`IB=…/redacted-third-party-config/infobases/dev NUSER="[redacted 1C user]" run_second_config_read_test.sh` →
`READ ESTABLISHED`.) The read path is the **universally** capture-free exception.

## ✅ The engine generalization FIX — UTF-16LE element paths (the headline)

The genuine third-party-config write capture (`Справочник.Валюты` field `НаименованиеПолное`) revealed that the
write-path machinery was **ASCII-only**: `_EDITFIELD_RE` / `read_field_value_near` matched `EditField[<name>]`
as **1-byte ASCII**. That is how the wire encodes an **ASCII** field name (`EditField[PF_EDIT_STRING]` — the
fixture), but a **non-ASCII (Cyrillic)** name is encoded **UTF-16LE** (`E\x00d\x00i\x00t\x00F\x00i\x00e\x00l\x00d\x00[\x00<cyrillic-utf16>]`).
So on ANY real (Russian-named) config the deriver found **zero** fields — a silent lab→product wall.

**Fix** (`src/qa_mcp/protocol/native_write.py`): new `editfields_in(frame)` decodes BOTH the ASCII and the
UTF-16LE element path (returns field NAMES as `str`); `derive_write_template` now matches by str name;
`read_field_value_near` tries the ASCII value-mode anchor (unchanged for the fixture) then the UTF-16LE leaf.
Verified: `derive_write_template` now resolves SET / activate / focus-change / read-back on the real
`Валюты` forms of **both** third-party-config and demo; **42 unit tests pass** (39 prior + 3 new UTF-16 tests);
the fixture still commits live (`committed: true`, control run — no regression).

## ⚠️ WRITE on a foreign config — engine + value-acceptance generalize; COMMIT does not yet

Genuine write captured on each config (open `e1cib/data/Справочник.Валюты` → activate → type the target
field → type a 2nd field to commit via focus-change → read-back), then replayed capture-free with the value
RE-TARGETED to an arbitrary new string against a FRESH client:

- **demo_1_0_41_3** (clean home page): the replay **establishes cleanly** (no divergence) and the client
  **ACCEPTS the arbitrary value** into the Cyrillic field `Наименование` — the SET response echoes
  `ZZGATEOK26` (`set_response_echoes_new=True`). **But the read-back shows the field EMPTY** (value-mode
  `…81 81 81 e1 20 a1` = a single space): the edit-text was set but **not committed to the attribute** — the
  replayed focus-change does not fire the platform `ПриИзменении` commit. Same result via the standalone
  `write_form_value` AND the shipped `NativeWriteSession`, and with the GENUINE value (no retarget) — so it is
  **replay-fidelity, not a retarget bug**. Control: the **fixture commits** under the identical mechanism →
  the gap is **config-specific** (a real grouped, multi-window form), not a code regression.
- **redacted-third-party-config** (busy 7-window home page: visa-workstation dashboard + 3 popups + app windows): the
  full-stream replay **crashes the client** (the manager returns a libc/`core83` backtrace error frame). The
  window-GUID rebinding desyncs against the non-deterministic auto-opening home page. So third-party-config write is
  blocked one step earlier than demo.

⇒ **Localized remaining gap:** the focus-change **commit fidelity** of the full-stream replay on real forms.
`write_form_value` opens the session, addresses the field by name (incl. Cyrillic now), and sets the value —
but does not yet make it *stick* on a foreign grouped form. This is the honest blocker to the "100% test-
manager replacement" claim for the WRITE surface; READ is unaffected.

## Generality matrix (updated)

| capability | status | evidence |
| --- | --- | --- |
| bootstrap / handshake | ✅ generalizes (infobase-portable) | established vs third-party-config + demo_1_0_41_3 |
| read path (active window / form / value / element) | ✅ generalizes, NO capture | read both foreign configs' real windows |
| element addressing by NAME — ASCII | ✅ | fixture |
| element addressing by NAME — Cyrillic / UTF-16LE | ✅ **fixed this session** | `editfields_in`/`read_field_value_near`; derive works on both real `Валюты` forms; 42 tests |
| write: session establish + value ACCEPTED (edit-text) on a foreign config | ✅ (after one-time per-flow capture) | demo: `set_response_echoes_new=True` with an arbitrary value |
| write: full COMMIT-persistence on a foreign grouped form | ⚠️ NOT yet | demo: edit-text set, read-back empty; fixture commits (control) ⇒ config-specific focus-change fidelity gap |
| write replay on a busy-home-page config | ❌ replay crashes client | third-party-config: GUID-rebind desync on the 7-window home page |

## Per-config onboarding recipe (current honest claim)

- **Read** against a new config: works immediately, **no capture** (proven on 2 configs).
- **Write/actions**: the engine is config-agnostic and now Cyrillic-name-aware; a one-time per-flow genuine
  capture on the target form is the onboarding cost (recipe `[[genuine-action-capture-recipe]]`). The value is
  accepted by name — **but COMMIT-persistence is not yet reliable on real forms** (focus-change fidelity), and
  configs with a busy auto-opening home page crash the full-stream replay. So the honest claim today is:
  **"read is universally capture-free; write establishes + sets the value by name on a foreign config after a
  one-time capture, but committing the value reliably on real forms is an open item."** NOT "write generalizes".

## Blocker #1 — root cause FOUND (2026-06-18, deep dive): form-attribute vs object-attribute fields

Instrumented frame-by-frame replay (genuine value, no retarget) showed the demo replay is **byte-identical to
the genuine capture through the SET + the entire focus-change** (mgr[16..24]; the SET echo at mgr[18] carries
the value in BOTH). The value is lost only at the read-back. Polling the read 6× with delays — always empty
(not a timing issue). So:

- The bare full-stream replay **reliably sets the field's EDIT-TEXT** (the SET command `e0 41 81 81 ba`
  echoes) on any field, incl. Cyrillic (UTF-16 fix).
- **The fixture commits because `PF_EDIT_STRING` is a FORM ATTRIBUTE with an `OnChange` handler** — the SET
  updates the form attribute directly and the read-back reads it. (Confirmed: `PF_EDIT_STRING` has
  `OnChange`/`PF_EDIT_STRING_OnChange` → `PFV3_RegisterLocalMutation`, all `&НаКлиенте`.)
- **Demo `Валюты.Наименование` is an OBJECT ATTRIBUTE (`Объект.Наименование`) and the form has NO `OnChange`
  on any field** (verified in the vanessa_client `Валюты` element form — zero `OnChange` handlers). The SET
  sets the edit-text, but committing it to the object attribute is a CLIENT-SIDE "user edited → commit on
  blur/save" step that the replayed command frames do NOT trigger on a fresh session.
- **`Записать` (save) does not rescue it on replay either** — DECISIVE DB check: after the save-replay
  (retarget → `ZZGATEOK26`), the demo `Валюты` list contains `QADEMO2026` (×2, from the GENUINE save runs)
  but **NOT `ZZGATEOK26`**. So the replayed save did not persist the retargeted value; the object-attribute
  commit never happened.

⇒ **Root cause:** `write_form_value`'s full-stream replay commits values into **form-attribute** fields (like
the fixture's `PF_*`) but **not object-attribute fields** (`Объект.*` on real catalog/document forms). The
missing piece is the client-side edit-text→object-binding commit (the "field was user-edited" state), which a
real Vanessa keystroke sets but the programmatic SET command does not reproduce on a bare replay. Most real
business forms are object forms, so **write-commit does not yet generalize to them** — the honest bound on the
"100% test-manager replacement" claim for WRITE. (READ is unaffected and fully generalizes.)

**Candidate fixes (each a new research effort):** (a) replay actual KEY-PRESS input (card 96 change 4,
keyboard — keystrokes mark the field user-edited → commit on blur), not the SET command; (b) decode the wire
signal a genuine client sends to commit an object attribute and synthesize it; (c) accept write as
form-attribute-only and document object-form write as out-of-scope for the replay engine.

### Fix (a) — keyboard input — ATTEMPTED + RULED OUT (2026-06-18)

Vanessa's keyboard text entry is **`Я эмулирую ввод текста` / `Эмуляция нажатия клавиши` under the `VanessaExt`
external component** — it does **OS-level input INSIDE the client** (the loaded external component drives the
focused control), NOT a TestClient protocol command. Captured `эмулирую ввод текста "qaemul2026"` into the demo
`Валюты.Наименование`: the typed value `qaemul2026` appears in **NO manager→client frame** (97 mgr chunks, zero
progressive per-char SETs, zero VanessaExt markers) — the keystrokes never ride the protocol. Also confirmed:
even the genuine emulate, with no blur after it, leaves the attribute `Наименование = ""` and only the
**edit-text** = `qaemul2026` (commit is blur-gated). ⇒ **Keyboard input cannot be replayed via the protocol
capture** (it bypasses the protocol), and the protocol-level `SetEditText` does not establish the control's
edit-mode that an object-attribute commit needs on blur. So fix (a) does not make object-attribute write commit
on a bare replay.

### Native AT-SPI introspection — TESTED + RULED OUT for elements (2026-06-18)

Could we bypass the protocol and read/drive 1C form elements natively via the Linux accessibility bus (AT-SPI)?
The 1C thin client is wxWidgets/GTK3 and **links** `libatk-1.0` + `libatk-bridge-2.0` + `libatspi` — so it
looked plausible. Tested with a control: headless Xvfb + matchbox WM + session D-Bus + `at-spi-bus-launcher` +
`at-spi2-registryd`, accessibility forced on (`GTK_MODULES=atk-bridge`, `NO_AT_BRIDGE=0`), running BOTH a
control GTK3 app and an interactive 1cv8c against demo, dumped via `pyatspi`.

- **Control GTK3 app registered fully:** `frame 'ATSPI_CONTROL_WINDOW' → [text] 'CONTROL_ENTRY'
  val='control_value_123' ifaces=[Action, EditableText, Text]` — the a11y stack + pyatspi work, and a real GTK
  field is readable AND writable (EditableText) via AT-SPI.
- **The 1C client registered ZERO accessible objects** — it created 5 real X11 windows (`xwininfo` sees them,
  title `1cv8c` / Cyrillic form titles) but exposed nothing on the a11y bus.

⇒ **1C does NOT expose its form elements via AT-SPI** (its controls are custom-drawn via `uiproxywx`/wx, not
ATK-enabled widgets; the atk-bridge/atspi linkage is transitive — webkit2gtk/GTK for web-content + system
dialogs). It is not active blocking — accessibility is simply not implemented for the custom UI. So: **window-
level introspection IS native** (X11 — useful for window management), but **element-level (fields/values by
name) is protocol-only** — which is exactly why the TestClient protocol exists. The AT-SPI shortcut (native
read, or native EditableText write that would commit like real input) is closed.
Tools: `tools/protocol-research/{atspi_dump.py,atspi_control.py,run_atspi_probe.sh}`.

**Implication for object-attribute write:** AT-SPI offers no shortcut, but the experiment confirms the X11
windows ARE OS-accessible — so the **hybrid** (protocol to find/focus the field by name + XTEST OS keystrokes
into the client window + protocol blur → commit + DB-verify) remains the viable path, and is exactly how the
VanessaExt component works (OS input on the shared display), just without Vanessa.

**Honest bottom line for the WRITE gate:** the capture-free replay engine commits values into **form-attribute**
fields (data-processor / some report-processing forms — proven on the fixture) but **NOT object-attribute fields**
on catalog/document forms (the bulk of business data entry), because that commit requires genuine client-side
edit-mode/keystrokes that the protocol does not carry. A full object-form write would need a HYBRID (protocol
replay for navigation + real OS keystrokes to the client window) — which re-introduces the OS-driving that the
capture-free engine set out to replace. READ generalizes universally and is unaffected.

## Next (to close the WRITE gate)

1. **Commit fidelity** — why the replayed focus-change sets the edit-text but does not fire the attribute
   commit on a foreign grouped form (the fixture's flat form commits). Inspect the focus-change frame's
   window/element GUID rebinding vs the SET; the SET lands (echo) but the focus-change apparently does not move
   focus. This is the single highest-value follow-up.
2. **Busy-home-page robustness** — a **block-retarget** write replay (establish via the clean read-only
   bootstrap + splice only the input command block, as `choose_from_list` does) would sidestep replaying the
   noisy home page that crashes third-party-config.

## Tools / artifacts (this session)

- Captures (gitignored, `runtime/protocol-research/captures/`): `genuine-card98-third-party-config-write`,
  `genuine-card98-demo-write`.
- Features: `tools/protocol-research/qa-{third-party-config,demo}-write.feature`, `qa-{third-party-config,demo}-connect`/`-open`.
- Probes / runners: `third-party-config_write_probe.py`, `demo_write_probe.py`, `demo_write_session_probe.py`,
  `run_third-party-config_write_test.sh`, `run_demo_write_test.sh`; read: `second_config_read_probe.py` /
  `run_second_config_read_test.sh` (now also exercised vs third-party-config).
- Engine fix + tests: `src/qa_mcp/protocol/native_write.py` (`editfields_in`, UTF-16 in `read_field_value_near`
  / `derive_write_template`); `tests/test_native_write.py` (+3 UTF-16 tests, 42 total).
