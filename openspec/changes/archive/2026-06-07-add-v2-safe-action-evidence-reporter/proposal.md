## Why

Safe-action captures need a reporter that can join action frame ranges without
mixing action traffic with bootstrap, background refresh or recovery frames.
The V1 read-only reporter is intentionally conservative and should remain
stable while V2 evidence gains action-specific fields.

## What Changes

- Add a V2 safe-action evidence reporter separate from the V1 read-only
  reporter.
- Publish compact reviewed rows with `action_frame_range`,
  `background_frame_ranges`, `recovery_frame_range`,
  `action_result_markers`, `pre_state`, `post_state` and
  `recovery_result`.
- Preserve non-accepted action rows as `candidate`, `blocked`, `partial`,
  `timeout`, `rejected` or `unsupported`.
- Keep raw traffic and generated replay payloads outside reviewed git changes.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 safe-action tooling gains a compact evidence
  reporter for action-frame joins and reviewed summaries.

## Impact

- Protocol reporting tools under `tools/protocol-research/`.
- Reviewed evidence docs under `docs/protocol-research/evidence/`.
- Requires Windows-native capture or fixture-output samples for verification.
