## 1. Focused Live Capture

- [x] 1.1 Consume the reviewed focused subset from
  `select-focused-v2-safe-action-subset`.
- [x] 1.2 Run the Windows-native `manager-fixture-v2-safe-action` scenario for
  the selected row or rows with a stable run id.
- [x] 1.3 Retain pre-read, action-start, action-end, post-read and recovery or
  recovery-read events for each attempted row.
- [x] 1.4 Record blocked, rejected, partial or timeout rows with typed status
  and reason.

## 2. Runtime Output Hygiene

- [x] 2.1 Keep raw captures, process logs and generated replay payloads under
  `runtime/protocol-research/captures/<run-id>/`.
- [x] 2.2 Publish only compact capture summaries under
  `.artifacts/openspec/capture-focused-v2-safe-action-run/<run-id>/` or reviewed
  docs paths.
- [x] 2.3 Confirm no full infobases, platform logs, raw large captures or
  credentials are added to reviewed git.

## 3. Verification

- [x] 3.1 Retain live capture summary and command transcript under
  `.artifacts/openspec/capture-focused-v2-safe-action-run/<run-id>/capture/`.
- [x] 3.2 Run `bin\openspec.cmd validate capture-focused-v2-safe-action-run --strict`.
- [x] 3.3 Run `git diff --check -- openspec/changes/capture-focused-v2-safe-action-run docs/protocol-research tools/protocol-research openspec/board`.

## Blocked Evidence

- Live run id: `20260607-first-focused-v2-safe-action-live-gate`
- Dry-run id: `20260607-first-focused-v2-safe-action-dry-run`
- Compact blocked summary:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-capture-gate/blocked_capture_summary.md`
- Safety stop: the live scenario fails closed before 1C startup with
  `manager-fixture-v2-safe-action live capture is gated until the manager fixture V2 safe-action runner is available`.

## Live Evidence

- Live run id: `20260607-first-focused-v2-safe-action-live-runner-2`
- Runtime output:
  `runtime/protocol-research/captures/20260607-first-focused-v2-safe-action-live-runner-2/`
- Compact evidence:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/`
- Runner result: `status=ok`, `command_count=2`, `completed_count=2`,
  `live_action_executed=true`.
- Phase events: 12 retained events, covering `pre_read`, `action_start`,
  `action_end`, `post_read`, `recovery` and `recovery_read` for both focused
  rows.
- Frame join: 2 joined rows with separate `action_frame_range`,
  `background_frame_ranges` and `recovery_frame_range`; rows remain candidate
  because replay/probe proof is not retained yet.

## 4. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Windows V2 safe-action capture run against `C:\1C_BASES\vanessa_client` and `C:\1C_BASES\vanessa_manager` | Operator-reviewed run id, manifest path and Windows command plan | Runtime command summary; process ownership notes; compact capture summary; OpenSpec strict validation | `.artifacts/openspec/capture-focused-v2-safe-action-run/<run-id>/capture/` | required | `project:qa-mcp` | N/A | Medium: local 1C session startup can fail or leave no action evidence |
| Form module or command | Manager fixture V2 safe-action runner commands for selected rows | Phase event sequence and typed runner status per row | `case_events.jsonl` summary; action result markers; recovery summary | `.artifacts/openspec/capture-focused-v2-safe-action-run/<run-id>/phase-events/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: command path can fail closed due to hidden or disabled target |
| Managed form layout | Client fixture selected target markers and recovery state | Pre-state, post-state and recovery or known-state marker reads | Form/marker read summary; retained runtime summary | `.artifacts/openspec/capture-focused-v2-safe-action-run/<run-id>/state-markers/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: fixture UI state can differ from offline target-map review |
