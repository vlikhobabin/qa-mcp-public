# Protocol Corpus Runner

`tools/protocol-research/protocol_corpus_runner.py` builds marked read-only
protocol corpus evidence from a TestManager/TestClient capture.

The runner can either analyze an existing capture or delegate a fresh Windows
capture to `tools/protocol-research/run_protocol_capture.ps1` with
`--run-capture`. In both modes, raw traffic stays under ignored
`runtime/protocol-research/` paths. Reviewed evidence is written under
`docs/protocol-research/evidence/corpus/`.

## Seeded Case Manifest

When no custom manifest is supplied, the runner uses the `readonly-smoke`
matrix by default:

| Case | API surface | Manager frames | Replay expectation |
| --- | --- | --- | --- |
| `active-window-context` | `TestedApplication.GetActiveWindow` and active window read-only properties | `8..11` | direct Python probe |
| `active-form-context` | `TestedApplication.GetActiveForm` and `TestedForm` metadata | `12..17` | direct Python probe |
| `form-element-details` | `TestedForm` form-element read-only property probes | `101..106` | direct Python probe |

The `expanded-readonly` seeded matrix keeps those smoke rows and adds a
family-labeled read-only element matrix. Families that are not exposed by the
current active form are emitted as explicit `unsupported` gap rows with no
frame range, so the reviewed evidence shows fixture coverage gaps instead of
silently dropping them.

Current `expanded-readonly` families:

| Family | Case behavior |
| --- | --- |
| `EditField` | Supported through the current form-element detail frames and direct Python probe. |
| `Button` | Unsupported fixture gap in the current sales dashboard form. |
| `Table` | Unsupported fixture gap in the current sales dashboard form. |
| `CommandBar` | Unsupported fixture gap in the current sales dashboard form. |
| `Page` | Unsupported fixture gap in the current sales dashboard form. |
| `Label` | Unsupported fixture gap in the current sales dashboard form. |
| `CheckBox` | Unsupported fixture gap in the current sales dashboard form. |

A custom JSON manifest may define `case_id`, `scenario`, `api_call`,
`ui_target`, `expected_state`, `safety_class`, `replay_expectation` and
`frame_range`. `frame_range` can contain direction-specific `manager_to_client`
and `client_to_manager` ranges, or just `from` and `to` manager frame numbers.
Manifest rows may also define `element_family`, `availability` and
`expected_response_markers`; `frame_range: null` is reserved for explicit
unsupported or pending fixture gaps.

Safe UI action manifests use `safety_class: safe_ui_action` and may also define
the V2 manifest gate fields `action_id`, `target_id`, `target_marker`,
`pre_state`, `action`, `post_state`, `recovery_expectation`,
`mutates_business_data=false`, `allowed_action_family` and
`expected_action_result_markers`. Tooling rejects rows with unsupported action
families or missing required fields before capture or reporting. Evidence rows
may also define `action_result_markers`, `action_frame_range` and
`background_frame_ranges`. `action_frame_range` identifies the candidate frames
for the non-mutating UI action; `background_frame_ranges` keeps active-window,
active-form, idle or refresh traffic visible without treating those frames as
proof of the action.

V4 dialog manifests use `safety_class: fixture_dialog` and keep the same
fail-closed pre/action/post/recovery shape. Rows must define
`dialog_scenario_id`, `scenario_family`, `target_marker`, `dialog_family`,
`dialog_lifecycle`, `expected_text_marker`,
`expected_dialog_result_marker`, `mutates_business_data=false` and
`expected_action_result_markers`. `expected_error` rows additionally require
`expected_diagnostic_marker`, while bounded wait rows additionally require
`bounded_duration_ms`. V4 rows remain candidate-only until reviewed runtime
evidence isolates dialog/action, background and recovery phases and then proves
the same scenario through replay, direct Python-manager probe or accepted typed
contract evidence.

## Controlled Fixture Plan

The current planned fixture manifest for missing read-only families is:

`docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/fixture_case_manifest.json`

The current V1 client fixture target map for the authored control surface is:

`docs/protocol-research/evidence/fixture-target-maps/20260604-client-fixture-v1-target-map/target_map.json`

It defines pending `Button`, `Table`, `CommandBar`, `Page`, `Label` and
`CheckBox` rows with read-only API intent, expected markers and no frame
range. These rows are planning inputs only. A row can move from `pending` to
accepted corpus evidence only after a Windows-native fixture run produces
compact evidence with frame range, normalized hash, dynamic fields, operation
token, response markers and replay or direct Python-manager status.

The V1 target map links the pending fixture families to concrete `PF_*`
source markers in the client fixture processor. Its rows are semantic/source
targets only; they do not replace live form-analysis output or wire evidence.

EDT authoring output, infobase exports, raw captures and runtime logs for
fixture runs stay outside git under ignored `.artifacts/` or
`runtime/protocol-research/` paths. Reviewed documentation links compact
summaries from `docs/protocol-research/evidence/fixture-plans/`,
`docs/protocol-research/evidence/fixture-target-maps/`,
`docs/protocol-research/evidence/corpus/` and
`docs/protocol-research/evidence/python-manager-probe/`.

The first live fixture-manifest run is:

`docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/`

It used the planned manifest with a Windows-native `form-analysis` capture and
produced six fixture rows. Every fixture row remains non-accepted:

| Family | Case id | Published status | Reason |
| --- | --- | --- | --- |
| `Button` | `fixture-button-readonly` | `pending` / `incomplete_hash` | Runner cannot target a source-candidate fixture form; no request frames or hash |
| `Table` | `fixture-table-readonly` | `pending` / `incomplete_hash` | Runner cannot target a source-candidate fixture form; no request frames or hash |
| `CommandBar` | `fixture-commandbar-readonly` | `pending` / `incomplete_hash` | Runner cannot target a source-candidate fixture form; no request frames or hash |
| `Page` | `fixture-page-readonly` | `pending` / `incomplete_hash` | Runner cannot target a source-candidate fixture form; no request frames or hash |
| `Label` | `fixture-label-readonly` | `pending` / `incomplete_hash` | Runner cannot target a source-candidate fixture form; no request frames or hash |
| `CheckBox` | `fixture-checkbox-readonly` | `pending` / `incomplete_hash` | Runner cannot target a source-candidate fixture form; no request frames or hash |

Classification evidence:
`docs/protocol-research/evidence/corpus-comparison/fixture-readonly-20260603-085618/`.
Accepted-mapping output:
`docs/protocol-research/evidence/accepted-mappings/fixture-readonly-20260603-085618/`,
with no accepted case ids.

## Manager Fixture V1 Live Join

The current industrial-format manager fixture route uses
`manager-fixture-v1-readonly` as a live capture scenario. In this mode the
manager harness, not Vanessa smoke probes, is the primary source of case
commands. The harness reads the generated `manager_harness_manifest.json`,
connects to the proxied TestClient, executes the manifest commands and writes
`case_events.jsonl` plus `manager_harness_result.json` next to the raw
`traffic.jsonl`.

`protocol_corpus_runner.py --capture-scenario manager-fixture-v1-readonly`
can delegate the live capture and publish the basic manager fixture live-join
evidence under:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/<capture-id>/`

For accepted mappings, publish with `report_manager_fixture_v1.py` and pass
each retained replay/probe summary explicitly:

```powershell
python tools\protocol-research\report_manager_fixture_v1.py `
  --run-dir runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup `
  --output-dir docs\protocol-research\evidence\manager-fixture-v1-live-join\20260606-pending-promotion-final-readiness `
  --replay-probe-summary docs\protocol-research\evidence\manager-fixture-v1-replay-probe\20260606-cleanup-readonly-fields\summary.json `
  --replay-probe-summary docs\protocol-research\evidence\manager-fixture-v1-replay-probe\20260606-cleanup-commandbar-main\summary.json `
  --replay-probe-summary docs\protocol-research\evidence\manager-fixture-v1-replay-probe\20260606-cleanup-summary419-uipath\summary.json `
  --replay-probe-summary docs\protocol-research\evidence\manager-fixture-v1-replay-probe\20260606-pending-missing-proof-runtime-gap\summary.json
```

The manager fixture report accepts a row only when the replay/probe evidence
matches the joined `case_id`, manager frame range and `normalized_hash`. Joined
frame evidence without replay/probe proof remains pending.

Current cleanup state:

| Status | Count |
| --- | ---: |
| Joined command windows | 17 |
| Accepted replay/probe rows | 8 |
| Promoted by pending-promotion pass | 0 |
| Pending rows | 9 |

Accepted rows:

- `tm-v1-active-window`
- `tm-v1-active-form`
- `tm-v1-diag-window-find-field-marker`
- `tm-v1-diag-form-find-field-marker`
- `tm-v1-field-version`
- `tm-v1-field-string`
- `tm-v1-commandbar-main`
- `tm-v1-pages-main`

Pending rows:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`
- `tm-v1-diag-window-find-form-marker`
- `tm-v1-diag-window-get-form-path`
- `tm-v1-form-summary`
- `tm-v1-checkbox-true`
- `tm-v1-button-inert`
- `tm-v1-table-items`
- `tm-v1-group-main`

Pending-row classification:

`docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Pending-row probe review:

`docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-readonly-review/`

Final pending-promotion readiness:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-promotion-final-readiness/`

The pending-promotion pass does not add accepted rows. It preserves precise
blockers under the missing-proof runtime-gap, broad-range isolation and
marker-contract evidence directories, and records that V2 live safe-action
acceptance was blocked at that stage until runtime proof or an explicit
residual-risk decision existed.

Follow-up after runtime restore and marker-contract correction:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-promote-candidate-marker-contracts-focused-proof-accepted/`

The follow-up focused proof selects active-window plus the nine formerly
pending rows. It accepts six former pending rows and initially leaves three
blocked.

Second follow-up for typed side-channel count contracts:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-count-contracts-focused-proof/`

The side-channel count proof accepts `tm-v1-diag-command-interface-dump` and
`tm-v1-diag-window-children` via
`manager_case_event.after.result_preview`.

Third follow-up for the typed side-channel form-path contract:

`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-form-path-focused-proof/`

The side-channel form-path proof accepts `tm-v1-diag-window-get-form-path` via
`manager_case_event.after.result_preview` marker `form_path_attempted=`.
After this proof, all nine formerly pending manager fixture V1 readonly rows
have accepted contract-backed mappings. The three side-channel rows remain
manager result-preview evidence, not direct wire marker observations.

## Manager Fixture V2 Safe-Action Tooling

The V2 safe-action path is intentionally separate from
`manager-fixture-v1-readonly`. It starts with offline manifest validation and
phase-aware dry-run output while the manager fixture V2 action runner is still
gated.

The reviewed manager-side catalog for the runner is:

`tools/protocol-research/manager_fixture_v2_safe_action_catalog.json`

It embeds `safe_action_targets` so validation can fail closed on missing target
ids, marker mismatches, unsupported target status and action families outside a
target's allowlist. Unsupported, blocked and rejected rows stay visible with
owner, reason and residual risk, but only executable rows are emitted into the
manager harness manifest.

Validate a reviewed manifest row set:

```powershell
python tools\protocol-research\v2_safe_action_tooling.py validate `
  --manifest tools\protocol-research\manager_fixture_v2_safe_action_catalog.json `
  --output-dir runtime\protocol-research\captures\v2-safe-action-validation-dry-run `
  --write-phase-events `
  --require-executable
```

Run the Windows-native capture wrapper in dry-run mode:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File tools\protocol-research\run_protocol_capture.ps1 `
  -Scenario manager-fixture-v2-safe-action `
  -DryRun `
  -RunId v2-safe-action-dry-run `
  -SafeActionManifestPath tools\protocol-research\manager_fixture_v2_safe_action_catalog.json
```

The dry run writes side-channel phase events for `pre_read`, `action_start`,
`action_end`, `post_read`, `recovery`, `recovery_read` and `background`
phases under
`runtime/protocol-research/captures/<run-id>/`. It does not start 1C and does
not inject markers into TCP traffic. The dry run also writes
`safe_action_runner_results.jsonl` with typed fail-closed dispatcher outcomes:
`success`, `blocked`, `unsupported`, `partial`, `timeout` or `rejected`.
`success` means the validated row passed the offline dispatcher and remains
candidate-only; it includes the expected recovery result markers and dry-run
rerun determinism contract, but it is not live action proof. Live
`manager-fixture-v2-safe-action` capture remains fail-closed until reviewed
manager/Vanessa execution evidence is available.

Publish compact V2 report rows from a dry-run or later live run:

```powershell
python tools\protocol-research\report_manager_fixture_v2_safe_action.py `
  --run-dir runtime\protocol-research\captures\v2-safe-action-dry-run `
  --output-dir docs\protocol-research\evidence\manager-fixture-v2-safe-action\v2-safe-action-dry-run
```

V2 report rows preserve `candidate`, `pending`, `unsupported`, `blocked`,
`partial`, `timeout` and `rejected` states with reason fields. A row reaches
accepted mapping output only after comparison sees a stable normalized hash,
action-frame evidence, action result markers and compact replay/probe or typed
contract proof.

## Outputs

Runtime output next to the capture:

- `case_manifest.json` - selected cases, source capture and raw-output policy;
- `case_events.jsonl` - `case_start`, `case_step`, `case_result` and
  `case_end` side-channel events with chunk counters and derived frame ranges.
  Safe UI action rows add `action_start` and `action_end` events with
  transition fields and action result markers.

Reviewed evidence output:

- `corpus_cases.jsonl` - normalized rows following
  `docs/protocol-research/corpus-evidence-contract.md`;
- `corpus_summary.json` - capture id, case ids, status counts and evidence
  paths;
- `corpus_report.md` - compact Markdown summary for the evidence index.

The runner does not inject markers into the TCP stream. Case markers are
derived side-channel events correlated with proxy chunk counters and
timestamps.

## Repeatability Comparison

`tools/protocol-research/compare_corpus_runs.py` compares two or more reviewed
`corpus_cases.jsonl` inputs without reading raw TCP payloads. Inputs can be
evidence directories or direct `corpus_cases.jsonl` paths.

The comparison groups rows by `case_id` and reports:

- capture ids, evidence paths and replay statuses;
- effective replay statuses after optional compact direct-probe evidence is
  applied;
- before-hash sets from tail-stripped request bytes before replacements;
- stable versus divergent `normalized_hash` values;
- request/response sizes, operation token sets, response markers and dynamic
  field replacement summaries;
- missing cases, incomplete hashes and unsupported fixture gaps.
- precise reason values and provider-owner routing for unresolved element hash
  gaps when supporting request-hash evidence is supplied.
- safe action status, action frame ranges, background refresh ranges and
  action result marker sets for `safe_ui_action` rows.

`stable` is reserved for rows that have the same non-null normalized hash in
every input and accepted replay/probe status. Rows with matching hashes but
non-accepted replay status stay visible as `non_accepted`.

Safe action rows use the action contract classifications `accepted`,
`pending`, `unsupported`, `partial`, `timeout`, `rejected` or `blocked`.
`accepted` requires reviewed action-frame evidence, a non-null stable
normalized hash, action result markers and accepted replay or direct
Python-manager proof for the same non-mutating action. Rows without those
proofs remain visible in comparison output and are kept out of accepted
mapping reports.

Use `--probe-evidence <python_manager_probe_result.json>` to attach compact
direct Python-manager evidence during comparison. When `--accepted-output-dir`
is supplied, the tool also writes an accepted-mapping evidence report for rows
that have both repeated stable hashes and accepted probe/replay evidence.
Rows with accepted probe output but missing request hashes remain visible as
`incomplete_hash`.

Use `--request-hash-evidence <request_hashes.json>` to attach compact reviewed
element request-hash evidence for gap classification. This does not promote a
row by itself; it adds stable `precise_reasons` such as
`accepted_reviewed_hash`, `missing_request_frames` or
`ambiguous_operation_join` and routes provider ownership for the next pass.

When `--normalizer-output-dir` is supplied, the comparison also writes compact
normalizer evidence with before/after hash counts, accepted replacement names,
preserved fields and ambiguous fields. The current normalizer preserves
`operation_token` in the normalized hash; it is reported as a preserved
semantic token until evidence proves it can be replaced safely.

## Direct Probe Acceptance

Direct Python-manager probing can promote a repeated read-only row only when
the reviewed corpus row links compact probe evidence and the probe confirms
the same operation shape. A stable `normalized_hash` by itself is not enough
for acceptance.

Accepted probe-backed rows should keep:

- the repeated capture ids and frame ranges used for the request hash;
- the accepted probe evidence path under
  `docs/protocol-research/evidence/python-manager-probe/` or a later compact
  evidence directory;
- the probe query or case family;
- expected and observed response markers;
- any unresolved limitation in `notes`.

Rows with useful probe output but no reviewed request-frame hash remain
non-accepted. Comparison reports should keep them visible as
`incomplete_hash`, `partial`, `pending` or another explicit unresolved class
instead of silently promoting them.

## Example

```powershell
python tools\protocol-research\protocol_corpus_runner.py `
  --capture-dir 20260602-084433 `
  --probe-result runtime\protocol-research\python-manager-probe\infra-check-20260602-161326\python_manager_probe_result.json
```

```powershell
python tools\protocol-research\protocol_corpus_runner.py `
  --capture-dir 20260602-172319 `
  --case-set expanded-readonly `
  --probe-result runtime\protocol-research\python-manager-probe\corpus-20260602-172319\python_manager_probe_result.json
```

```powershell
python tools\protocol-research\compare_corpus_runs.py `
  docs\protocol-research\evidence\corpus\20260602-193802-expanded-readonly `
  docs\protocol-research\evidence\corpus\20260602-195407-expanded-readonly `
  --comparison-id expanded-readonly-20260602-193802-vs-20260602-195407 `
  --normalizer-output-dir docs\protocol-research\evidence\normalizer\expanded-readonly-20260602-193802-vs-20260602-195407
```

```powershell
python tools\protocol-research\compare_corpus_runs.py `
  docs\protocol-research\evidence\corpus\20260602-193802-expanded-readonly `
  docs\protocol-research\evidence\corpus\20260602-195407-expanded-readonly `
  --comparison-id expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted `
  --probe-evidence docs\protocol-research\evidence\python-manager-probe\expanded-20260602-193802\python_manager_probe_result.json `
  --accepted-output-dir docs\protocol-research\evidence\accepted-mappings\expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted
```

```powershell
python tools\protocol-research\compare_corpus_runs.py `
  docs\protocol-research\evidence\corpus\20260602-193802-expanded-readonly `
  docs\protocol-research\evidence\corpus\20260602-195407-expanded-readonly `
  --probe-evidence docs\protocol-research\evidence\python-manager-probe\expanded-20260602-193802\python_manager_probe_result.json `
  --request-hash-evidence docs\protocol-research\evidence\readonly-element-request-hashes\20260602-172319-expanded-extracted\request_hashes.json `
  --comparison-id readonly-element-hash-resolution-20260603-extracted
```

```powershell
python tools\protocol-research\compare_corpus_runs.py `
  docs\protocol-research\evidence\corpus\20260603-134132-safe-action `
  --comparison-id safe-action-20260603-134132 `
  --accepted-output-dir docs\protocol-research\evidence\accepted-mappings\safe-action-20260603-134132
```
