# Native Semantic Navigation — Command Decode + Re-targeting

Step 2 endpoint: make navigation **semantic** (decode the catalog / row / button
parameters in the command frames) so the manager can target a chosen object,
instead of opaquely replaying captured frames.

## Decode: navigation parameters live in the command frames (UTF-16LE)

Searching the captured 861-frame flow's manager command frames for the literal
navigation strings located them precisely:

| Operation | Manager frame ordinal(s) | Carrier (UTF-16LE) |
| --- | --- | --- |
| open catalog list | 8–9 | nav link `e1cib/list/Справочник.Склады` under `MainFrame[guid]` |
| select row | 15 | `…Table[…]` + column `Наименование` + value `Средний` |
| open card | 19+ | button `Изменить` |
| field reference | 241+, 272+ | `НеИспользовать` (the toggled flag) |

Frame 15 structure (the row selector), decoded:
`SecondaryFrame[g].ManagedForm[g].Table[…]` then `Наименование` then the row
value `Средний` (offset 378, UTF-16LE), then padding. So the row is selected
by **column name + value**, both carried as text.

Section navigation (`Товарные запасы`) is **not** a literal in the frames — it is
issued by command id / nav link, a separate decode if needed.

## Re-targeting capability (offline-verified)

`qa_mcp.protocol.native_mutation.retarget_row_value(manager_chunks, old, new)`
replaces the row value (UTF-16LE) in the navigation frames, requiring equal
length so the frame structure is preserved. On the real capture, retargeting
`Средний` → `Большой` (both 7 chars) changes **exactly one** frame (ordinal 15),
substitutes the value, preserves length, and leaves all other frames identical.
This is semantic control: the manager can choose which warehouse to drive.

Exposed live via `adaptive_replay_probe.py --retarget-row-file` (UTF-8 file to
avoid shell Cyrillic mojibake).

## Status

- **Decode:** solid — the navigation parameters are located and their carriers
  characterized; the row selector is a column+value text command.
- **Re-targeting:** offline-verified (single-frame, length-safe substitution),
  unit-tested.
- **Live re-targeting: CONFIRMED.** Driven via the reliable adaptive (rebound)
  replay path with the row value re-pointed to `Большой` (`retarget_substitutions=1`),
  the full 861-frame flow ran with zero divergence and the probe client responses
  carried the **`Большой (Склад)` card title 22 times and `Средний (Склад)` 0
  times**. The manager opened a **different warehouse's card** than the captured
  flow, by a single length-preserving UTF-16LE row-value substitution — semantic
  navigation control. See `native_navigation_retarget_result.json`.

## Navigation plan model (`qa_mcp.protocol.navigation`)

`extract_navigation_links(manager_chunks)` parses the flow's navigation links
(`e1cib/<kind>/<metadata>`) into a structured plan. On the real capture it
yields `frame 8: kind=list target=Справочник.Склады` — the open-list operation,
robustly decoded. `retarget_navigation_link(...)` re-points the catalog
(length-preserving), the counterpart of `native_mutation.retarget_row_value` for
the row. So the flow is now a parameterized semantic model: open-list(target) →
select-row(value) → open-card(button) → toggle/write/recover.

## First synthesized navigation command: open_list

The open-list command was fully decoded and templated. Chronologically it is one
manager frame (201 B) that says "in MainFrame open list X":

| Field | Offset | Length | Role |
| --- | ---: | ---: | --- |
| message id | 2 | 16 | per-frame |
| sequence | 19 | 2 | uint16 LE |
| nonce | 68 | 16 | per-frame |
| MainFrame GUID | 96 | 36 | live home-window id (from handshake) |
| nav path | after `e1cib/list/` | — | **semantic parameter** (which list) |

Its effect: the client creates a new `SecondaryFrame[…]` + `ManagedForm[…]` (the
list window), whose GUIDs the manager learns from the responses.

`qa_mcp.protocol.navigation.render_open_list_command(template_body, *, catalog,
main_frame_guid, message_id, sequence, nonce)` **synthesizes** this command:
- identity reproduces the captured frame byte-for-byte (verified on the real
  capture);
- re-targets the catalog (`Справочник.Склады` → `Справочник.Товары`,
  same-length) and the live MainFrame GUID.

This is the first package-**constructed** navigation command (vs replayed). It is
offline-verified and unit-tested.

## Full navigation-command synthesizer set

All three navigation commands are now decoded and synthesized in
`qa_mcp.protocol.navigation`:

| Command | Frame | Semantic param | Synthesizer |
| --- | --- | --- | --- |
| open_list | 8 | catalog (`Справочник.Склады`, ASCII MainFrame GUID) | `render_open_list_command` |
| select_row | 15 | row value (`Средний`, offset 378 UTF-16LE) | `render_select_row_command` |
| open_card | 19 | button (`Изменить`, UTF-16LE) | `render_open_card_command` |

`render_form_command` is the generic synthesizer (header fields + GUID rebind in
all encodings + same-length UTF-16LE text params). Each reproduces its captured
command byte-for-byte at identity and re-targets its parameter; all offline-
verified and unit-tested.

## Chaining driver

`native_mutation.run_replay_with_renderers(renderers={ordinal: synthesizer})`
drives the flow as **named, parameterized operations**: the open_list /
select_row / open_card frames are built by their synthesizers (live GUID rebind),
every other frame is rebound-replayed. `tools/.../native_navigation_probe.py`
wires this with `--target-file` to re-target the row.

**Live end-to-end CONFIRMED** (`native_navigation_chaining_result.json`): the
chaining driver ran 861/861 with zero divergence, **3 operation frames
synthesized by the package** (open_list, select_row→`Большой`, open_card), and
the client responses carried **`Большой (Склад)` 22 times, `Средний (Склад)` 0**
— the synthesizer-driven operation chain opened the re-targeted warehouse card.

## Frame minimization (live-validated)

The flow's frames were classified: **642 of 861 manager frames (75%) are a single
repeated managed-form state poll** (`fSecondaryFrame[…].ManagedForm[…]` + `P39w`),
in 3 busy-wait clusters (~194/221/227 frames) between operations; only 85 distinct
normalized forms exist; 219 frames are non-poll (essential candidates).

`native_mutation.poll_frame_ordinals` / `build_poll_skip_set(keep_every=N)` thin
the polls (operation frames never skipped). A live ablation
(`--keep-every-poll 4`) **sent 380 frames (skipped 481, −56%)** and still drove
the synthesized chain to the re-targeted `Большой` card with **zero divergence**
(`Большой (Склад)` 22, `Средний (Склад)` 0). The busy-wait polls are largely
redundant. See `frame_minimization_result.json`.

## Length-field decode (live-validated): arbitrary-length targets

The string length encoding was decoded: a length-prefixed value is stored as a
**1-byte char count immediately before the UTF-16LE text**, and frames are
**tail-marker delimited** (`6653b2a6`) with no frame total-length field, so a
different-length value only needs its count byte updated.
`navigation.substitute_length_prefixed_string` / `render_select_row_command`
do this. A live re-target `Средний` (7) → `Малый` (5) shortened the select_row
frame by 4 bytes and **opened the `Малый (Склад)` card** (22 vs 0), 861/861 zero
divergence — confirming no nested length fields. The same-length constraint is
lifted (`length_field_decode_result.json`).

## Minimization to the floor + from-scratch synthesis (live-validated)

- **Minimization**: `--keep-every-poll 20` sent **252 frames (-71%)** with zero
  divergence and still opened the re-targeted `Большой` card - essentially the
  essential floor (~219 non-poll + ~33 kept polls).
- **From-scratch synthesis**: `--synthesize-polls` constructed **36 frames**
  (the 3 operations + 33 kept poll frames, fresh message id + live GUID rebind)
  from templates instead of rebound-replaying them; 252 frames, zero divergence,
  reached the card. Poll frames are read-only, so a fresh message id is accepted.
  See `minimization_and_synthesis_result.json`.

## Write-synthesis gate — RESOLVED

The earlier "synthesized writes fail (uniform 665)" was diagnosed: the offset-2
16-byte field is the **per-session ack/connection GUID** (constant across
~857/861 frames, learnable as an ASCII guid), not a per-frame message id.
`render_write_frame` substituted only the SecondaryFrame/ManagedForm GUIDs and
left the ack GUID stale → the client rejected the write; regenerating offset-2
with a random uuid clobbered the rebound ack GUID the same way.

Fix: synthesize write/poll frames with `navigation.render_form_command` (global
GUID rebind in all encodings, including the binary ack GUID) + a fresh offset-68
nonce. A live run (`--synthesize-write --synthesize-polls --keep-every-poll 20`)
constructed **50 frames** (3 operations + 33 polls + 14 writes), 252 frames total,
**zero divergence and zero 665 responses**, opened the card and executed the
write. See `write_synthesis_gate_resolved.json`.

## Handshake synthesis — the irreducible replay

The 7-frame handshake is a text-record exchange: the client **assigns** the
ack/connection GUID (`77393350-...`) and the manager adopts it; the manager
**originates** 5 session GUIDs (`e23134a2`, `7f58f27d`, `ae135932`, `d450256e`,
`102301e1`) in its first frames. Regenerating those 5 fresh
(`--synthesize-handshake`) **fails**: the client rejects the session (248
uniform-665, the card never opens). Adaptive replay with the *captured* manager
GUIDs works on a fresh TestClient, so the GUIDs are validated/correlated by the
client (a challenge/response or derivation not yet decoded). See
`handshake_synthesis_finding.json`.

## Practical limit

The Python manager drives the flow as: **replay the 7-frame handshake** (captured
manager GUIDs) **+ synthesize every subsequent frame** (template + live/learned
GUID rebind + fresh nonce) **+ minimize** (252 frames, -71%). The frame structure
is the inherent protocol format (templates); the session-bound GUIDs must be the
live values; only the nonce is free. Decoding the handshake's deeper
challenge/response structure is the remaining follow-up to remove even that
7-frame replay.

Raw probe streams stay under ignored `runtime/protocol-research/captures/`.
