# TestedFormTable.ChangeRow — accepted (Phase 1, breadth)

The fifth accepted mutation mapping, and the third in the tabular-section row-op
family (after AddRow and DeleteRow). Reached after the user chose to pivot here
when `TestedFormDecoration.Click` proved blocked on a config fixture (see
`../eventlog-filter-decoration-click/findings.md`).

| Field | Value |
| --- | --- |
| API member | `TestedFormTable.ChangeRow` (`ТЧ.ИзменитьСтроку`) |
| Action | begin editing a committed row of the goods document `ТоварныеЗапасы` table |
| Manifest | `tools/protocol-research/action-manifests/goods-doc-changerow.json` |
| Target | new (unsaved) `Документ.ОперацияПоУчетуТоваров` in `vanessa_client` |
| `mutates_business_data` | false (the document is never saved; no persistence) |

## Why the bootstrap commits a row first

`ВТаблицеЯНачинаюРедактированиеСтроки` calls `ТЧ.ИзменитьСтроку()` **only when the
table is not already in edit mode** (`Если НЕ ТЧ.ТекущийРежимРедактирование()`).
`AddRow` leaves the new row in edit mode, so the bootstrap adds a row, fills
`Количество=1` (so the row is retained), then **finishes editing** to return to
browse mode. The `action` phase then begins editing that committed row, which is
the single `ИзменитьСтроку` (ChangeRow) call. Confirmed against the upstream
VanessaAutomation step definitions.

## Loop result

- **stability** (ref1 vs ref2, phase=action) → **`fully_stable`**
  (`all_hashes_match`, residual 0, `stability_ref1_vs_ref2.json`) — clean on the
  first try; the existing UTF-16LE managed-form-GUID normalizer covered it.
- **probe**: `adaptive_replay_probe.py` reproduced the flow live, **182/182**
  exchanges, zero divergence (`adaptive_replay_summary.json`).
- **acceptance** (probe-ordinal, phase=action) → **`accepted`**, both directions
  hash-match, `structural_match` (`python_manager_acceptance.json`).
- **promote** → `accepted_reviewed` (mutation **5/9**, total 5/160).

## Note on a probe-harness fix surfaced here

The first two probe runs returned `mismatch` on `client_to_manager` only, with the
`manager_to_client` (command) direction matching exactly and the action client
frames byte-identical under a constant **+1** offset. Root cause was **not** the
member: the ad-hoc probe runner waited for the proxy by **TCP-connecting through
it**, which made the proxy record a spurious extra downstream connection (a leading
5-byte client handshake frame), shifting every client ordinal by one. The fix
(`tools/protocol-research/probe_runner.ps1`) waits on the proxy **ready-file** and
checks listen state passively (`Get-NetTCPConnection`), never connecting through
the proxy. Attempt 3 recorded a single clean connection and the compare accepted.
The runner is now committed so the probe step is reproducible for the remaining
members.

Raw captures stay under ignored `runtime/protocol-research/captures/`.
