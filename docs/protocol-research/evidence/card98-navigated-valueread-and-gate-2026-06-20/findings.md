# Card 98 — navigated value-read (mechanism) + change-5 generality matrix

**Date:** 2026-06-20. Two threads: (a) extend the value-read to a NAVIGATED form (read its field VALUES, not
just structure); (b) the change-5 "2nd config" generality matrix. 45 MCP tools, 323 tests.

## (a) Navigated value-read — mechanism implemented + integrated, record-form verify pending

`_retarget_read_to_groups` gained a ``form_ref=(SecondaryFrame, ManagedForm)`` override: the value-read element
path's S.F is replaced with a navigated form's, so the read targets THAT form's field (the same explicit-S.F
trick the descriptor query uses — `splice_descriptor_query`). `read_form_descriptor(open_link=…)` now also
value-reads the navigated form's EditFields (via `extract_descriptor_fields` on its descriptor) with the resolved
``form_ref``, returning ``{opened, elements, fields, …}``.

**Live (Контрагенты):** opened='Контрагенты', **79 elements** (the full tree), **0 field VALUES** — correct: a
catalog LIST has no `Group.EditField` form-fields (its content is a dynlist Table; columns are
`Table[Список].EditField[col]`, a different read surface). The value-read integration does not crash and correctly
yields 0 for a list.

**Honest status:** the S.F-override value-read MECHANISM is implemented + integrated + regression-tested (323
tests). Reading actual VALUES off a navigated form is **not yet verified end-to-end** — it needs a navigable
RECORD/edit form (with `Group.EditField` fields). In vanessa_client the catalog list forms have 0 form-fields,
`e1cib/data/Справочник.X` nav-links did not open a matching record form, and a record card is opened by a command
(`Создать`) / row-drill, not a bare nav-link. So the value-read of a navigated form is a sound extension awaiting
a record-form fixture or the demo config (below).

## (b) Change-5 — 2nd-config generality matrix

The capture-free surface, classified for a SECOND real config (beyond the vanessa_client fixture). The
**session-level splice techniques decoded this epic are config-agnostic** (they carry no fixture-specific
element paths — only the live session GUIDs + a session-independent command body), so they generalize; the
**fixture-specific OPEN frames (11-17)** are the boundary.

| Capability | Generalizes to a 2nd config? |
| --- | --- |
| Handshake / bootstrap | ✅ infobase-portable (card 98 s3 — read on demo_1_0_41_3 + third-party-config, no config capture) |
| `read_active_window` | ✅ proven on 2 real configs (card 98 2ndconfig-read) |
| `get_window_list_testclient` | ✅ session-level command (splice onto a live header — no fixture paths) |
| Resolve query (S→S.F) / `splice_resolve_form_query` | ✅ session-level (S-only input + a session-independent body) |
| Navigate / `splice_navigate` | ✅ session-level; nav-link is the only per-form input (retargetable to any config's `e1cib/…`) |
| Descriptor query / `splice_descriptor_query` | ✅ session-level (form path = the live S.F; works on ANY open form — proven on Контрагенты, a non-fixture form) |
| `read_form_descriptor` (no `open_link`) | ⚠ bootstraps on the FIXTURE open frames (11-17) — fixture-bound |
| `read_form_descriptor(open_link=…)` | ⚠ opens the fixture FIRST (frames 11-17) then navigates — so the bootstrap is still fixture-bound; on a config with NO fixture the open fails |
| Object-attribute WRITE | ⚠ XTEST hybrid (card 98 s3, DB-verified on demo) — needs a window manager + OS input |

**The remaining boundary (the gate):** the OPEN frames (11-17) replay the genuine fixture-form open. The
session-level techniques (navigate / resolve / descriptor / window-list) all generalize, but they currently ride
on a session bootstrapped by opening the fixture. A **config-agnostic open** — bootstrap to the desktop, then
navigate to the target form by nav-link WITHOUT first opening the fixture — would lift `read_form_descriptor`
(and `open_link`) onto any config with no fixture. That, plus a record-form value-read verify, closes change 5.
Read/introspection of the desktop + any navigated form's STRUCTURE already generalize.

## Artifacts

- Code: `src/qa_mcp/mcp_server.py` (`_retarget_read_to_groups(form_ref=…)`, `read_form_descriptor(open_link=…)`
  value-read). No new tests beyond the 323 (the mechanism is the existing value-read + the override param).
  Probe: `read_form_descriptor_openlink_verify.py` (structure + values).
