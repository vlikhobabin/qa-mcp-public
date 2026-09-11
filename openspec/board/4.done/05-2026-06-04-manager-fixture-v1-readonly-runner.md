# 05. TestManager Fixture Processor V1: Read-Only Command Runner

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
05

## Source
- 2026-06-04 planning session
- `docs/protocol-research/research-plan.md`
- `docs/protocol-research/evidence/fixture-runtime/20260604-client-fixture-v1-live-open/runtime_summary.md`
- V1 client fixture processor card

## Summary
Create the first dedicated manager-side fixture processor/harness in the
TestManager infobase. V1 should use standard 1C TestManager/TestedApplication
APIs to drive the live client fixture through a TCP proxy and produce a
deterministic read-only command/event log that can be joined to captured
protocol frames.

Vanessa Automation remains useful as bootstrap, smoke-test and comparison
evidence, but it should not be the primary generator of the protocol corpus for
this controlled fixture path.

## Expected Scope
- Create or prepare a dedicated manager-side processor/harness in the
  `vanessa_manager` runtime/project context.
- Establish the manager target binding and deployment path if an EDT manager
  project is required.
- Define a stable run manifest format with `run_id`, `case_id`,
  `command_id`, target fixture path, proxy/TestClient port and expected
  markers.
- Connect the manager harness to the TestClient through the proxy port, not
  directly to the real TestClient port.
- Open the client fixture processor form as a bootstrap step and label that
  traffic separately from read-only corpus cases.
- Implement a read-only command catalog for the client V1 fixture:
  active window, active form, form summary, element enumeration, element
  value/text/caption, visibility, enabled/read-only state, tested object class,
  table rows/columns, command bar buttons, groups and pages.
- Write a manager-side event log with timestamps before/after every command,
  command status, target `PF_*` marker, expected response marker and failure
  details.
- Write compact run output such as `manager_harness_result.json` and
  `case_events.jsonl` under the capture/runtime directory selected by the
  capture runner.
- Integrate the harness with the protocol capture script so the proxy traffic,
  manager event log and TestClient/manager logs share one capture id.
- Keep all raw TCP data, 1C logs and generated runtime output under ignored
  `runtime/` paths.

## Out Of Scope
- TCP parsing, protocol normalization or socket handling inside 1C.
- Treating Vanessa Automation feature steps as the primary corpus generator.
- Text input, clicks, page switching, row selection or other safe actions as
  accepted command cases.
- Business commands and writes to catalogs, documents, registers, settings or
  external services.
- Promoting protocol mappings without frame ranges, dynamic-field
  normalization and replay/direct Python-manager evidence.

## Acceptance
- The manager V1 harness can run a read-only scenario against the live client
  fixture form through the proxy.
- Each emitted command has a stable `case_id`, `command_id`, target marker and
  expected marker.
- The capture directory contains proxy traffic plus a manager event log that
  can be used to join command boundaries to frame ranges.
- The V1 run does not mutate business data or fixture local state beyond
  documented bootstrap/open-form state.
- A compact reviewed evidence summary documents the manager command catalog,
  runtime run id and any unresolved frame-join gaps.

## Change Set
- `openspec/changes/archive/2026-06-04-add-manager-fixture-v1-runner-shell/`
- `openspec/changes/archive/2026-06-04-define-manager-fixture-v1-readonly-command-manifest/`
- `openspec/changes/archive/2026-06-04-integrate-manager-fixture-v1-capture-runner/`
- `openspec/changes/archive/2026-06-04-publish-manager-fixture-v1-evidence-reporting/`

## Verify
- `openspec validate add-manager-fixture-v1-runner-shell --strict`
- `openspec validate define-manager-fixture-v1-readonly-command-manifest --strict`
- `openspec validate integrate-manager-fixture-v1-capture-runner --strict`
- `openspec validate publish-manager-fixture-v1-evidence-reporting --strict`
- `openspec validate qa-mcp-protocol-lab --strict`
- `openspec validate --all`
- `git diff --check`
- PowerShell parser check for `tools/protocol-research/run_protocol_capture.ps1`
- manager fixture V1 dry-run and generated JSON parser checks
- reporter `py_compile`, reviewed summary JSON checks and evidence path checks

## Archive
- `openspec/changes/archive/2026-06-04-add-manager-fixture-v1-runner-shell/`
- `openspec/changes/archive/2026-06-04-define-manager-fixture-v1-readonly-command-manifest/`
- `openspec/changes/archive/2026-06-04-integrate-manager-fixture-v1-capture-runner/`
- `openspec/changes/archive/2026-06-04-publish-manager-fixture-v1-evidence-reporting/`

## Related
- `docs/protocol-research/research-plan.md`
- `docs/protocol-research/evidence/fixture-runtime/20260604-client-fixture-v1-live-open/runtime_summary.md`
- `docs/protocol-research/evidence/manager-fixture-v1-shell/20260604-manager-fixture-v1-shell/source_summary.md`
- `docs/protocol-research/evidence/manager-fixture-v1-readonly-contract/20260604-manager-fixture-v1-readonly-contract/command_catalog_summary.md`
- `docs/protocol-research/evidence/manager-fixture-v1-capture-runner/20260604-manager-fixture-v1-dryrun/runner_summary.md`
- `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/runtime_summary.md`
- `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/frame_join_report.md`
- `openspec/board/4.done/01-2026-06-04-client-fixture-v1-control-surface.md`
- `openspec/changes/archive/2026-06-04-add-manager-fixture-v1-runner-shell/`
- `openspec/changes/archive/2026-06-04-define-manager-fixture-v1-readonly-command-manifest/`
- `openspec/changes/archive/2026-06-04-integrate-manager-fixture-v1-capture-runner/`
- `openspec/changes/archive/2026-06-04-publish-manager-fixture-v1-evidence-reporting/`

## Result
Four OpenSpec changes were implemented, verified, synced to
`qa-mcp-protocol-lab` and archived. The manager-side EDT source shell and V1
read-only command contract were authored for `vanessa_manager`; the capture
runner now has a Windows-native `manager-fixture-v1-readonly` scenario,
shared run id, dry-run path and reviewed evidence/report generation.

The result is source-ready and dry-run/reporting-ready, not live-protocol
accepted. Live manager smoke remains provider/runtime-gapped because the
configured Vanessa EPF is absent, broad manager deploy was skipped after EDT
classified it as a full configuration reload, and live COM access reported the
manager platform mismatch recorded in evidence. No command is accepted as a
protocol mapping without frame ranges, dynamic fields, normalized hashes and
replay/direct Python-manager proof.

## Next
- restore the configured Vanessa EPF/runtime profile before a live manager V1
  smoke run or V2 safe-action runner work

## Publish
- Docs updated:
  `docs/protocol-research/evidence-index.md`,
  `docs/protocol-research/README.md`.
- Delivery manifest:
  `.runtime/opsx/delivery-manifests/05-2026-06-04-manager-fixture-v1-readonly-runner.json`.
- Commit: scoped publish commit created by this `$opsx-pub` run.
- Push: pushed to `origin/main`.

## Change Plan Notes
## Change 1: `add-manager-fixture-v1-runner-shell`

### Why
The manager-side harness must exist in the `manager` EDT target before it can
execute controlled TestManager API commands.

### Goal
Create the dedicated manager fixture processor/harness shell with explicit run
context, bootstrap behavior and no protocol parsing inside 1C.

### Scope
- Manager EDT project `vanessa_manager`.
- Run context fields: `run_id`, proxy TestClient port, client fixture target
  and output directory.
- Bootstrap command path that opens the client fixture and labels bootstrap
  traffic separately.
- Binding, deploy and runtime-smoke evidence planning.

### Acceptance
- `validate_project_infobase_binding(target_id="manager")` is clean before
  apply/deploy.
- The manager shell can open and smoke its bootstrap path.
- No TCP parsing, clicks, input, page switching or business writes are added.

### Depends On
- none

### Related
- `openspec/changes/add-manager-fixture-v1-runner-shell/`

### Notes For `$openspec-ff-change`
- Keep the first change focused on shell and bootstrap; read-only command
  catalog belongs to the next change.

## Change 2: `define-manager-fixture-v1-readonly-command-manifest`

### Why
Protocol captures need stable command/case ids and side-channel event records
before frame ranges can be joined or reviewed.

### Goal
Define and implement the manager V1 manifest, read-only command catalog and
event/result output contract.

### Scope
- Manifest fields for run, command, target, proxy port and expected markers.
- Read-only command catalog for client fixture V1 families.
- `case_events.jsonl` and `manager_harness_result.json`.
- Explicit rejection of actions and writes from V1 accepted commands.

### Acceptance
- Each emitted command has stable `case_id`, `command_id`, target marker and
  expected marker.
- Event records include before/after timestamps, status, result preview and
  exception details.
- V1 catalog remains read-only.

### Depends On
- `add-manager-fixture-v1-runner-shell`

### Related
- `openspec/changes/define-manager-fixture-v1-readonly-command-manifest/`

### Notes For `$openspec-ff-change`
- Seed command cases from the client fixture V1 target map and live-open
  evidence; do not promote protocol mappings here.

## Change 3: `integrate-manager-fixture-v1-capture-runner`

### Why
The manager harness must run inside the proxy/TestClient capture lifecycle so
manager events and TCP frames share one run id.

### Goal
Add a Windows-native capture-runner scenario that starts or attaches the
needed pieces, passes the proxy endpoint to the manager harness and preserves
all outputs under one runtime directory.

### Scope
- Capture runner scenario for manager fixture V1 read-only runs.
- Shared `run_id` and runtime directory.
- Proxy endpoint wiring into the manager harness.
- Bootstrap phase labeling and owned-PID cleanup.

### Acceptance
- Capture output contains proxy traffic, manager event log and 1C logs under
  one run id.
- Cleanup stops only runner-owned PIDs.
- Raw TCP data and generated runtime output remain ignored.

### Depends On
- `add-manager-fixture-v1-runner-shell`
- `define-manager-fixture-v1-readonly-command-manifest`

### Related
- `openspec/changes/integrate-manager-fixture-v1-capture-runner/`

### Notes For `$openspec-ff-change`
- Preserve Windows-native PowerShell behavior and existing capture runner
  safety rules.

## Change 4: `publish-manager-fixture-v1-evidence-reporting`

### Why
Raw captures and full logs are not reviewable; manager V1 needs compact
evidence that documents command coverage and unresolved frame-join gaps.

### Goal
Publish reviewed manager V1 evidence summaries and frame-join reports without
claiming accepted protocol mappings prematurely.

### Scope
- Compact manager V1 runtime summary.
- Per-case frame/chunk join status or unresolved reason.
- Evidence index and protocol research doc links.
- Explicit acceptance boundary for future normalizer/replay work.

### Acceptance
- Reviewed evidence documents run id, command catalog, runtime outputs and
  unresolved gaps.
- Raw captures remain outside reviewed changes.
- No mapping is accepted without frame ranges, dynamic-field normalization and
  replay/direct Python-manager evidence.

### Depends On
- `add-manager-fixture-v1-runner-shell`
- `define-manager-fixture-v1-readonly-command-manifest`
- `integrate-manager-fixture-v1-capture-runner`

### Related
- `openspec/changes/publish-manager-fixture-v1-evidence-reporting/`

## Log
- 2026-06-04T16:47:33Z card created
- 2026-06-04T17:40:00Z decomposed into four OpenSpec changes and moved to `2.todo`
- 2026-06-04T18:20:00Z archived `add-manager-fixture-v1-runner-shell`
- 2026-06-04T18:47:00Z archived `define-manager-fixture-v1-readonly-command-manifest`
- 2026-06-04T18:58:00Z archived `integrate-manager-fixture-v1-capture-runner`
- 2026-06-04T19:07:00Z archived `publish-manager-fixture-v1-evidence-reporting`
- 2026-06-04T19:08:04Z moved card to `4.done`
- 2026-06-04T19:20:00Z publish docs reviewed and final scoped verification started
