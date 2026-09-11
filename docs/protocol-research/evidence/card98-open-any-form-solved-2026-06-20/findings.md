# Card 98 change-1 — open-any-form wrapper SOLVED: introspect ANY form by nav-link, no per-form capture

**Date:** 2026-06-20. **Result:** the open-any-form wrapper is **built and live-verified**. The last blocker —
the navigated form's **ManagedForm F** — is solved by a decoded **"resolve form" query**. `read_form_descriptor(
open_link="e1cib/list/Справочник.Контрагенты")` opens a DIFFERENT form by nav-link and returns its full
**79-element tree** with NO per-form capture. This closes the change-1 generalization end-to-end. 45 MCP tools,
323 tests.

## The missing F — the "resolve form" query

The navigated form's window gives only its SecondaryFrame (S); the descriptor query needs `SecondaryFrame[S].
ManagedForm[F]`. Decoded from `genuine-card98-formanalysis` (the sweep's FIRST query, mgr#2): a **resolve query**
— body ``<nonce> 9a 34 SecondaryFrame[S]`` (S-only) + opcode ``88 81 81 e1 81 81 81 81 81 81 81`` (note ``e1 81``,
distinct from the descriptor's ``e1 82``). Its response returns the form's full ``SecondaryFrame[S].ManagedForm[F]``
— the F. `native_write.splice_resolve_form_query` builds it (graft onto a live header); the response is searched
for the TARGET's S (not the first match — the response can carry several forms' refs).

## The wrapper (`read_form_descriptor(open_link=…)`)

`_open_form_by_link(handle, nav_link)`:

1. **Navigate** — `splice_navigate` grafts the genuine open-list navigate command (a **2-frame** request, opcodes
   ``88 82 81`` then ``81 81 81``; one frame alone opens nothing) onto a live header with the nav-link retargeted
   (UTF-16, char-count recomputed). Opens the form as a new tab (the desktop MainFrame source GUID is
   session-stable, no retarget). Live-proven: Контрагенты opens (screenshot + window-list).
2. **Window-list** — `get_window_list_testclient` → the new window's SecondaryFrame (matched by caption).
3. **Resolve** — `splice_resolve_form_query(S)` → the form's S.F (the **F**).
4. **Descriptor** — `splice_descriptor_query(S, F)` (explicit S.F — NOT the rendered frame's, which the value-read
   response observation resets to the fixture) → the navigated form's element-tree descriptor.
5. **Parse** — `responses.extract_descriptor_elements` → the full element tree (every ``<Kind>[name]`` —
   EditField / Button / Table / Group / Page / Decoration / …, ASCII + UTF-16LE).

## Live verification

`read_form_descriptor(open_link="e1cib/list/Справочник.Контрагенты")` (fresh /TESTCLIENT,
`read_form_descriptor_openlink_verify.py`):

```
opened form: 'Контрагенты'
enumerated: 79 elements
  Group[ФормаКоманднаяПанель] · Group[Настройки] · Table[Список]  (the dynamic list)
  Button[ФормаСоздать] · Button[ФормаИзменить] · Button[ФормаУдалить] · Button[ФформаОбновить] · …
  Group[ФормаРежимПросмотра] · Button[ФормаПеренестиЭлемент] · …
```

A DIFFERENT form than the captured fixture, introspected with **no per-form capture** — its real structure
(dynlist Table + command buttons + view-mode group). The earlier wrong-form bug (fixture's 46 returned) was the
resolve picking the first S.F in the response, not the target's — fixed by matching the target's SecondaryFrame.

## Scope / honest

- **Structure** (the element tree / `ui_read_tree` surface) of ANY form, capture-free — DONE.
- **Values** of a navigated form's fields are NOT read here (the value-read template renders the fixture's region;
  retargeting the value-read S.F to the navigated form is a follow-up). The OPEN form (no `open_link`) reads
  values via `enumerate_live`.
- The window match is by caption (works for catalog lists/forms whose caption = the catalog name); a
  newest-window diff would generalize custom-caption forms.

## Artifacts

- Code: `src/qa_mcp/protocol/native_write.py` (`splice_navigate`, `splice_resolve_form_query`,
  `RESOLVE_QUERY_*`, `NAVIGATE_BODY`), `src/qa_mcp/protocol/responses.py` (`extract_descriptor_elements`),
  `src/qa_mcp/mcp_server.py` (`_open_form_by_link`, `_live_descriptor_blob`, `read_form_descriptor(open_link=…)`).
  Tests: `tests/test_form_descriptor.py` (+4). **323 tests.** Probes: `open_any_form_probe.py` (the chain),
  `read_form_descriptor_openlink_verify.py` (the tool — 79 elements). Capture: `genuine-card98-formanalysis`.
