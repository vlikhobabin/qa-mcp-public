# TestedFormTable.SwitchRowDeleteMark — accepted (Phase 1, breadth)

The eighth accepted mutation mapping. Unlike the four tabular-section row ops, this
member only works on a **dynamic list** (rows that are DB objects with a deletion
mark), so it took a different, carefully data-safe approach.

| Field | Value |
| --- | --- |
| API member | `TestedFormTable.SwitchRowDeleteMark` (`ПереключитьПометкуУдаленияСтроки`) |
| Action | toggle the delete mark of the current row of the `Справочник.Склады` list |
| Manifest | `tools/protocol-research/action-manifests/warehouse-list-switchdeletemark.json` |
| Target | `Справочник.Склады` list in `vanessa_client` |
| `mutates_business_data` | false (the confirmation is never answered — see below) |

## Why a tabular section does not work (proven)

The first attempt toggled the delete mark of a `ТоварныеЗапасы` register-records row
(`goods-doc-switchdeletemark.json`); the platform rejected it with
`Неподходящий тип элемента управления для вызванного действия` — tabular-section
rows have no delete mark. A dynamic list of catalog objects is required.

## Why it does not persist

`ПереключитьПометкуУдаленияСтроки` only **opens** the confirmation dialog
`Пометить выбранный элемент на удаление?` (captured in `switchdel-learn1`); the mark
is written to the DB only on `Да`. The capture/probe never click `Да`, and the
TestClient is then killed with the dialog pending — so toggling an **existing**
warehouse touches no data, while keeping the object ref stable across runs
(`fully_stable`). The post-toggle confirmation form is preserved here as
`post_toggle_confirmation_dialog.json`.

## Data-safety incident (resolved)

During an earlier probe run an operator manually clicked `Да` on the live
TestClient, which confirmed the mark on 5 warehouses. This was fully reverted with a
COM script (`УстановитьПометкуУдаления(Ложь)` on every marked `Склады`), verified
`remaining_marked_warehouses=0`; the learning-run throwaway region was also deleted.
The probe was then re-run clean (no manual interaction) — **never click anything in
the TestClient during a probe**; the replay is automated and intentionally leaves
the confirmation unanswered.

## Loop result

- **stability** (ref1 vs ref2, phase=action) → **`fully_stable`**
  (`all_hashes_match`, residual 0, `stability_ref1_vs_ref2.json`).
- **probe** (clean re-run): `adaptive_replay_probe.py` reproduced it live,
  **260/260** exchanges, zero divergence (`adaptive_replay_summary.json`).
- **acceptance** (probe-ordinal, phase=action) → **`accepted`**, both directions
  hash-match, `structural_match` (`python_manager_acceptance.json`).
- **promote** → `accepted_reviewed` (mutation **8/9**, total 8/160).

Raw captures stay under ignored `runtime/protocol-research/captures/`.
