# Protocol Research Status Report - 2026-06-06

> **⚠ HISTORICAL (2026-06-06) — superseded.** A mid-research snapshot (manager fixture V1 read-only corpus route),
> kept for provenance. "Current snapshot" below is as of 2026-06-06 only. For current state see
> `../qa-mcp-tool-reference.md` + `../program-102-native-superset-handoff.md` and the README banner.

This report is the current project snapshot for the manager fixture V1
read-only corpus route. The older `status-report-2026-06-03.md` remains the
historical replacement-readiness baseline.

## Verdict

The project is ready for controlled industrial-format protocol research on the
manager fixture V1 route: a manifest-driven manager harness can drive the
TestClient through the proxy, emit side-channel command events, and publish a
frame-join report from `case_events.jsonl` plus `traffic.jsonl`.

Current V2 readiness state: manager fixture V1 read-only no longer has a
pending-row gap blocking V2 safe-action planning. The final readiness label for
this V1 gap is `unblocked_by_v1_readonly`.

Historical baseline context: the initial cleanup run accepted replay/probe
proof for 8 of 17 joined rows. A first pending-promotion pass promoted 0 of the
remaining 9 rows while the focused runtime endpoint was unavailable. The
follow-up proofs below supersede that baseline blocker for current V2 planning.

## Follow-up After Runtime Restore And Contract Corrections

The runtime endpoint was restored later on 2026-06-06 and a focused proof was
run after promoting five candidate marker contracts in the manager fixture V1
manifest/catalog. The focused proof selected active-window plus the nine
formerly pending rows:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-promote-candidate-marker-contracts-focused-proof-accepted/`

Result:

| Metric | Value |
| --- | ---: |
| Focused commands | 10 |
| Joined command windows | 10 |
| Accepted by marker proof | 6 |
| Remaining former pending rows after marker proof | 3 |

Accepted former pending rows:

- `tm-v1-diag-window-find-form-marker`
- `tm-v1-form-summary`
- `tm-v1-checkbox-true`
- `tm-v1-button-inert`
- `tm-v1-table-items`
- `tm-v1-group-main`

Rows that still needed follow-up after marker proof:

- `tm-v1-diag-window-get-form-path`

The two diagnostic count rows were then accepted by a second focused proof
using typed manager side-channel contracts:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-count-contracts-focused-proof/`

| Metric | Value |
| --- | ---: |
| Focused count commands | 2 |
| Joined command windows | 2 |
| Accepted side-channel count rows | 2 |
| Remaining former pending rows | 1 |

Accepted side-channel rows:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`

The count rows are accepted as `manager_case_event.after.result_preview`
evidence, not as direct wire marker observations.

The remaining form-path diagnostic row was then accepted by a third focused
proof using the same typed side-channel contract class:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-form-path-focused-proof/`

| Metric | Value |
| --- | ---: |
| Focused form-path commands | 1 |
| Joined command windows | 1 |
| Accepted side-channel form-path rows | 1 |
| Remaining former pending rows | 0 |

Accepted side-channel form-path row:

- `tm-v1-diag-window-get-form-path`

This row is accepted as `manager_case_event.after.result_preview` evidence for
`form_path_attempted=`, not as a direct wire marker observation.

## Current Evidence

Primary live capture:

`runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`

Published live-join evidence:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Final pending-promotion publication:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-promotion-final-readiness/`

Replay/probe evidence folded into the live-join report:

- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-readonly-fields/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-commandbar-main/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-summary419-uipath/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/`

Pending-row classification evidence:

`docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Pending-promotion blocker evidence:

- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-readonly-runtime-preflight/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-ambiguous-range-isolation/`
- `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/`

Focused follow-up proof evidence:

- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-promote-candidate-marker-contracts-focused-proof-accepted/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-count-contracts-focused-proof/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-form-path-focused-proof/`

Baseline cleanup live-join counts:

| Metric | Value |
| --- | ---: |
| Manifest commands | 17 |
| Joined command windows | 17 |
| Accepted replay/probe rows | 8 |
| Promoted by pending-promotion pass | 0 |
| Pending rows | 9 |

## Baseline Accepted Rows

The baseline cleanup accepted protocol mappings were:

- `tm-v1-active-window`
- `tm-v1-active-form`
- `tm-v1-diag-window-find-field-marker`
- `tm-v1-diag-form-find-field-marker`
- `tm-v1-field-version`
- `tm-v1-field-string`
- `tm-v1-commandbar-main`
- `tm-v1-pages-main`

Acceptance currently requires the replay/probe summary to match the joined
`case_id`, manager frame range and `normalized_hash`. Joined frame evidence
alone is intentionally not enough.

## Baseline Pending Rows

The baseline cleanup pending rows were:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`
- `tm-v1-diag-window-find-form-marker`
- `tm-v1-diag-window-get-form-path`
- `tm-v1-form-summary`
- `tm-v1-checkbox-true`
- `tm-v1-button-inert`
- `tm-v1-table-items`
- `tm-v1-group-main`

All pending rows now have retained blocker evidence and a next route. The
diagnostic count rows are blocked by the missing focused TestClient endpoint.
The form-marker and form-summary rows need current-run endpoint/marker-contract
proof before their expected markers can change. The form-path and button rows
remain blocked by broad frame windows that were not isolated. The checkbox,
table and group rows already return useful target or structural markers, but
their endpoint semantics are still not independently proven. No additional row
was accepted by the pending-promotion pass.

The follow-up proofs above supersede this baseline pending list for current
planning: all nine rows are now accepted by contract-backed evidence. Six are
accepted by marker-contract focused proof, and three diagnostic rows are
accepted by typed manager side-channel contracts.

## Tooling State

The current route is:

1. `tools/protocol-research/run_protocol_capture.ps1 -Scenario manager-fixture-v1-readonly`
   starts a Windows-native capture, launches the manager harness as the primary
   command source, and writes `manager_harness_manifest.json`,
   `case_events.jsonl`, `manager_harness_result.json` and `traffic.jsonl`.
2. `tools/protocol-research/protocol_corpus_runner.py --capture-scenario manager-fixture-v1-readonly`
   can delegate the live capture and publish the basic manager fixture
   live-join evidence directory.
3. `tools/protocol-research/report_manager_fixture_v1.py` publishes compact
   reviewed evidence and accepts repeated `--replay-probe-summary` inputs to
   promote rows that have matching replay/probe proof.
4. `tools/protocol-research/replay_probe.py` replays captured manager frames
   against a fresh TestClient and records compact accepted/non-accepted
   summaries under `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/`.

The machine-readable automated-testing API inventory now exists under
`docs/protocol-research/api-inventory/automated-testing-8.3.27.1786.json` and
is planning input for corpus expansion. It does not replace wire evidence.

## Dynamic Protocol Rules Retained

The current replay evidence retains these adaptation rules:

- session ACK GUID adaptation after manager frame 3;
- frame 4 and frame 5 GUID replacement;
- frame 5 random-block replacement;
- range-sensitive binary random-block adaptation for object-resolution frames;
- GUID-only binary adaptation for later value/collection frames where block
  replacement would break replay;
- raw UI path GUID replacement for `MainFrame[...]`, `SecondaryFrame[...]` and
  `ManagedForm[...]`.

The important current constraint is that binary random-block replacement is
not globally safe across all frames. The accepted field, command-bar and pages
evidence uses narrower frame ranges for block replacement and broader GUID
replacement for session/form identity.

## V2 Readiness

Manager fixture V1 no longer has a pending-row gap blocking V2 safe-action
work. The final readiness state for this V1 gap is `unblocked_by_v1_readonly`.
V2 fixture planning can move to a separate safe-action proof, with the boundary
that the three diagnostic side-channel rows are not direct wire marker claims.

## V2 Boundary

V1 read-only readiness unblocks V2 planning only. It does not accept any V2
safe-action protocol mapping by inference.

The next route is to define and enforce the V2 safe-action contract before any
safe-action fixture or manager runner work executes actions:

- document a fail-closed safe-action manifest with `mutates_business_data=false`;
- allow only non-mutating fixture-local families such as focus/activation,
  existing window/form activation, fixture page switching, local table row
  selection and menu/group expand-collapse without command execution;
- keep text input, value toggles, business command clicks, object writes,
  save/post/delete/fill/import/export and external side effects outside V2;
- require every V2 action row to produce its own pre-state, action, post-state,
  recovery, action frame range, response markers, action result markers and
  replay or direct Python-manager proof before acceptance.
