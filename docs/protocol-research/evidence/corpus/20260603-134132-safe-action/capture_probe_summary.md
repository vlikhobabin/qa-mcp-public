# Safe Action Capture Summary 20260603-134132

## Command

```powershell
python tools\protocol-research\protocol_corpus_runner.py --run-capture --capture-scenario safe-action --case-set safe-action --case-manifest docs\protocol-research\evidence\safe-action-candidates\20260603-opsx-do-safe-action\safe_action_case_manifest.json --vanessa-epf C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\vanessa-mcp\releases\vanessa\single\vanessa-automation-single-51f920f-windows-screenshot-fixes.epf --json
```

The reviewed compact evidence was regenerated from the retained raw capture
without starting 1C again after the runner learned to redact localized window
title values from committed rows:

```powershell
python tools\protocol-research\protocol_corpus_runner.py --capture-dir 20260603-134132 --case-set safe-action --case-manifest docs\protocol-research\evidence\safe-action-candidates\20260603-opsx-do-safe-action\safe_action_case_manifest.json --evidence-dir docs\protocol-research\evidence\corpus\20260603-134132-safe-action --json
```

## Retained Evidence

- Candidate manifest:
  `docs/protocol-research/evidence/safe-action-candidates/20260603-opsx-do-safe-action/`.
- Compact corpus evidence:
  `docs/protocol-research/evidence/corpus/20260603-134132-safe-action/`.
- Raw capture output:
  `runtime/protocol-research/captures/20260603-134132/`.
- UI evidence bundle:
  `.artifacts/openspec/capture-safe-ui-action-evidence/20260603-134132/`.

## Result

The Windows-native `safe-action` capture completed. It attached Vanessa to the
running TestClient through the TCP proxy, listed existing internal TestClient
windows, invoked `activate_window` for an already-open window, then attempted
recovery by reactivating the original window when the target differed.

The reviewed row remains non-accepted:

| Case id | Action | Capture id | Frame range | Normalized hash | Replay/probe status | Runtime status | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `safe-activate-existing-window` | `activate_window` | `20260603-134132` | N/A | N/A | `pending` | `pending` | The provider invoked the safe action, but the active window did not change to the selected target and no action frame range has been joined yet. |

The compact row redacts localized window title values and keeps only
reviewable marker facts:

- `action_result_markers`: `status=pending`, `window_title_observed`;
- `action_runtime_result.target_selected`: `true`;
- `action_runtime_result.post_matches_target`: `false`;
- `action_runtime_result.recovered_matches_pre`: `true`.

## Cleanup

`runtime/protocol-research/captures/20260603-134132/capture_summary.json`
records owned-PID cleanup:

- stopped manager pid `14460`;
- stopped proxy pid `20320`;
- stopped TestClient pid `3288`.

## Safety

No text input, command invocation with business side effects, checkbox toggle,
table edit, save/post/delete or persisted business-data mutation was performed.
The captured action is retained as unresolved safe-action evidence only.
