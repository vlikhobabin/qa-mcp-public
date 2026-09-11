# Manager Fixture V2 Safe-Action Catalog

The reviewed manager V2 safe-action catalog lives at:

`tools/protocol-research/manager_fixture_v2_safe_action_catalog.json`

It is the allowlist gate for the future `manager-fixture-v2-safe-action`
runner. Passing catalog validation means a row may become candidate input for
the manager runner. It does not accept a protocol mapping and does not prove
live TestClient action behavior.

## Row Contract

Each executable row uses the V2 safe-action manifest fields from
`docs/protocol-research/safe-ui-action-scope.md`:

- `action_id`
- `target_id`
- `target_marker`
- `pre_state`
- `action`
- `post_state`
- `recovery_expectation`
- `mutates_business_data=false`
- `allowed_action_family`
- `expected_action_result_markers`

The row also records `provider_owner`, `status_reason` and `residual_risk` so
candidate, blocked, unsupported and rejected rows keep an owner and a handoff
reason.

## Target Binding

The catalog embeds `safe_action_targets` with stable V2 target ids and
reviewed `PF_*` markers. The validator fails closed when an executable action:

- references a target id missing from the target set;
- uses a marker that does not match the target marker;
- selects an action family not allowed for that target;
- points at a target whose target status is blocked, pending, unsupported,
  partial or timeout.

The target set links back to the reviewed client fixture target-map evidence:

- `docs/protocol-research/evidence/fixture-target-maps/20260607-client-fixture-v2-safe-action-target-map/target_map_summary.md`
- `docs/protocol-research/evidence/fixture-target-maps/20260604-client-fixture-v1-target-map/target_map.json`

## Non-Executable Rows

Rows outside the current V2 execution subset remain visible:

- `blocked` rows keep the target, marker, attempted family, owner, reason and
  residual risk.
- `rejected` rows show excluded action families such as command or button
  clicks.
- No non-executable row is written into the manager harness executable command
  list.

## Offline Validation

Validate the reviewed catalog without starting 1C:

```powershell
python tools\protocol-research\v2_safe_action_tooling.py validate `
  --manifest tools\protocol-research\manager_fixture_v2_safe_action_catalog.json `
  --output-dir .artifacts\openspec\define-manager-fixture-v2-safe-action-catalog\<run-id>\catalog-validation `
  --write-phase-events `
  --require-executable
```

The dry-run output retains `v2_safe_action_manifest_validation.json`,
`safe_action_phase_events.jsonl`, `safe_action_runner_results.jsonl`,
`manager_harness_manifest.json` and `manager_harness_result.json` under the
ignored evidence directory.
