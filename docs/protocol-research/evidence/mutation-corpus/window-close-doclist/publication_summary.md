# TestedClientApplicationWindow.Close — accepted (Phase 1, breadth)

The fourth accepted mutation mapping, and the first outside the tabular-section
family — a client application window lifecycle action.

| Field | Value |
| --- | --- |
| API member | `TestedClientApplicationWindow.Close` |
| Action | close the current window |
| Manifest | `tools/protocol-research/action-manifests/window-close-doclist.json` |
| Target | goods document list `Документ.ОперацияПоУчетуТоваров` in `vanessa_client` |
| `mutates_business_data` | false (an unmodified list window; nothing persists) |

The bootstrap opens the document **list** (an unmodified window that closes
without a "save changes?" prompt); the action phase closes the current window via
`И я закрываю текущее окно`, the canonical Vanessa close step (confirmed against
the upstream VanessaAutomation step definitions, not guessed).

## Loop result

- **stability** (ref1 vs ref2, phase=action) -> **`fully_stable`**
  (residual 0, `stability_ref1_vs_ref2.json`) — clean on the first try thanks to
  the UTF-16LE GUID normalization added for DeleteRow.
- **probe**: `adaptive_replay_probe.py` reproduced the close live
  (146/146 exchanges, zero divergence).
- **acceptance** (probe-ordinal, phase=action) -> **`accepted`**
  (`python_manager_acceptance.json`).
- **promote** -> `accepted_reviewed` (mutation 4/9, total 4/160).

## Note on the run

This capture was initially blocked by a machine-level 1C software-license failure
(every 1C session, even a single one, returned "no license found"). The block was
environmental, not in the code/manifest/step; once the license was restored the
loop ran clean. See the `license-drift-blocker` memory.

Raw captures stay under ignored `runtime/protocol-research/captures/`.
