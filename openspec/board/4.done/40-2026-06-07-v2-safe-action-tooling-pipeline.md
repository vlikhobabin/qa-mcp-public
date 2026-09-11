# 40. V2 Safe-Action Tooling Pipeline

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
40

## Source
- 2026-06-07 V2 planning discussion
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- Client and manager fixture V2 backlog cards

## Summary
Extend the protocol tooling so manager fixture V2 safe-action runs can produce
reviewed evidence with isolated action frames. The tooling should keep action
traffic separate from bootstrap, background refresh and recovery traffic, and
must not promote mappings without replay/probe or typed contract evidence.

## Expected Scope
- Add a capture scenario such as `manager-fixture-v2-safe-action`.
- Add or document a machine-readable safe-action manifest schema.
- Add a V2 reporter, preferably separate from the V1 read-only reporter, for
  safe-action frame joins and compact evidence.
- Record `action_frame_range`, `background_frame_ranges`,
  `recovery_frame_range`, `action_result_markers`, `pre_state`, `post_state`
  and `recovery_result`.
- Classify safe-action rows as `candidate`, `accepted`, `rejected`, `blocked`,
  `partial` or `timeout`.
- Extend compare/replay hooks only where evidence can remain compact and
  reproducible.
- Keep raw traffic and generated replay payloads under ignored runtime paths.

## Change Set
- `openspec/changes/archive/2026-06-07-add-manager-fixture-v2-safe-action-scenario/`
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-tooling-manifest/`
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-evidence-reporter/`
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-acceptance-gates/`

## Out Of Scope
- Implementing client fixture UI handlers.
- Implementing manager-side action execution.
- Accepting real demo button behavior before fixture V2 proof exists.
- Mutation or rollback tooling for V3.

## Acceptance
- A safe-action capture can publish compact reviewed evidence without raw TCP in
  git.
- Action frames are separated from background and recovery ranges.
- Joined action evidence remains `candidate` until accepted replay/probe or a
  typed contract matches the action row.
- Existing V1 read-only reporting remains stable.

## Delivery Gate
- Full live verification depends on the manager fixture V2 safe-action runner
  card producing reviewed action event boundaries.
- If this card is implemented before that runner is archived, limit delivery to
  offline manifest, reporter and comparison samples, and keep live capture
  evidence marked pending.

## Verify
- `bin\openspec.cmd validate add-manager-fixture-v2-safe-action-scenario --strict`
- `bin\openspec.cmd validate define-v2-safe-action-tooling-manifest --strict`
- `bin\openspec.cmd validate add-v2-safe-action-evidence-reporter --strict`
- `bin\openspec.cmd validate add-v2-safe-action-acceptance-gates --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check -- openspec/changes/add-manager-fixture-v2-safe-action-scenario openspec/changes/define-v2-safe-action-tooling-manifest openspec/changes/add-v2-safe-action-evidence-reporter openspec/changes/add-v2-safe-action-acceptance-gates openspec/board/2.todo/40-2026-06-07-v2-safe-action-tooling-pipeline.md`
- `python -m pytest -p no:cacheprovider --basetemp C:\Temp\qa-mcp-pytest\full`
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\protocol-research\run_protocol_capture.ps1 -Scenario manager-fixture-v2-safe-action -DryRun -RunId 20260607-v2-safe-action-dry-run -SafeActionManifestPath .artifacts\openspec\define-v2-safe-action-tooling-manifest\20260607-offline-samples\manifest-validation\v2-safe-action-manifest.sample.json`

## Archive
- `openspec/changes/archive/2026-06-07-add-manager-fixture-v2-safe-action-scenario/`
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-tooling-manifest/`
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-evidence-reporter/`
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-acceptance-gates/`

## Related
- `openspec/board/4.done/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/4.done/10-2026-06-07-v2-readiness-docs-and-safety-contract.md`
- `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
- `openspec/changes/archive/2026-06-07-add-manager-fixture-v2-safe-action-scenario/`
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-tooling-manifest/`
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-evidence-reporter/`
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-acceptance-gates/`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/safe-ui-action-scope.md`

## Result
offline V2 safe-action tooling delivered and archived; live action proof remains
gated by manager fixture V2 safe-action runner readiness

Implemented:
- `manager-fixture-v2-safe-action` dry-run scenario in the Windows capture
  wrapper, including fail-closed live gating.
- Machine-readable V2 safe-action manifest validation for required fields,
  allowlisted families and `mutates_business_data=false`.
- Separate V2 safe-action reporter with action/background/recovery ranges,
  result fields and non-accepted reasons.
- Comparison and accepted-mapping gates that keep safe-action rows out of
  accepted output until hash, action markers and replay/probe or typed contract
  proof are present.
- Offline retained evidence under `.artifacts/openspec/...` and ignored
  runtime output under `runtime/protocol-research/captures/20260607-v2-safe-action-dry-run/`.

## Next
- continue with the manager fixture V2 safe-action runner card, then first
  focused V2 safe-action proof

## Publish
- Durable docs updated: `docs/protocol-research/protocol-corpus-runner.md`
  and `docs/protocol-research/corpus-evidence-contract.md`.
- Main spec synced: `openspec/specs/qa-mcp-protocol-lab/spec.md`.
- Delivery manifest:
  `.runtime/opsx/delivery-manifests/40-2026-06-07-v2-safe-action-tooling-pipeline.json`.
- Runtime and offline proof artifacts remain excluded from git under
  `.artifacts/openspec/...` and
  `runtime/protocol-research/captures/20260607-v2-safe-action-dry-run/`.
- Commit and push are handled by this `$opsx-pub` publication pass.

## Change 1: `add-manager-fixture-v2-safe-action-scenario`

### Why
Safe-action evidence needs a capture scenario that separates pre-read, action,
post-read, recovery and background traffic.

### Goal
Add a `manager-fixture-v2-safe-action` scenario boundary for phase-aware
runtime output.

### Scope
- Add the safe-action capture scenario entrypoint.
- Require reviewed manifest rows before capture starts.
- Emit phase-aware side-channel events without injecting TCP markers.

### Acceptance
- The scenario can produce phase-aware runtime output under ignored paths.
- Missing or unsafe manifest rows fail closed before capture.

### Depends On
- none for offline wiring
- live proof depends on `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`

### Related
- `openspec/changes/archive/2026-06-07-add-manager-fixture-v2-safe-action-scenario/`

### Notes For `$openspec-ff-change`
- Keep raw captures out of reviewed git and retain only compact dry-run
  summaries.

## Change 2: `define-v2-safe-action-tooling-manifest`

### Why
The tooling needs a machine-readable row contract before it can capture or
report safe actions safely.

### Goal
Define fail-closed validation for V2 safe-action manifest rows.

### Scope
- Define required fields from the V2 safety contract.
- Reject incomplete, mutating or unsupported rows before capture.
- Link manifest rows to fixture target maps and corpus rows.

### Acceptance
- Manifest examples cover accepted-for-capture, rejected, unsupported and
  pending rows.
- Mutation families remain outside V2.

### Depends On
- `add-manager-fixture-v2-safe-action-scenario`

### Related
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-tooling-manifest/`

### Notes For `$openspec-ff-change`
- A valid manifest row permits capture or reporting only; it does not accept a
  protocol mapping.

## Change 3: `add-v2-safe-action-evidence-reporter`

### Why
V2 action evidence needs compact reporting that keeps action, background and
recovery ranges separate.

### Goal
Add a safe-action reporter that publishes reviewed rows without regressing V1
read-only reporting.

### Scope
- Emit action-specific frame ranges and result markers.
- Preserve candidate and non-accepted statuses with reasons.
- Keep raw payloads and generated replay data outside reviewed git.

### Acceptance
- Safe-action rows include action/background/recovery ranges where present.
- Existing V1 read-only reporter output remains stable.

### Depends On
- `define-v2-safe-action-tooling-manifest`

### Related
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-evidence-reporter/`

### Notes For `$openspec-ff-change`
- Treat action-frame joins as candidate evidence until acceptance gates attach
  replay/probe or typed contract proof.

## Change 4: `add-v2-safe-action-acceptance-gates`

### Why
Joined action frames must not be promoted to accepted mappings without
repeatable proof.

### Goal
Gate accepted V2 safe-action mappings on stable hashes, action markers and
replay/probe or typed contract evidence.

### Scope
- Extend comparison and accepted-mapping gates for safe-action rows.
- Keep unresolved rows visible as candidate or another explicit non-accepted
  status.
- Preserve compact proof links and keep raw replay/probe payloads ignored.

### Acceptance
- Accepted output excludes joined rows that lack accepted proof.
- Non-accepted rows remain visible in comparison output with reasons.

### Depends On
- `add-v2-safe-action-evidence-reporter`

### Related
- `openspec/changes/archive/2026-06-07-add-v2-safe-action-acceptance-gates/`

### Notes For `$openspec-ff-change`
- Do not broaden this change into V3 mutation or real demo button acceptance.

## Log
- 2026-06-07T00:00:00Z card created
- 2026-06-07T00:00:00Z fast-forwarded into four OpenSpec changes and moved to `2.todo`
- 2026-06-07T15:21:37Z publish scope recorded from the OPSX delivery manifest
