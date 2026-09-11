# TestedFormTable.AddRow — accepted (Phase 1, breadth)

The second accepted mutation mapping, produced entirely through the generalized
manifest-driven pipeline (no warehouse-specific code).

| Field | Value |
| --- | --- |
| API member | `TestedFormTable.AddRow` |
| Action | add a row to the goods document `ТоварныеЗапасы` tabular section |
| Manifest | `tools/protocol-research/action-manifests/goods-doc-addrow.json` |
| Target | new (unsaved) `Документ.ОперацияПоУчетуТоваров` in `vanessa_client` |
| `mutates_business_data` | false (the document is never saved; no persistence) |

## Loop (the breadth per-action loop)

1. **capture x2** via `run_protocol_capture.ps1 -Scenario demo-action-manifest
   -ActionManifest goods-doc-addrow.json` (319 frames; phases bootstrap /
   pre_read / action / post_read).
2. **decode/stability**: `compare_probe_reference.py --mode stability --phase
   action` -> **`fully_stable`** (two reference runs byte-identical,
   `stability_ref1_vs_ref2.json`).
3. **probe**: `adaptive_replay_probe.py` replayed the flow live (158/158
   exchanges, zero divergence).
4. **acceptance**: `compare_probe_reference.py --mode probe-ordinal --phase
   action` -> **`accepted`** (manager and client action frames match the Vanessa
   reference, `python_manager_acceptance.json`).
5. **promote**: `promote_member.py --api TestedFormTable.AddRow --bucket
   accepted_reviewed` -> scope tracker now `accepted_reviewed=2` (mutation 2/9).

## Significance

This validates the breadth pipeline end to end: a new API member went from a
manifest to an `accepted_reviewed` mapping with no member-specific code. The
remaining mutation members follow the same loop (author a manifest -> capture ->
probe -> compare -> promote).

Raw captures stay under ignored `runtime/protocol-research/captures/`.
