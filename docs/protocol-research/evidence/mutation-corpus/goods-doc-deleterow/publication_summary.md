# TestedFormTable.DeleteRow — accepted (Phase 1, breadth)

The third accepted mutation mapping. Producing it surfaced and closed a generic
normalizer gap (UTF-16LE-only session GUIDs), so the win is twofold: a new member
**and** a more robust decode for every future action.

| Field | Value |
| --- | --- |
| API member | `TestedFormTable.DeleteRow` |
| Action | delete a row from the goods document `ТоварныеЗапасы` tabular section |
| Manifest | `tools/protocol-research/action-manifests/goods-doc-deleterow.json` |
| Target | new (unsaved) `Документ.ОперацияПоУчетуТоваров` in `vanessa_client` |
| `mutates_business_data` | false (the document is never saved; no persistence) |

The manifest opens the document and adds a row in `bootstrap`, then deletes that
row in the `action` phase (so the delete has a row to operate on).

## The normalizer gap this exposed (and fixed)

The first probe came back `candidate`, not `accepted`: structurally identical
(168/168 exchanges, zero divergence) but the action-phase normalized hashes
differed by exactly **336 bytes**. Decoding the diff showed those bytes were a
single per-session **managed-form GUID** in the text `{GUID}].ManagedForm[`,
present in 6 frames — and present **only as UTF-16LE** (never ASCII):

| run | managed-form GUID |
| --- | --- |
| ref1 | `4254cda8-782d-48de-97ef-644f7d2d83b1` |
| ref2 | `0280e622-ce85-4f8b-9d85-a77b1e14fa4c` |

`session_guids()` scanned only the raw bytes with an ASCII GUID regex, so it
found **zero** GUIDs in these frames and stripped nothing. AddRow never hit this
because its append frames carry no managed-form GUID in the action phase.

**Fix:** `session_guids()` now also scans a UTF-16LE decode of each payload, so a
GUID in either encoding is collected; `normalize_payload()` already strips both
encodings given the GUID string. Regression test:
`tests/test_compare_probe_reference.py::test_session_guids_detects_utf16le_only_guid`.

## Loop result (after the fix)

- **stability** (ref1 vs ref2, phase=action) -> **`fully_stable`**
  (residual 0, `stability_ref1_vs_ref2.json`).
- **probe**: `adaptive_replay_probe.py` reproduced the flow live (168/168
  exchanges, zero divergence).
- **acceptance** (probe-ordinal, phase=action) -> **`accepted`**
  (`python_manager_acceptance.json`).
- **promote** -> `accepted_reviewed` (mutation 3/9).

## Significance

The breadth loop is not just a counter — it is a normalizer-hardening engine. Each
new action that references existing form state can expose a dynamic field the
generic decode does not yet handle; closing that gap (here, UTF-16LE GUIDs)
improves acceptance for the whole surface, not just this member.

Raw captures stay under ignored `runtime/protocol-research/captures/`.
