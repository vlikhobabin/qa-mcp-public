# TestedFormTable.CopyRow — accepted (Phase 1, breadth)

The seventh accepted mutation mapping, and the fourth tabular-section row op (after
AddRow, DeleteRow, ChangeRow).

| Field | Value |
| --- | --- |
| API member | `TestedFormTable.CopyRow` (`Таблица.СкопироватьСтроку`, F9) |
| Action | copy the current row of the goods document `ТоварныеЗапасы` table |
| Manifest | `tools/protocol-research/action-manifests/goods-doc-copyrow.json` |
| Target | new (unsaved) `Документ.ОперацияПоУчетуТоваров` in `vanessa_client` |
| `mutates_business_data` | false (the document is never saved; no persistence) |

## Bootstrap

Same committed-row pattern as ChangeRow: open a new document, add a `ТоварныеЗапасы`
row, fill `Количество=1`, finish editing (commit). The `action` phase then copies
that committed row (`в таблице ... я копирую строку` → `СкопироватьСтроку`).

## Loop result

- **stability** (ref1 vs ref2, phase=action) → **`fully_stable`**
  (`all_hashes_match`, residual 0, `stability_ref1_vs_ref2.json`).
- **probe**: `adaptive_replay_probe.py` reproduced it live, **186/186** exchanges,
  zero divergence (`adaptive_replay_summary.json`), single clean connection.
- **acceptance** (probe-ordinal, phase=action) → **`accepted`**, both directions
  hash-match, `structural_match` (`python_manager_acceptance.json`).
- **promote** → `accepted_reviewed` (mutation **7/9**, total 7/160).

Raw captures stay under ignored `runtime/protocol-research/captures/`.
