# Safe Action Classification Summary

- Change: `classify-safe-ui-action-mappings`
- Capture input:
  `docs/protocol-research/evidence/corpus/20260603-134132-safe-action/`
- Comparison output:
  `docs/protocol-research/evidence/corpus-comparison/safe-action-20260603-134132/`
- Accepted-mapping output:
  `docs/protocol-research/evidence/accepted-mappings/safe-action-20260603-134132/`

Command:

```powershell
python tools\protocol-research\compare_corpus_runs.py `
  docs\protocol-research\evidence\corpus\20260603-134132-safe-action `
  --comparison-id safe-action-20260603-134132 `
  --accepted-output-dir docs\protocol-research\evidence\accepted-mappings\safe-action-20260603-134132 `
  --json
```

Result:

| Case id | Action | Classification | Accepted | Reasons | Next owner |
| --- | --- | --- | --- | --- | --- |
| `safe-activate-existing-window` | `activate_window` | `pending` | no | `missing_action_frame_range`, `missing_request_frames`, `missing_safe_action_hash`, `pending_action_result`, `replay_or_probe_unavailable` | `/opt/vanessa-mcp-stack`, `project:qa-mcp` |

The row is useful coverage evidence, but it is not protocol knowledge yet. The
capture selected an already-open internal window and invoked
`activate_window`, but the reviewed corpus row has no action frame range, no
request or response bytes, no normalized hash, no operation token and no
accepted replay or direct Python-manager proof.

No package descriptor is promoted by this classification. Current reusable
package APIs remain read-only, and there is no evidence-backed direct safe
action replay/probe path for `activate_window`.
