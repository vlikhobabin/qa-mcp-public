# Card 90 — page-field input: deploy + capture + native verify (2026-06-17)

## Summary

Inputting into a field on a **tab page** is now DONE end-to-end. The page fields were the blocker only because
they were **read-only** (not a protocol gap): `PF_PAGE_A_FIELD` / `PF_PAGE_B_FIELD` are plain `InputField`s
(textEdit) but had `<readOnly>true</readOnly>`. Once made editable + deployed, page-field input needs **no new
protocol code** — a page field is a plain `EditField` at a deeper element path, and the existing
`write_form_value` / `NativeWriteSession.write` (card 86b/c) drive it from a genuine page-field capture
(base==target → the nested path replays as-is; read-back works because a page field IS a plain value control,
unlike a table cell).

## Fixture fix (deployed)

`Forms/Форма/Form.form`: removed `<readOnly>true</readOnly>` from `PF_PAGE_A_FIELD` (id 93, dataPath
PF_EDIT_STRING, on tab page PF_PAGE_A) and `PF_PAGE_B_FIELD` (id 97, dataPath PF_EDIT_READONLY, on tab page
PF_PAGE_B). Backup `Form.form.bak-card90-pagefield`; 28 other read-only fields (incl. PF_TABLE_MARKER + the main
PF_EDIT_READONLY field) left untouched. Deployed to the live `vanessa_client` infobase via the same MANUAL
`ibcmd` export/import/apply procedure as table-cell (apache STOP, Vanessa DOWN, EDT daemon down → fresh export;
`run_dev_infobase_apply` stays structurally workspace-locked — see capture-free-epic-state.md §7 Step 1).
generation `e1496ab9…` → `3aab6541becb9543b4169d8d7855dd07…`. IB backup `1Cv8.1CD.bak-card90-pagefield-pre`.

## Live verify (Vanessa) + capture

`в поле с именем 'PF_PAGE_A_FIELD' я ввожу текст 'PAGEA1'` → **Success** (was read-only). Self-contained capture
`tools/protocol-research/qa-card90-capture-pagefield-selfcontained.feature` (connect + open + input
PF_PAGE_A_FIELD="PGFLDA" + a PF_EDIT_NUMBER focus-change). The read sweep shows `PF_PAGE_A_FIELD стал равен
"PGFLDA"` (committed). Traffic: `runtime/protocol-research/captures/genuine-card90-pagefield-20260617/
traffic-selfcontained/traffic.jsonl` (682 chunks; client TPort 48003 / manager 34718).

## The page-field element path (KEY)

The genuine SET frame addresses the page field 3 groups deep:

```
SecondaryFrame[S].ManagedForm[F].Group[PF_GROUP_MAIN].Group[PF_PAGES_MAIN].Group[PF_PAGE_A].EditField[PF_PAGE_A_FIELD]
```

So a leaf-only retarget from a different-group capture would build a WRONG path — hence the genuine page-field
capture is used directly (base==target, no retarget). The value buffer + commit law are the plain string SET.

## Native verify (no Vanessa) — ✅ PASS

`tools/protocol-research/set_page_field_probe.py` (open the form once via `NativeWriteSession`, write many):
wrote `PGNEW1` then `PGNEW2` into PF_PAGE_A_FIELD on a fresh native client (port 15381, vanessa_client FREE) —
both `readback=<value> committed=True`. (A single-shot `write_form_value` works for ONE write per client boot;
the open-once `NativeWriteSession` is required for multiple writes — a fresh client accepts one manager session.)

## Productization

No new MCP tool: **page-field input = the existing `write_form_value` with the page-field `capture`**
(base_field=target_field=PF_PAGE_A_FIELD). For a field on a NON-active page, compose the existing
`switch_page(target_page)` (card 86d, verified) first, then `write_form_value`. Probe:
`set_page_field_probe.py` (run via `run_table_cell_test.sh` with `PROBE=`/`CAP=`).

**Not yet done:** an end-to-end native `switch_page(PF_PAGE_B)` + `write_form_value(PF_PAGE_B_FIELD)` demo (the
switch-then-cross-page-input composition). Both primitives are individually verified; PF_PAGE_B_FIELD's own
genuine path needs a page-B capture (Vanessa auto-/explicit switch to page B) to drive `write_form_value`
without a two-segment retarget.
