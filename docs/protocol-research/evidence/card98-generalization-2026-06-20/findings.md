# Card 98 change-1 generalization — introspect ANY form: path mapped, blocker characterized

**Date:** 2026-06-20. **Result:** `read_form_descriptor` already generalizes under the epic's **one-time per-form
capture** model (its `capture_dir` param). Generalizing to **any form with NO capture** (live element
enumeration) is precisely characterized: the element tree is a single descriptor re-render frame, but replaying
the descriptor sequence needs full dynamic-field modeling the template tooling doesn't yet do — a focused
reverse-engineering follow-up, not a quick win.

## read_form_descriptor already generalizes (one-time-capture model)

The tool takes `capture_dir`; `_enumerate_capture_fields` reads the field list (names + Group chains) from THAT
capture's query paths, then loop-reads each live. So introspecting a DIFFERENT form is "capture-free after a
ONE-TIME per-form capture" — exactly the epic's model for actions (read is universally capture-free; the per-form
field list is the one-time cost). Point `read_form_descriptor(capture_dir="<other-form-capture>")` at another
form's value-read capture and it introspects that form.

## Generalizing to NO capture (live enumeration) — the path + the blocker

Goal: enumerate the live form's elements without any per-form capture, so introspection needs zero setup.

1. **The form OPEN does not enumerate** — `handle.form_summary()` returns **0 elements** live; the open frames
   (1-17) carry only the root SecondaryFrame/ManagedForm, not the element tree.
2. **The element tree is one descriptor re-render** — pairing each genuine manager send with its response,
   exactly ONE response (manager send ~40) enumerates **45 distinct element names**; every other send ≤4. So the
   "get form analysis" enumeration is a single descriptor re-render in the genuine sweep.
3. **Single-frame raw replay → ACK only** — sending the captured enumeration frame (frames 38-41) GUID-rebound
   via `run_action` on the open session returns a 481-byte ACK with **0 element names**: the enumeration is a
   STATEFUL descriptor sequence (it depends on the preceding descriptor frames + the live seq counter), not a
   single replayable frame.
4. **Template replay of the descriptor sequence DESYNCS** — generated a `tm-v1-form-analysis` template
   (`extract_manager_templates.py --frames 8-41,218-221`) to render frames 18-40 with seq/GUID injection, but:
   (a) the generator's dynamic-field model is **bootstrap-specific** — it adds a `nonce`@68 to every frame ≥6,
   which is out-of-range on the shorter descriptor frames (`Template field out of range`); (b) after patching out
   the spurious nonces, the send **broke the pipe** — the descriptor frames carry dynamic content beyond
   seq/GUID/nonce (per-element refs, etc.) that, replayed as captured, the client rejects.

**⇒ Blocker (precise):** live enumeration needs the descriptor re-render frames' dynamic fields fully MODELED
(the template tooling models only the bootstrap/open/value-read frames). The descriptor frames are materially
more complex; modeling them (or synthesizing the enumeration query) is the focused next step to drop the
one-time-capture cost. Until then, `read_form_descriptor` generalizes per the one-time-capture model.

## Also open: Cyrillic-named fields

`_enumerate_capture_fields` matches ASCII query paths only, so the 2 Cyrillic reference fields (Контрагент,
ПолеСоСпискомВыбораСтрока) aren't queried live (the offline `extract_form_field_values` already decodes UTF-16
leaves). Reading them needs UTF-16 query-path retargeting (`_retarget_read_to_groups` builds latin1 paths) — a
bounded refinement, separate from the live-enumeration gate.

## Artifacts

- Probes (investigation): `tools/protocol-research/form_summary_enum_probe.py` (open enumerates 0),
  `form_enum_replay_probe.py` (single-frame ACK), `form_enum_template_probe.py` (template-sequence desync).
  Template gen: `extract_manager_templates.py … --frames 8-41,218-221` (runtime/, regenerated). No production
  code changed — generalization is characterized, not yet built; `read_form_descriptor` ships as-is
  (one-time-capture model).
