# Card 96 / E2 — reference selection (`set_reference_field`): productized + live-verified capture-free

**Date:** 2026-06-18. **Card:** 96 (interaction breadth), change 2 (reference / value selection). **Status:**
DONE for same-length ref names — `set_reference_field` sets a CatalogRef field to an arbitrary catalog element
by NAME, no Vanessa (MCP tool #22, 229 tests, live-verified). Completes change 2 (value-list + menu + reference).

## Polygon — NO fixture edit / deploy needed (correction)

The fixture form **ALREADY has a reference field** `Контрагент` of type `CatalogRef.Контрагенты`
(`Group[Группа1].EditField[Контрагент]`, an InputField with a choice button) — so NO Form.form edit and NO
deploy were needed (this corrects an earlier wrong assumption that a typed attribute had to be added).

⚠ **Correction to an earlier wrong finding:** the Контрагенты catalog is NOT "groups only" — it has many leaf
elements (Магазин "Обувь", Корнет ЗАО, Скороход АО, Пантера АО, …) NESTED inside the groups Покупатели /
Поставщики. The selection form opens HIERARCHICAL with the groups at the top; clicking «Выбрать» on the active
GROUP raised "Выберите элемент, а не группу!" — the fix is to reach an element (expand the group / flat «Список»
view / type the name), not to seed data. (Thanks to the operator's screenshots for catching this.)

## Decode — reference set = "choice-by-string" (type-resolve), the value-SET family

A CatalogRef InputField resolves a TYPED name to a ref (выбор по строке) on focus-change. Capture
`genuine-card96-ref-20260618` (open form → «И в поле с именем 'Контрагент' я ввожу текст 'Корнет ЗАО'» →
focus-change via a PF_EDIT_STRING input → read-back). The typed name rides the wire as
**`e0 41 81 81 b7 <char-count:varint><utf-16le name><ASCII-space padding>`** — the SAME value-SET family as a
string write but with tag `b7` (vs the plain string's `ba`) and a **UTF-16LE** value with a **CHAR-count**
length prefix. The commit is the ordinary focus-change (the genuine session typed into PF_EDIT_STRING next). On
read-back the field reads as the resolved presentation (the Контрагент name). So a reference set ≈ a value write
whose value is a name the field resolves.

## Productize

`src/qa_mcp/protocol/native_write.py`:
- `retarget_ref_value(frame, old, new)` — swaps the UTF-16 name + the CHAR-count prefix, growing/shrinking the
  trailing ASCII-space padding to keep the frame size constant (the UTF-16 twin of the card-80 `retarget_value`).
- `SetReferenceFieldTemplate`, `derive_set_reference_field(capture_dir, field, captured_value)` (validates the
  UTF-16 choice value is present), `set_reference_field(template, value, …)` — a faithful full-stream replay of
  the genuine reference-input session, re-targeting the typed name to ``value``; commit confirmed by the
  resolved presentation reading back. MCP tool `set_reference_field(value, field, captured_value)` (the **22nd**).
- Unit tests `test_retarget_ref_value_fixed_width_utf16`, `test_derive_set_reference_field_validates_utf16_value`.

## Live proof (no Vanessa)

`tools/protocol-research/{set_reference_field_probe.py,run_reference_field_test.sh}`, fresh native client:
- `value="Пантера АО"` (re-targeted from the captured "Корнет ЗАО", **same 10-char length**) → `committed=true`
  — the field resolved the arbitrary name to its ref, presentation read back. PASS.

## Constraint (known refinement)

`value` must currently be the **same character length** as ``captured_value`` (10 chars). A variable-length name
("Скороход АО", 11 chars) does NOT commit even though the retarget keeps the frame size constant — the field's
edit buffer is length-fixed (the same fixed-width limit as the card-80 string write, one layer up). Workaround:
capture once per name-length, or re-capture with a same-length name. Lifting this (a length-aware ref buffer) is
the documented follow-up. The core capability — capture-free reference selection by name, no Vanessa — is proven.
