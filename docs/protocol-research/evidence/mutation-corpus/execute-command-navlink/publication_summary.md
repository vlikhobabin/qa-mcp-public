# TestedClientApplicationWindow.ExecuteCommand — accepted (Phase 1, breadth)

The ninth accepted mutation mapping — **the last member of the `mutation` bucket,
which is now fully covered (9/9).**

| Field | Value |
| --- | --- |
| API member | `TestedClientApplicationWindow.ExecuteCommand` (`ВыполнитьКоманду`) |
| Action | navigate the main window to the `Справочник.Склады` list |
| Manifest | `tools/protocol-research/action-manifests/execute-command-navlink.json` |
| Target | main application window in `vanessa_client` |
| `mutates_business_data` | false (opens a read-only list; nothing persists) |

## Mapping

The step `я перехожу по навигационной ссылке "..."` (`ЯПерехожуПоНавигационнойСсылке`)
calls `ГлавноеОкноТестируемого.ВыполнитьКоманду(НавигационнаяСсылка)` =
`TestedClientApplicationWindow.ExecuteCommand`, confirmed against the upstream
VanessaAutomation step definitions. This is distinct from the bootstrap
`я открываю навигационную ссылку`. The bootstrap opens the goods document list; the
`action` phase navigates to the `Склады` list via `ExecuteCommand`.

## Loop result

- **stability** (ref1 vs ref2, phase=action) → **`fully_stable`**
  (`all_hashes_match`, residual 0, `stability_ref1_vs_ref2.json`).
- **probe**: `adaptive_replay_probe.py` reproduced it live, **147/147** exchanges,
  zero divergence (`adaptive_replay_summary.json`).
- **acceptance** (probe-ordinal, phase=action) → **`accepted`**, both directions
  hash-match, `structural_match` (`python_manager_acceptance.json`).
- **promote** → `accepted_reviewed` (mutation **9/9**, total 9/160).

## Milestone

With this member the entire `mutation` bucket (9 members) is `accepted_reviewed`:
Button.Click, Table.AddRow / ChangeRow / DeleteRow / CopyRow / SwitchRowDeleteMark,
Window.Close, Decoration.Click, Window.ExecuteCommand.

Raw captures stay under ignored `runtime/protocol-research/captures/`.
