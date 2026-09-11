# Card 98 change-5 — CONFIG-AGNOSTIC open SOLVED: introspect ANY form on ANY config, no fixture

**Date:** 2026-06-20. **Result:** the change-5 GATE is closed. `read_form_descriptor(open_link=…)` now opens +
introspects ANY form **without opening the suite fixture first**, so it works on a config that has NO fixture —
**live-proven on a SECOND, foreign config** (the БСП demo, never captured). This lifts the whole capture-free
introspection surface onto any real 1C configuration. 45 MCP tools, **325 tests**.

## The blocker (and why it was smaller than it looked)

The open-any-form wrapper (`card98-open-any-form-solved`) bootstrapped by replaying the **fixture** open frames
(11-17), because every splice (navigate / window-list / resolve / descriptor) grafts its command body onto a
**live value-read header** — and rendering a value-read frame (218) raises `ValueError: managed_form_guid_ascii
… requires a live ManagedForm GUID` unless a form is open (the fixture open sets `state.managed_form_guid`). So
introspection was tied to a config that ships the fixture.

**The key measurement:** the splice header is `rendered_frame_218[: rfind(cb-23-95) + 3]`. In frame 218 the
`cb 23 95` marker is at **offset 48**; the form-specific fields are `secondary_frame_guid` @101 and
`managed_form_guid` @151 — **both AFTER the marker**. The header [0:51] carries only `ack_guid` @2 (from the
bootstrap handshake, frame-3 client response) and `sequence` @19. So the managed_form_guid the render demands is
in the part of the frame the splice **discards**.

⇒ Render frame 218 with **placeholder** form GUIDs (`00000000-…`), slice to the marker → a splice header that is
**byte-identical** to the fixture-rendered header[0:51], with NO form open. Offline-proven identical; the only
live inputs are `ack_guid` + `sequence`, both set by bootstrap (frames 1-10).

## The config-agnostic open chain (`_open_form_by_link`, no fixture)

1. **bootstrap (frames 1-10) only** — NO fixture open (frames 11-17 skipped in the `open_link` path).
2. `_splice_header_no_form(handle)` — build the splice header from bootstrap state (placeholder form GUIDs).
3. **window-list the bare desktop** → the LIVE desktop **MainFrame** GUID (the navigate's config-agnostic source)
   + confirm NO SecondaryFrame is open (the fixture really isn't open).
4. **navigate** to the target nav-link, MainFrame retargeted to the live desktop (`splice_navigate(main_frame=…)`
   — on vanessa_client the desktop GUID is deterministic so the genuine value already matched; the retarget is
   what makes it portable to a config whose desktop GUID differs).
5. **window-list** → the navigated form's SecondaryFrame (by caption) → **resolve** (S→S.F) → **descriptor**
   (`extract_descriptor_elements` → the full element tree).

Every step rides `_splice_header_no_form`; nothing opens or addresses the fixture region.

## Live verification

**(a) vanessa_client, fixture config but fixture NOT opened** (`config_agnostic_open_probe.py`):

```
step1 bootstrap: ack_guid=5282ca11-… seq=19841 (NO fixture open)
step3 windows (bare desktop): [('HomePage','Начальная страница'), ('MainFrame','Демонстрационное приложение')]
   live desktop MainFrame = 6ca75e50-…  (== the genuine hardcoded — vanessa_client's desktop GUID is deterministic)
step5 windows after navigate: [('SecondaryFrame','Контрагенты'), ('MainFrame',…), ('HomePage',…)]
step6 DESCRIPTOR of 'Контрагенты': 37815B, 79 elements (Button×54, EditField×14, Group×10, Table×1)
PASS — form opened + introspected with NO fixture open (config-agnostic)
```

The bare-desktop window list has **no SecondaryFrame** → the splice header was built with no form open, and the
navigate opened Контрагенты from the desktop. Same 79-element tree as the fixture-bootstrapped open-any-form.

**(b) SECOND config — demo_1_0_41_3 (a real 1C:БСП base, NEVER captured)** (`config_agnostic_2nd_config_probe.py`,
the productized MCP tool against `:15382`):

```
launched demo БСП pid=… listening=True port=15382 open_link=e1cib/list/Справочник.Валюты
opened form: 'Валюты'
enumerated: 46 elements; 0 field VALUES read
elements: Group[ФормаКоманднаяПанель] · Table[Список] · Button[ФормаСоздать] · Button[ФормаНайти] · …
PASS — a DEMO (2nd-config) form opened + introspected with NO fixture, NO per-form capture
```

The **same productized `read_form_descriptor(open_link=…)`** introspected a demo form on a config with no suite
fixture and no per-form capture — bootstrap is config-portable (card 98 s3), and every splice is session-level +
MainFrame-retargeted. **This is the change-5 gate: the open surface generalizes to any real config.**

## Productization

- `src/qa_mcp/mcp_server.py`:
  - `_splice_header_no_form(handle)` — placeholder-render the value-read header, no form open.
  - `_live_descriptor_blob(handle, form_ref)` — for a navigated form (form_ref given) use the no-form header.
  - `_open_form_by_link` — window-list the bare desktop for the live MainFrame; all splices use the no-form
    header; navigate retargets MainFrame.
  - `_read_form_descriptor` — the `open_link` path SKIPS the fixture frames 11-17 (navigates from the bare
    desktop) and points the session at the navigated form's S.F (so a record form's value-read could render).
- `src/qa_mcp/protocol/native_write.py`: `splice_navigate(…, main_frame=None)` retargets the desktop MainFrame;
  `NAVIGATE_GENUINE_MAINFRAME` constant.
- Tests (+2, **325 total**): `_splice_header_no_form` byte-identity vs a real-GUID render; `splice_navigate`
  MainFrame retarget. The existing fixture/enumerate_live/open_link paths stay green.
- Probes: `config_agnostic_open_probe.py` (the chain, no fixture), `config_agnostic_2nd_config_probe.py` (demo).

## Scope / honest

- **Structure** (the element tree / `ui_read_tree` surface) of ANY form on ANY config — DONE, capture-free.
- The bootstrap capture (`tm-v1-ro-batchQ3`) is still vanessa_client-derived but is **config-portable** (proven:
  read on demo + third-party-config, and now navigate+introspect on demo). No per-config capture is needed.
- **Navigated-form VALUES** are still 0 for a LIST form (its content is the dynlist `Table[Список]` columns, not
  `Group.EditField` form-fields). The open_link path now sets the session's S.F to the navigated form so a value
  read would render against it, but reading a navigated **record** form's field VALUES is unverified end-to-end —
  it needs a record form, and on these configs records open by command/row-drill, not a bare `e1cib/list` link.
  (Follow-up: drill a list row → record, or a record nav-link, then value-read.)
- A custom-caption form would need a newest-window match (the caption match assumes caption ⊇ catalog name).

## Artifacts

- Code: `src/qa_mcp/mcp_server.py`, `src/qa_mcp/protocol/native_write.py`.
- Tests: `tests/test_form_descriptor.py` (15).
- Probes: `tools/protocol-research/config_agnostic_open_probe.py`,
  `tools/protocol-research/config_agnostic_2nd_config_probe.py`,
  `tools/protocol-research/read_form_descriptor_openlink_verify.py` (productized tool, no fixture).
