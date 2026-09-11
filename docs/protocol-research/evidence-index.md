# Evidence Index

This index lists compact protocol research evidence. Some entries were
imported from the original `vanessa-mcp` runtime; newer entries were produced
in this repository. Full raw captures stay outside git under
`runtime/protocol-research/`.

## Capture `20260602-084433`

Path: `docs/protocol-research/evidence/captures/20260602-084433/`

What it proves:

- A complete Vanessa manager to TestClient session was captured.
- The capture contains 106 manager-to-client chunks and 107
  client-to-manager chunks.
- It is the baseline source for generated manager templates and replay probes.

Included files:

- `analysis.md`
- `capture_manifest.json`
- `capture_summary.json`

## Request Series `18..30`

Path:
`docs/protocol-research/evidence/captures/20260602-084433/request-series-18-30/`

What it proves:

- Frames `18..30` form a repeated managed-form reference request family.
- Normalization over ACK GUID, sequence, nonce and ManagedForm GUID produces a
  stable canonical hash for the request shape.

Included files:

- `request_series.md`
- `request_series.json`

## Request Series `101..106`

Path:
`docs/protocol-research/evidence/captures/20260602-084433/request-series-101-106/`

What it proves:

- Frames `101..106` contain element-detail request families.
- Operation token at offset `51` is echoed in responses at offset `13`.
- The observed operations split into three semantic labels for two chart
  elements.

Included files:

- `request_series.md`
- `request_series.json`

## Replay `20260602-150229`

Path:
`docs/protocol-research/evidence/captures/20260602-084433/replay/20260602-150229/`

What it proves:

- Generated manager frames can replay the `101..106` element-detail family
  against a live TestClient after session bootstrap.
- The replayed request family keeps the same normalized classification.

Included files:

- `request-series-101-106/request_series.md`
- `request-series-101-106/request_series.json`

## Manager Frame Templates

Path:
`docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/`

What it proves:

- Manager frames can be represented as templates with dynamic fields:
  ACK GUID, sequence, nonce and ManagedForm GUID in ASCII/UTF-16LE forms.
- The template set is the current input for `python_manager_client.py` and
  replay probes.

Included files:

- `manager_frame_templates.md`
- `manager_frame_templates.json`

## Python Manager Probe

Path:
`docs/protocol-research/evidence/python-manager-probe/short-element-details-20260602-151206/`

What it proves:

- Python code can talk directly to TestClient for the short
  `form-element-details` schedule.
- It can retrieve active form metadata and element details without running a
  1C TestManager instance.

Included files:

- `python_manager_probe_result.json`
- `probe_manifest.json`

## Infrastructure Check `20260602-161326`

Path:
`docs/protocol-research/evidence/infrastructure-checks/20260602-161326/`

What it proves:

- The qa-mcp local target env satisfies the current Vanessa TestClient
  bootstrap contract with `TEST_CLIENT_BOOTSTRAP_MODE=ensure-profile`.
- A fresh `connect-only` Vanessa run can route TestManager/TestClient traffic
  through the TCP proxy and preserve a short capture.
- The direct Python manager prototype can still query a live TestClient without
  a 1C TestManager instance.

Included files:

- `infra_check.md`

## Semantic Source Readiness `20260603-opsx-do-semantic-sources`

Path:
`docs/protocol-research/evidence/semantic-sources/20260603-opsx-do-semantic-sources/`

What it proves:

- The semantic-source inventory was applied using compact evidence only.
- `help-mcp`, `meta-mcp` and legacy `edt-mcp` readiness is referenced from the
  2026-06-02 infrastructure check instead of copying raw provider output.
- The current AI1C profile preflight recorded unproxied provider telemetry
  gaps, including the expected Vanessa gap, without blocking this docs-only
  source inventory.

Included files:

- `source_readiness.md`

## Semantic Mapping `20260603-opsx-do-semantic-mapping`

Path:
`docs/protocol-research/evidence/semantic-mapping/20260603-opsx-do-semantic-mapping/`

What it proves:

- Current expanded-readonly corpus case ids are linked to compact semantic
  help/meta references without rewriting historical corpus rows.
- `active-form-context` maps to `Report.ДашбордПродажи.Form.ФормаОтчета`
  while preserving runtime managed-form GUIDs as protocol evidence.
- `EditField` rows remain partial for metadata element identity, and the
  `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox` families
  remain explicit fixture gaps.

Included files:

- `semantic_map.md`
- `source_summary.md`

## Fixture Plan `20260603-opsx-do-readonly-fixtures`

Path:
`docs/protocol-research/evidence/fixture-plans/20260603-opsx-do-readonly-fixtures/`

What it proves:

- Missing `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox`
  families have explicit planned read-only corpus cases instead of being
  silently omitted.
- The planned fixture source, expected markers, provider owners, evidence
  paths and safety boundaries are recorded before any live capture is accepted.
- EDT authoring output, generated validation output and raw fixture captures
  remain outside git; only compact planning summaries are reviewed here.

Included files:

- `fixture_plan.md`
- `fixture_case_manifest.json`
- `source_summary.md`

## Fixture Source Readiness `20260603-opsx-do-readonly-fixture-source`

Path:
`docs/protocol-research/evidence/fixture-sources/20260603-opsx-do-readonly-fixture-source/`

What it proves:

- The external EDT source boundary
  `C:\1C_BASES\EDT\demo10413\demo10413` exists locally and was scanned
  read-only without committing source payloads.
- The scan found static source candidates for `Button`, `Table`,
  `CommandBar`, `Page`, `Label` and `CheckBox`; three form files contain all
  six family markers.
- Family readiness remains `partial_source_candidate` until live TestClient
  form-open and wire evidence target one of the candidate forms.

Included files:

- `source_summary.md`
- `source_scan.json`

## Fixture Target Map `20260604-client-fixture-v1-target-map`

Path:
`docs/protocol-research/evidence/fixture-target-maps/20260604-client-fixture-v1-target-map/`

What it proves:

- The authored V1 client fixture source has a reviewed semantic target map for
  `PF_*` form shell, edit field, checkbox, choice, button, command bar, table,
  row, label, group and page markers.
- The map links V1 targets to planned read-only case ids while preserving the
  corpus evidence gate: live form analysis, frame range, normalized hash,
  dynamic fields and replay or direct Python-manager status are still required
  before any row can be accepted.
- Runtime form-open and Vanessa marker coverage remain deferred because the
  fixture source was not applied to the client infobase in this change.

Included files:

- `target_map.json`
- `target_map_summary.md`

## Fixture Target Map `20260607-client-fixture-v2-safe-action-target-map`

Path:
`docs/protocol-research/evidence/fixture-target-maps/20260607-client-fixture-v2-safe-action-target-map/`

What it proves:

- The client fixture V2 safe-action surface is documented as a reviewed
  target-map publication boundary.
- The publication names the local state markers, allowlisted action families
  and reset hook that downstream V2 work must use.
- It is documentation-only and does not claim live runtime acceptance,
  replay proof or direct Python-manager confirmation.

Included files:

- `target_map_summary.md`

## Manager Fixture V2 Safe-Action `20260607-candidate-dry-run`

Path:
`docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-candidate-dry-run/`

What it proves:

- The manager fixture V2 safe-action catalog, dispatcher, boundary and recovery
  contracts can publish compact candidate rows without committing raw runtime
  output.
- The publication contains seven reviewed rows: five validated runner-smoke
  successes, one blocked row and one rejected row.
- `accepted_count` is `0`; rows remain candidate, blocked or rejected because
  there is no accepted replay/probe or typed contract proof and no joined
  action frame hash.
- Recovery result markers and dry-run rerun determinism are retained as
  side-channel contract evidence only, not live action proof.

Included files:

- `safe_action_report.md`
- `safe_action_report.json`
- `corpus_cases.jsonl`
- `runtime_summary.json`
- `runtime_summary.md`

## Corpus Comparison `manager-fixture-v2-safe-action-20260607-candidate-dry-run`

Path:
`docs/protocol-research/evidence/corpus-comparison/manager-fixture-v2-safe-action-20260607-candidate-dry-run/`

What it proves:

- The candidate evidence comparison keeps all seven rows non-accepted:
  five `pending`, one `blocked` and one `rejected`.
- Missing action frame ranges, request frames, safe-action hashes and
  replay/probe proof remain visible as precise follow-up reasons.
- Raw captures and generated replay payloads are not copied into reviewed docs.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

## Accepted Mappings `manager-fixture-v2-safe-action-20260607-candidate-dry-run`

Path:
`docs/protocol-research/evidence/accepted-mappings/manager-fixture-v2-safe-action-20260607-candidate-dry-run/`

What it proves:

- Accepted safe-action mapping output was generated for the publication gate.
- `accepted_case_ids` is empty because candidate rows lack accepted replay,
  direct probe or typed contract proof with stable action-frame evidence.

Included files:

- `accepted_mappings.md`
- `accepted_mappings.json`

## Manager Fixture V2 Safe-Action `20260607-first-focused-live-action-frame-join`

Path:
`docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/`

What it proves:

- A Windows-native focused live run executed two reviewed non-mutating V2
  safe-action rows:
  `safe-switch-fixture-page-b` and `safe-focus-existing-edit-string`.
- The run retained 12 phase events: `pre_read`, `action_start`, `action_end`,
  `post_read`, `recovery` and `recovery_read` for both rows.
- The compact report separates action, background and recovery frame ranges and
  records request/response sizes, dynamic-field metadata and normalized hash
  candidates.
- Both rows remain candidate because replay/probe or accepted typed contract
  proof is not retained.

Included files:

- `safe_action_report.md`
- `safe_action_report.json`
- `corpus_cases.jsonl`
- `runtime_summary.json`
- `runtime_summary.md`
- `frame_isolation_summary.md`

## Manager Fixture V2 Safe-Action Proof Decision `20260607-first-focused-proof-decision`

Path:
`docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-proof-decision/`

What it proves:

- The focused proof gate consumed isolated candidate rows and evaluated replay,
  direct Python-manager probe and typed contract routes.
- `decision_counts` is `{"candidate": 2}` and `accepted_count` is `0`.
- Existing replay/probe helpers do not yet safely reproduce same-action V2
  switch/focus semantics with recovery; typed contract evidence is insufficient
  to promote the wire shape.

Included files:

- `proof_summary.md`
- `proof_summary.json`
- `proof_decisions.jsonl`

## Accepted Mappings `manager-fixture-v2-first-focused-proof-20260607`

Path:
`docs/protocol-research/evidence/accepted-mappings/manager-fixture-v2-first-focused-proof-20260607/`

What it proves:

- The accepted-mapping publication gate ran for the first focused V2 proof.
- `accepted_case_ids` is empty because both focused rows are candidate-only.
- Candidate rows are explicitly excluded until same-action replay, direct
  Python-manager probe or accepted typed contract proof exists.

Included files:

- `accepted_mappings.md`
- `accepted_mappings.json`

## Client Fixture V3 Mutation Recovery Proof `20260609-recovery-proof`

Path:
`docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-recovery-proof/`

What it proves:

- The closed V3 client fixture surface has a reviewed before/action/post/reset
  evidence boundary for text, number, date, checkbox toggle and inert-button
  mutation cases.
- The compact rows reference retained Windows-native handler and reset proof in
  ignored `.artifacts/openspec/` paths without copying raw captures or full
  form-analysis dumps into git.
- All five rows remain candidate-only because mutation action frame ranges,
  normalized hashes and accepted replay, direct Python-manager probe or typed
  contract proof are not retained yet.

Included files:

- `recovery_proof_summary.md`
- `mutation_recovery_cases.jsonl`

## Client Fixture V3 Mutation Manifest Contract `20260609-manifest-contract`

Path:
`docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-manifest-contract/`

What it proves:

- V3 mutation rows now have a fail-closed manifest shape with required
  `target_marker`, `mutation_family`, `pre_state`, `action`, `post_state`,
  `recovery_expectation`, `mutates_business_data=false` and
  `expected_action_result_markers` fields.
- Candidate publication is allowed for reviewed text, number, date, checkbox
  toggle and inert-button rows, but accepted promotion remains gated by
  mutation-specific action-frame isolation and replay, direct probe or typed
  contract proof.
- The accepted-mapping publication for
  `client-fixture-v3-mutation-20260609` is intentionally empty.

Included files:

- `manifest_contract_summary.md`
- `mutation_manifest_rows.jsonl`

## Client Fixture V4 Dialog Manifest Contract `20260609-manifest-contract`

Path:
`docs/protocol-research/evidence/client-fixture-v4-dialog-recovery/20260609-manifest-contract/`

What it proves:

- V4 dialog, expected-error and bounded-wait rows now have a fail-closed
  manifest shape with required `scenario_family`, `dialog_family`,
  `dialog_lifecycle`, expected text/result markers, recovery expectation and
  `mutates_business_data=false` fields.
- Expected-error rows require an expected diagnostic marker, while bounded-wait
  rows require a fixed `bounded_duration_ms` value.
- Candidate publication is allowed for warning, question, fixture-modal
  lifecycle, expected-error and bounded-wait rows, but accepted promotion
  remains gated by V4-specific dialog/action frame isolation and replay, direct
  probe or typed contract proof.

Included files:

- `manifest_contract_summary.md`
- `dialog_manifest_rows.jsonl`

## Client Fixture V4 Dialog Runtime Proof `20260609-runtime-proof`

Path:
`docs/protocol-research/evidence/client-fixture-v4-dialog-recovery/20260609-runtime-proof/`

What it proves:

- The live client fixture exposes the V4 baseline, warning, question,
  fixture-modal lifecycle, expected-error and bounded-wait marker families.
- Vanessa runtime proof retained action and reset fallback bundles for each
  V4 family; the local token validator checked 16 bundles and passed.
- Expected-error rows produced the reviewed diagnostic marker and reset back to
  `PF_V4_DIAGNOSTIC_NONE`.
- V4 runtime rows remain candidate-only until V4-specific replay, direct probe
  or typed contract proof supports accepted promotion.

Included files:

- `runtime_proof_summary.md`

## Accepted Mappings `client-fixture-v3-mutation-20260609`

Path:
`docs/protocol-research/evidence/accepted-mappings/client-fixture-v3-mutation-20260609/`

What it proves:

- The V3 mutation accepted-mapping publication gate ran for the candidate
  manifest rows.
- `accepted_case_ids` is empty because the rows lack isolated mutation action
  frame ranges, stable normalized hashes and accepted replay, direct
  Python-manager probe or typed contract proof.
- Marker and reset evidence are retained as candidate evidence only.

Included files:

- `accepted_mappings.md`
- `accepted_mappings.json`

## Manager Fixture V1 `opsx-manager-fixture-v1-dryrun`

Path:
`docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/`

What it proves:

- The manager fixture V1 reviewed evidence format records run id, command
  catalog version, bootstrap status, output paths, command counts and owner
  routes without copying raw runtime output.
- The retained run is explicitly a dry-run: it validates the manifest, result
  and event contract but does not claim live TestManager execution.
- The frame-join report records one unresolved dry-run event and five blocked
  catalog commands; no command is accepted as a protocol mapping.
- Future accepted mappings still require reviewed frame ranges, dynamic-field
  evidence, normalized hashes and replay or direct Python-manager proof.

Included files:

- `runtime_summary.md`
- `runtime_summary.json`
- `frame_join_report.md`
- `frame_join_report.json`

## Protocol Corpus `20260603-085618-fixture-readonly`

Path:
`docs/protocol-research/evidence/corpus/20260603-085618-fixture-readonly/`

What it proves:

- A Windows-native `form-analysis` capture ran with the planned fixture case
  manifest and retained raw traffic under
  `runtime/protocol-research/captures/20260603-085618/`.
- The capture produced six reviewed fixture rows, one for each planned family.
- All six rows remain `pending` with no frame range, normalized hash,
  operation token or response markers because the current runner cannot target
  a source-candidate fixture form.
- Capture cleanup stopped only the manager, proxy and TestClient PIDs created
  for the run.

Included files:

- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`
- `capture_probe_summary.md`

## Python Manager Probe `fixture-20260603-085618`

Path:
`docs/protocol-research/evidence/python-manager-probe/fixture-20260603-085618/`

What it proves:

- The direct Python-manager read-only probe still works against the current
  lab and the `20260603-085618` capture bootstrap.
- The probe returned the existing sales dashboard active form and two
  `EditField` details.
- The probe cannot target the candidate fixture forms and therefore does not
  accept `Button`, `Table`, `CommandBar`, `Page`, `Label` or `CheckBox`
  mappings.

Included files:

- `probe_summary.md`
- `probe_manifest.json`
- `python_manager_probe_result.json`

## Protocol Corpus Comparison `fixture-readonly-20260603-085618`

Path:
`docs/protocol-research/evidence/corpus-comparison/fixture-readonly-20260603-085618/`

What it proves:

- The fixture corpus rows were classified before publication.
- All six fixture families are non-accepted: analyzer classification is
  `incomplete_hash` and delivery status remains `pending`.
- No dynamic-field or normalizer rule was added because no fixture request
  frames were captured.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`
- `classification_summary.md`

## Protocol Accepted Mappings `fixture-readonly-20260603-085618`

Path:
`docs/protocol-research/evidence/accepted-mappings/fixture-readonly-20260603-085618/`

What it proves:

- Publication produced an accepted-mapping evidence directory for the fixture
  run, but it contains no accepted case ids.
- Missing fixture hashes, frame ranges and probe joins keep all six planned
  families out of accepted mappings.

Included files:

- `accepted_mappings.md`
- `accepted_mappings.json`

## Protocol Corpus `20260602-084433-readonly-smoke`

Path:
`docs/protocol-research/evidence/corpus/20260602-084433-readonly-smoke/`

What it proves:

- The first corpus runner can map read-only active-window, active-form and
  form-element cases to explicit protocol frame ranges.
- Each case row records request/response sizes, dynamic fields, normalized
  hash, operation tokens, response markers and replay status.
- The baseline mappings are confirmed by the direct Python-manager probe
  without a 1C TestManager instance.
- Runtime case markers are stored next to ignored raw capture output as
  `runtime/protocol-research/captures/20260602-084433/case_events.jsonl`.

Included files:

- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`

## Protocol Corpus `20260602-172319-readonly-smoke`

Path:
`docs/protocol-research/evidence/corpus/20260602-172319-readonly-smoke/`

What it proves:

- A fresh Windows capture was produced through the Vanessa attach-running path
  by `protocol_corpus_runner.py --run-capture`.
- The raw capture stayed under
  `runtime/protocol-research/captures/20260602-172319/`, including
  `case_manifest.json` and `case_events.jsonl`.
- The reviewed rows repeat the read-only active-window, active-form and
  form-element mappings with explicit frame ranges and normalized hashes.
- All three rows are marked `accepted` after a fresh direct Python-manager
  probe.

Included files:

- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`

## Python Manager Probe `corpus-20260602-172319`

Path:
`docs/protocol-research/evidence/python-manager-probe/corpus-20260602-172319/`

What it proves:

- The direct Python-manager prototype can query a live TestClient without a
  1C TestManager instance during the corpus-runner verification.
- The probe returned active form metadata and two form-element detail groups.
- The result confirms the fresh corpus rows as `accepted` read-only mappings.

Included files:

- `python_manager_probe_result.json`
- `probe_manifest.json`

## Protocol Corpus `20260602-172319-expanded-readonly`

Path:
`docs/protocol-research/evidence/corpus/20260602-172319-expanded-readonly/`

What it proves:

- The expanded read-only matrix emits family-labeled corpus rows for active
  window, active form, existing `EditField` element details and explicit
  fixture gaps.
- `EditField`/typed input rows are accepted by the direct Python-manager probe
  path; unavailable `Button`, `Table`, `CommandBar`, `Page`, `Label` and
  `CheckBox` families are marked `unsupported`.
- Unsupported rows retain `case_id`, `api_call`, `ui_target`, availability,
  expected markers and replay status while intentionally leaving frame ranges
  and hashes empty.

Included files:

- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`

## Protocol Corpus `20260602-193802-expanded-readonly`

Path:
`docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/`

What it proves:

- A fresh Windows Vanessa attach-running capture was produced for the expanded
  matrix by `protocol_corpus_runner.py --run-capture`.
- Cleanup stopped only the manager, proxy and TestClient PIDs created for the
  run; raw capture data remains under
  `runtime/protocol-research/captures/20260602-193802/`.
- This Vanessa-only run captured active-window/form traffic but did not reach
  the `101..106` element-detail frames, so supported element rows remain
  `pending` and the matrix exposes that coverage gap explicitly.

Included files:

- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`

## Protocol Corpus `20260602-195407-expanded-readonly`

Path:
`docs/protocol-research/evidence/corpus/20260602-195407-expanded-readonly/`

What it proves:

- A second fresh Windows Vanessa attach-running capture was produced for the
  same `expanded-readonly` matrix during repeatability verification.
- The run produced the same ten reviewed case rows as `20260602-193802` and
  kept raw capture data under
  `runtime/protocol-research/captures/20260602-195407/`.
- Supported active-window/form rows have captured hashes; supported
  element-detail rows remain `pending` because this Vanessa-only path did not
  emit the `101..106` detail frames.

Included files:

- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`

## Protocol Corpus Comparison `expanded-readonly-20260602-193802-vs-20260602-195407`

Path:
`docs/protocol-research/evidence/corpus-comparison/expanded-readonly-20260602-193802-vs-20260602-195407/`

What it proves:

- The repeatability analyzer can compare reviewed `corpus_cases.jsonl` inputs
  for the same matrix and report each `case_id` independently.
- Active-window and active-form hashes repeat across the two fresh captures,
  but remain `non_accepted` because replay/probe status is pending in the
  Vanessa-only rows.
- Element-detail rows are visible as `incomplete_hash`; unsupported fixture
  families remain explicit `unsupported_gap` entries.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

## Protocol Corpus Comparison `expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted`

Path:
`docs/protocol-research/evidence/corpus-comparison/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`

What it proves:

- The repeatability analyzer can attach compact direct Python-manager probe
  evidence while comparing reviewed corpus rows.
- Active-window and active-form rows are promoted from pending row status to
  stable accepted mappings because their normalized hashes repeat across
  captures and probe evidence confirms the same read-only operation family.
- Element-detail and typed-input rows stay `incomplete_hash` because the
  Vanessa-only rows still lack reviewed request-frame hashes, even though the
  direct probe returned useful data.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

## Protocol Accepted Mappings `expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted`

Path:
`docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`

What it proves:

- The first expanded read-only dictionary entries promoted through repeated
  hashes plus compact probe evidence are `active-window-context` and
  `active-form-context`.
- Accepted rows retain source capture ids, normalized hashes,
  request/response sizes and the compact probe evidence path.
- Raw captures and full probe output remain under ignored runtime paths.

Included files:

- `accepted_mappings.md`
- `accepted_mappings.json`

## Protocol Normalizer `expanded-readonly-20260602-193802-vs-20260602-195407`

Path:
`docs/protocol-research/evidence/normalizer/expanded-readonly-20260602-193802-vs-20260602-195407/`

What it proves:

- The normalizer report records before-hash and after-hash sets for repeated
  expanded corpus cases.
- Accepted replacements are limited to `ack_guid_uuid_le`,
  `sequence_uint16_le`, `nonce` and observed ASCII GUID ranges in the current
  reviewed rows.
- `operation_token` is preserved as a semantic token and is not replaced by
  the current normalizer; ambiguous fields are empty for this comparison.

Included files:

- `normalizer_report.md`
- `normalizer_report.json`

## Manager Fixture V1 Repeat Normalizer `manager-fixture-v1-full-repeat-20260605`

Path:
`docs/protocol-research/evidence/corpus-comparison/manager-fixture-v1-full-repeat-20260605/`

What it proves:

- Two full manager fixture V1 read-only runs completed the same 11-command
  catalog with joined frame windows and no failed harness commands.
- Raw selected payload hashes still differ between runs, but
  `manager_fixture_v1_binary_frame_signature.v1` stabilizes all 11 normalized
  hashes by preserving semantic payload tokens and replacing binary dynamic
  bytes plus repeated polling frames.
- All 11 rows remain `non_accepted`, not accepted protocol mappings, because
  replay/direct-probe evidence is still pending for the manager-fixture case
  ids.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

Related evidence:

- `docs/protocol-research/evidence/normalizer/manager-fixture-v1-full-repeat-20260605/`
- `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v1-full-repeat-20260605/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-full-readonly-bootstrap-second-boundary-guard/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-full-readonly-repeat-second-boundary-guard/`

## Manager Fixture V1 Active Window Probe Guard `manager-fixture-v1-full-repeat-active-window-probe-20260605`

Path:
`docs/protocol-research/evidence/corpus-comparison/manager-fixture-v1-full-repeat-active-window-probe-20260605/`

What it proves:

- The repeated manager fixture V1 read-only rows plus compact direct
  Python-manager active-window probe evidence do not promote
  `tm-v1-active-window` because the joined manager-fixture corpus row did not
  observe either expected marker `PF_FORM_MAIN` or
  `QA MCP Protocol Fixture V1`.
- The row remains `non_accepted` with stable normalized hash
  `840568665427219086966de565315bdc0a0adf25d6a7030da08a70a12ade50b5`,
  request size `99`, response size `212` and observed response markers
  `homepage[<guid>]`, `homepage`, `e1cib/navigationpoint/startpage`.
- The comparison keeps the active-window probe evidence path, but the
  marker-compatibility guard leaves effective replay status `pending` and
  records `expected_response_marker_not_observed`.
- `tm-v1-active-form` and the remaining 9 read-only rows also stay
  `non_accepted`; a valid fixture-form probe still needs a manager-harness
  request-shape replay for marker `PF_FORM_MAIN`.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

Related evidence:

- `docs/protocol-research/evidence/python-manager-probe/client-fixture-v1-active-window-20260604-172832/`
- `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v1-full-repeat-active-window-probe-20260605/`
- `docs/protocol-research/evidence/normalizer/manager-fixture-v1-full-repeat-active-window-probe-20260605/`

## Manager Fixture V1 Active Form Marker Replay `manager-fixture-v1-full-repeat-active-form-marker-probe-20260605`

Path:
`docs/protocol-research/evidence/corpus-comparison/manager-fixture-v1-full-repeat-active-form-marker-probe-20260605/`

What it proves:

- The repeated manager fixture V1 read-only rows plus direct Python-manager
  marker replay promote `tm-v1-active-form` to an accepted
  manager-fixture mapping.
- The replay used the captured manager-fixture request shape for
  `PF_FORM_MAIN`, replaced dynamic ACK GUID, sequence and nonce fields, and
  observed `PF_FORM_MAIN` in the client response.
- The accepted row keeps stable normalized hash
  `484507fd5b4399e3cee38f0da8201ca4efc6e3b5721851199effac2f1d39e973`,
  source captures
  `20260605-live-full-readonly-bootstrap-second-boundary-guard` and
  `20260605-live-full-readonly-repeat-second-boundary-guard`, request sizes
  `16638`, `16992`, response sizes `11280`, `11520` and response marker
  `PF_FORM_MAIN`.
- The active-window row remains `non_accepted`; its manager-fixture capture
  observes only HomePage/startpage markers, not the expected fixture window
  markers.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

Related evidence:

- `docs/protocol-research/evidence/manager-fixture-marker-probe/20260605-tm-v1-active-form-marker-replay/`
- `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v1-full-repeat-active-form-marker-probe-20260605/`
- `docs/protocol-research/evidence/normalizer/manager-fixture-v1-full-repeat-active-form-marker-probe-20260605/`

## Manager Fixture V1 Checkbox Marker Replay `manager-fixture-v1-full-repeat-active-form-checkbox-marker-probe-20260605`

Path:
`docs/protocol-research/evidence/corpus-comparison/manager-fixture-v1-full-repeat-active-form-checkbox-marker-probe-20260605/`

What it proves:

- A second direct Python-manager marker replay promotes
  `tm-v1-checkbox-true` to an accepted manager-fixture read-only mapping while
  retaining the previously accepted `tm-v1-active-form` row.
- The replay used the captured manager-fixture request shape for
  `PF_CHECKBOX_TRUE`, replaced dynamic ACK GUID, sequence and nonce fields, and
  observed the expected semantic marker `CheckBox` in the client response.
- The accepted checkbox row keeps stable normalized hash
  `7a6b4ee6ce323d54fc81add277f7e2071513e9ddff9f5a5af6d666bd0fdc9581`,
  source captures
  `20260605-live-full-readonly-bootstrap-second-boundary-guard` and
  `20260605-live-full-readonly-repeat-second-boundary-guard`, request sizes
  `17202`, `17690`, response sizes `11844`, `12180` and response markers
  `PF_CHECKBOX_TRUE`, `CheckBox`, `pf_checkbox_true`.
- The same smoke retained rejected probe evidence for `tm-v1-form-summary` and
  `tm-v1-field-version`: each replay returned only the target marker and did
  not observe the expected semantic marker.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

Related evidence:

- `docs/protocol-research/evidence/manager-fixture-marker-probe/20260605-next-readonly-marker-probes/`
- `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v1-full-repeat-active-form-checkbox-marker-probe-20260605/`
- `docs/protocol-research/evidence/normalizer/manager-fixture-v1-full-repeat-active-form-checkbox-marker-probe-20260605/`

## Manager Fixture V1 Window Sequence Replay `manager-fixture-v1-full-repeat-window-sequence-probe-20260605`

Path:
`docs/protocol-research/evidence/corpus-comparison/manager-fixture-v1-full-repeat-window-sequence-probe-20260605/`

What it proves:

- The marker probe can replay a complete joined case window by sending every
  captured manager chunk with dynamic ACK GUID, sequence and nonce replacement.
- Full-window replay did not promote additional read-only mappings beyond
  `tm-v1-active-form` and `tm-v1-checkbox-true`; accepted case ids remain
  `["tm-v1-active-form", "tm-v1-checkbox-true"]`.
- `tm-v1-form-summary` replayed `141` manager frames, sent `18682` bytes and
  received `12518` bytes, but observed only `PF_FORM_MAIN` and `pf_form_main`;
  expected marker `PF_FIXTURE_VERSION` was not observed.
- `tm-v1-field-version` replayed `126` manager frames, sent `17668` bytes and
  received `12074` bytes, but observed only `PF_FIXTURE_VERSION` and
  `pf_fixture_version`; expected marker `protocol-fixture.v1` was not
  observed.
- This points to a manifest/command semantic gap rather than a first-frame
  replay limitation for these two rows.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`

Related evidence:

- `docs/protocol-research/evidence/manager-fixture-marker-probe/20260605-window-sequence-probes/`
- `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v1-full-repeat-window-sequence-probe-20260605/`
- `docs/protocol-research/evidence/normalizer/manager-fixture-v1-full-repeat-window-sequence-probe-20260605/`

## Manager Fixture V1 BSL Object Semantics Probe `20260605-live-readonly-findobject-selected`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-readonly-findobject-selected/`

What it proves:

- The capture runner now supports narrow selected case execution through
  `-ManagerFixtureV1CaseId`; this retained run executed only
  `tm-v1-form-summary` and `tm-v1-field-version`.
- Failed inline BSL command events now retain `ОписаниеОшибки()` in
  `result_preview`, making manager-harness API failures diagnosable from
  compact runtime evidence.
- `ОжидатьОтображениеОбъекта(...)` is a visibility guard, not the returned
  tested object. Calling `ПолучитьПодчиненныеОбъекты()` or
  `ПолучитьПредставлениеДанных()` on that result failed with
  `Значение не является значением объектного типа`.
- Follow-up attempts using `ПолучитьОбъект(...)` failed for both marker and
  full fixture path addressing. The retained `НайтиОбъект(...)` run failed
  with explicit `form_summary object not found by marker` and
  `element_details object not found by marker`.
- The joined traffic still contains only `PF_FORM_MAIN` for
  `tm-v1-form-summary` and only `PF_FIXTURE_VERSION` for
  `tm-v1-field-version`; expected semantic markers `PF_FIXTURE_VERSION` and
  `protocol-fixture.v1` remain unobserved.

Included files:

- `runtime_summary.md`
- `frame_join_report.md`
- `corpus_cases.jsonl`

Related evidence:

- `runtime/protocol-research/captures/20260605-live-readonly-semantics-fix-selected/`
- `runtime/protocol-research/captures/20260605-live-readonly-getobject-selected/`
- `runtime/protocol-research/captures/20260605-live-readonly-targetpath-selected/`
- `runtime/protocol-research/captures/20260605-live-readonly-findobject-selected/`

## Python Manager Probe `expanded-20260602-193802`

Path:
`docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/`

What it proves:

- The direct Python-manager prototype queried a live `/TESTCLIENT` without a
  1C TestManager instance during the expanded matrix verification.
- The probe returned active form metadata and two `EditField` element detail
  groups, confirming the supported typed-input family.
- The TestClient PID created for the probe was stopped after the run; verbose
  runtime output remains under `runtime/protocol-research/python-manager-probe/`.

Included files:

- `python_manager_probe_result.json`
- `probe_manifest.json`

## Readonly Element Hash Audit `current-element-hash-gaps`

Path:
`docs/protocol-research/evidence/readonly-element-hash-audit/current-element-hash-gaps/`

What it proves:

- `form-element-details` and `typed-input-field-readonly` remain
  `incomplete_hash` in current package descriptors and in the repeated
  `20260602-193802` versus `20260602-195407` expanded comparison.
- The direct Python-manager probe returned useful `EditField` element detail
  data, but the compared rows still have zero request/response bytes and no
  normalized hashes.
- `20260602-172319-expanded-readonly` contains extractable reviewed
  `101..106` request-hash evidence for both target rows; typed-input still
  needs an operation-join review because it reuses the element-detail request
  shape.

Included files:

- `audit_summary.md`

## Readonly Element Request Hashes `20260602-172319-expanded-extracted`

Path:
`docs/protocol-research/evidence/readonly-element-request-hashes/20260602-172319-expanded-extracted/`

What it proves:

- Existing reviewed compact corpus evidence can supply request-hash facts for
  `form-element-details` and `typed-input-field-readonly` without starting a
  fresh live 1C runtime.
- Both rows use manager frames `101..106`, client frames `102..107`, request
  size `1200`, response size `972` and normalized hash
  `b56da7520da52418f0941530becea763233f5affc658a7bb3da9c1c3162e630a` from
  capture `20260602-172319`.
- The typed-input row shares the element-detail request shape, so downstream
  classification must still record the operation-join decision before
  descriptor publication.

Included files:

- `request_hash_summary.md`
- `request_hashes.json`

## Protocol Corpus Comparison `readonly-element-hash-resolution-20260603-extracted`

Path:
`docs/protocol-research/evidence/corpus-comparison/readonly-element-hash-resolution-20260603-extracted/`

What it proves:

- The comparison tool now emits stable `precise_reasons` and provider-owner
  routing alongside the existing classification.
- `form-element-details` remains `incomplete_hash` with
  `accepted_reviewed_hash` and `missing_request_frames` reasons.
- `typed-input-field-readonly` remains `incomplete_hash` with
  `accepted_reviewed_hash`, `ambiguous_operation_join` and
  `missing_request_frames` reasons.
- Active-window and active-form accepted classifications are preserved.

Included files:

- `corpus_comparison.md`
- `corpus_comparison.json`
- `classification_summary.md`

## Readonly Element Hash Resolution `20260603-incomplete-hash-with-extracted-request-evidence`

Path:
`docs/protocol-research/evidence/readonly-element-hash-resolution/20260603-incomplete-hash-with-extracted-request-evidence/`

What it proves:

- The final card outcome is unresolved: neither `form-element-details` nor
  `typed-input-field-readonly` is promoted to an accepted package descriptor.
- Extracted reviewed request-hash evidence exists from `20260602-172319`, but
  the current repeated comparison inputs still lack request bytes and hashes
  for both target rows.
- `typed-input-field-readonly` additionally keeps an
  `ambiguous_operation_join` reason because it shares the element-detail
  request shape.
- Safe-action work remains blocked by read-only descriptor evidence gaps.

Included files:

- `resolution_summary.md`
- `resolution.json`

## Safe Action Candidate Manifest `20260603-opsx-do-safe-action`

Path:
`docs/protocol-research/evidence/safe-action-candidates/20260603-opsx-do-safe-action/`

What it proves:

- The first safe-action candidate is limited to activating an already-open
  internal TestClient window.
- The candidate keeps controlled fixture and read-only element hash outcomes
  as deferred/unresolved gates instead of treating them as accepted action
  evidence.
- The row contract includes pre-state, action, post-state, recovery
  expectation and action result marker fields before live capture.

Included files:

- `candidate_summary.md`
- `safe_action_case_manifest.json`

## Protocol Corpus `20260603-134132-safe-action`

Path:
`docs/protocol-research/evidence/corpus/20260603-134132-safe-action/`

What it proves:

- A Windows-native `safe-action` capture ran through Vanessa attach-running
  and retained raw traffic under
  `runtime/protocol-research/captures/20260603-134132/`.
- The capture invoked `activate_window` for an already-open internal
  TestClient window and attempted recovery to the original active window.
- The reviewed row remains `pending`: no action frame range, normalized hash,
  operation token or replay/probe proof is accepted yet.
- The compact row redacts localized window title values and records only
  status and match facts.
- Capture cleanup stopped only the manager, proxy and TestClient PIDs created
  by the run.

Included files:

- `capture_probe_summary.md`
- `corpus_report.md`
- `corpus_summary.json`
- `corpus_cases.jsonl`

## Protocol Corpus Comparison `safe-action-20260603-134132`

Path:
`docs/protocol-research/evidence/corpus-comparison/safe-action-20260603-134132/`

What it proves:

- The safe-action comparison classified
  `safe-activate-existing-window` as `pending`, not accepted.
- The row keeps the action result markers
  `status=pending` and `window_title_observed`, while recording that the
  reviewed evidence still lacks an action frame range, request frames,
  normalized hash and replay/probe proof.
- Provider-owner routing stays visible:
  `/opt/vanessa-mcp-stack` for action-frame join evidence and
  `project:qa-mcp` for replay/probe support after reviewed action frames
  exist.

Included files:

- `classification_summary.md`
- `corpus_comparison.md`
- `corpus_comparison.json`

## Safe Action Accepted Mappings `safe-action-20260603-134132`

Path:
`docs/protocol-research/evidence/accepted-mappings/safe-action-20260603-134132/`

What it proves:

- No safe UI action mapping is accepted from capture `20260603-134132`.
- The accepted mapping set is intentionally empty because the action row has
  pending status and no reviewed action frame or replay/probe proof.
- Package descriptors remain unchanged and read-only.

Included files:

- `accepted_mappings.md`
- `accepted_mappings.json`

## Python Manager Package Smoke Environment Gap `20260603-offline-gap`

Path:
`docs/protocol-research/evidence/python-manager-package-smoke/20260603-offline-gap/`

What it proves:

- The package read-only session API was verified offline during promotion.
- The local Vanessa target environment was statically valid, but no live
  manager or TestClient was started for a retained package smoke in that run.
- A future live read-only package smoke should write compact evidence under a
  new run id before treating live package behavior as fresh runtime evidence.

Included files:

- `environment_gap.md`

## Manager Fixture V1 Live Smoke Gap `20260605-live-smoke-runtime-gap`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-live-smoke/20260605-live-smoke-runtime-gap/`

What it proves:

- The first manager fixture V1 smoke scope is bounded to
  `tm-v1-active-window`, `tm-v1-active-form` and `tm-v1-field-version`.
- The non-dry-run runner fails closed before starting any 1C process when the
  default Vanessa EPF is absent.
- The retained runtime directory contains a three-command manager harness
  manifest, invocation record, empty `case_events.jsonl` and
  `manager_harness_result.json` with `runtime_gap`.
- Join/corpus evidence was generated for the smoke runtime directory; all
  three rows remain non-accepted with unresolved reason `no_before_event`.
- Full V1 catalog expansion remains blocked until the EPF/runtime profile is
  restored and at least one smoke row has reviewed range/hash evidence.

Included files:

- `smoke_summary.md`
- `smoke_summary.json`

Related evidence:

- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260605-live-smoke-runtime-gap/`
- `runtime/protocol-research/captures/20260605-live-smoke-runtime-gap/`

## Automated Testing API Inventory `8.3.27.1786`

Path:
`docs/protocol-research/api-inventory/`

What it proves:

- The first corpus-planning inventory was extracted from the available
  `help-mcp` platform help snapshot `8.3.27.1786`.
- Eight automated-testing object surfaces and 160 member rows have conservative
  `read_only`, `safe_ui_action`, `mutation`, `agent_runtime` or
  `unsupported_initial` safety classes.
- Source gaps are explicit: help/runtime version mismatch, missing client-agent
  entity resolution, parameter signatures, constructor signatures,
  command-bar identity and one table exhaustiveness gap.
- The inventory is planning input only; accepted protocol mappings still
  require live frame ranges, normalized hashes and replay or probe proof.

Included files:

- `automated-testing-8.3.27.1786.json`
- `automated-testing-8.3.27.1786-summary.md`
- `automated-testing-8.3.27.1786-gaps.md`

## Manager Fixture V1 Command Interface Bootstrap `20260606`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/`

What it proves:

- `20260606-live-command-interface-dump-app-window-direct` shows that
  `ПолучитьАктивноеОкно()` can be the start page, while the application
  command interface is available from
  `ТестируемоеОкноКлиентскогоПриложения` with caption
  `Демонстрационное приложение`.
- `20260606-live-command-interface-section-dump-retry` shows that the fixture
  command is under section `Предприятие` and has navigation URL
  `e1cib/command/Обработка.ФикстураПротоколаTestClient.Открыть`.
- `20260606-live-fixture-ci-bootstrap-smoke-title-fix` proves the manager
  harness can open the client fixture itself through command interface
  bootstrap and then complete three read-only commands:
  `tm-v1-active-form`, `tm-v1-form-summary` and `tm-v1-field-version`.
- `20260606-live-fixture-ci-bootstrap-full-readonly` scales the same bootstrap
  to the full read-only catalog selected by the runner. All 17 case windows
  were joined to traffic ranges, while the harness result is intentionally
  `partial`: three legacy diagnostic branches still search forms through the
  active window/path semantics and need a separate cleanup before they are
  useful as accepted corpus rows.
- `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup` is the cleanup
  run after fixing those diagnostic branches and replacing generic
  `*_summary` waits with object-level read-only lookups. It completed all 17
  read-only commands, joined all 17 frame windows, and retained typed
  `result_preview` markers for checkbox, button, table, command bar, group and
  pages surfaces.
- The successful smoke joined all three command windows to traffic ranges and
  preserved normalized hashes. The cleanup live-join report now folds in the
  retained replay proof for eight rows: active window, active form, two
  diagnostic field-marker rows, two field rows, the main command bar and pages.
  The pending-promotion publication keeps the accepted count at eight, promotes
  zero additional rows, and records blockers for all nine pending rows.
- The Vanessa pre-attach/open-fixture route remains negative evidence: it can
  open the form, but leaves the TestClient connected to another TestManager and
  therefore cannot be the primary corpus route.

Included files:

- `20260606-live-command-interface-dump-app-window-direct/runtime_summary.md`
- `20260606-live-command-interface-section-dump-retry/runtime_summary.md`
- `20260606-live-fixture-ci-bootstrap-smoke-title-fix/runtime_summary.md`
- `20260606-live-fixture-ci-bootstrap-smoke-title-fix/frame_join_report.md`
- `20260606-live-fixture-ci-bootstrap-smoke-title-fix/corpus_cases.jsonl`
- `20260606-live-fixture-ci-bootstrap-full-readonly/runtime_summary.md`
- `20260606-live-fixture-ci-bootstrap-full-readonly/frame_join_report.md`
- `20260606-live-fixture-ci-bootstrap-full-readonly/corpus_cases.jsonl`
- `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/runtime_summary.md`
- `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/frame_join_report.md`
- `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/corpus_cases.jsonl`
- `20260606-pending-promotion-final-readiness/runtime_summary.md`
- `20260606-pending-promotion-final-readiness/frame_join_report.md`
- `20260606-pending-promotion-final-readiness/readiness_summary.md`
- `20260606-pending-promotion-final-readiness/corpus_cases.jsonl`

## Manager Fixture V1 Replay Probe `20260606-cleanup-readonly-fields`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-readonly-fields/`

What it proves:

- `tm-v1-field-version` replays through manager frame `122` against a fresh
  TestClient and returns `KS protocol-fixture.v1`.
- `tm-v1-field-string` replays through manager frame `125` and returns
  `KS PF_EDIT_STRING_VALUE`.
- Raw replay must rewrite UI path GUIDs for `SecondaryFrame[...]` and
  `ManagedForm[...]` to the live values observed from client responses; replacing
  only `ManagedForm[...]` leaves value reads as `KU`.
- Binary random-block adaptation is range-sensitive: resolution frames can use
  GUID+block replacement, while value-read frames are replayed with GUID-only
  replacement plus UI path GUID replacement.

Included files:

- `summary.md`
- `summary.json`

## Manager Fixture V1 Replay Probe `20260606-cleanup-commandbar-main`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-commandbar-main/`

What it proves:

- `tm-v1-commandbar-main` replays through manager frame `407` against a fresh
  TestClient and returns the command bar children, including
  `PF_COMMAND_ENABLED`, `PF_COMMAND_DISABLED`, `PF_COMMAND_POPUP` and
  `PF_RESET_STATE`.
- The replay uses the same UI path GUID replacement rule proven by the field
  probes, plus range-sensitive binary random-block adaptation. Frames
  `402..405` use GUID+block replacement; frames `406..407` use GUID-only
  replacement.
- The cleanup live-join report folds this retained replay proof into
  `accepted_case_ids`, together with the field and summary419 replay evidence.
  The run now includes the command-bar row among accepted rows:
  `tm-v1-field-version`, `tm-v1-field-string` and `tm-v1-commandbar-main`.

Included files:

- `summary.md`
- `summary.json`

## Manager Fixture V1 Replay Probe `20260606-cleanup-summary419-uipath`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-summary419-uipath/`

What it proves:

- A replay through manager frame `419` completes without `no_response` and
  confirms five additional rows: `tm-v1-active-window`, `tm-v1-active-form`,
  `tm-v1-diag-window-find-field-marker`,
  `tm-v1-diag-form-find-field-marker` and `tm-v1-pages-main`.
- `tm-v1-pages-main` returns `PF_PAGE_A`, `PF_PAGE_B` and `PF_PAGES_MAIN` in
  response after send `419`.
- `tm-v1-checkbox-true`, `tm-v1-button-inert`, `tm-v1-table-items` and
  `tm-v1-group-main` are intentionally retained as non-accepted observations:
  their endpoint responses contain useful target/structural markers, but not
  their declared expected markers.
- The cleanup live-join report now has eight accepted rows and nine pending
  rows.

Included files:

- `summary.md`
- `summary.json`

## Manager Fixture V1 Pending Read-Only Classification `20260606`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

What it proves:

- All nine non-accepted rows from the current cleanup run have a retained
  classification.
- Two diagnostic rows primarily lack replay/direct-probe evidence, three rows
  are wrong expected-marker or wrong-endpoint candidates, two rows have
  ambiguous frame ranges, and two rows have current-run replay marker
  mismatches.
- Classification does not promote any row. Manifest marker changes are listed
  as candidate-only until current-run replay/direct-probe evidence validates
  the corrected semantics.

Included files:

- `classification_summary.md`
- `classification.json`

## Manager Fixture V1 Replay Probe `20260606-pending-readonly-review`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-readonly-review/`

What it proves:

- No additional pending row is accepted by this review.
- Four rows have retained current-run transport-level replay observations with
  marker mismatches: `tm-v1-checkbox-true`, `tm-v1-button-inert`,
  `tm-v1-table-items` and `tm-v1-group-main`.
- Five rows were not attempted because no live TestClient endpoint was
  available for focused Windows-native replay/direct probes during this pass.
- The reviewed summary has zero `accepted_probe_cases`, so feeding it to the
  manager fixture report preserves the accepted count at eight.

Included files:

- `summary.md`
- `summary.json`

## Manager Fixture V1 Pending Promotion Final Readiness `20260606`

Path:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-promotion-final-readiness/`

What it proves:

- The final manager fixture V1 read-only publication still has 17 joined
  command windows.
- Eight rows remain accepted by replay/probe evidence matched by `case_id`,
  manager frame range and `normalized_hash`.
- The pending-promotion card promotes zero additional rows. The final state is
  8 accepted rows and 9 pending rows.
- V2 live safe-action acceptance remains blocked until the runtime endpoint is
  restored and focused proof is retained, or the project records an explicit
  residual-risk decision.

Included files:

- `runtime_summary.md`
- `runtime_summary.json`
- `frame_join_report.md`
- `frame_join_report.json`
- `readiness_summary.md`
- `readiness_summary.json`
- `corpus_cases.jsonl`

## Manager Fixture V1 Pending Promotion Blockers `20260606`

Paths:

- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-readonly-runtime-preflight/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-ambiguous-range-isolation/`
- `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/`

What it proves:

- The focused runtime pass stopped at `runtime_gap` before starting 1C
  processes because the default Vanessa EPF asset is missing.
- Five missing-proof rows have row-specific blockers with current cleanup
  frame ranges and normalized hashes.
- `tm-v1-diag-window-get-form-path` and `tm-v1-button-inert` remain
  non-accepted because their broad frame windows were not isolated.
- Marker-contract reconciliation applies no catalog changes and accepts no row
  by expected-marker change alone.
- This blocker state is historical. It is superseded by the follow-up marker
  and side-channel contract proofs below.

Included files:

- `runtime_summary.md`
- `runtime_summary.json`
- `summary.md`
- `summary.json`
- `isolation_summary.md`
- `isolation_summary.json`
- `marker_contract_summary.md`
- `marker_contract_summary.json`
- `catalog_comparison.json`

## Manager Fixture V1 Follow-up Contract Proofs `20260606`

Paths:

- `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-promote-candidate-marker-contracts/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-promote-candidate-marker-contracts-focused-proof-accepted/`
- `docs/protocol-research/evidence/manager-fixture-v1-side-channel-count-contracts/20260606-side-channel-count-contracts-focused-proof/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-count-contracts-focused-proof/`
- `docs/protocol-research/evidence/manager-fixture-v1-side-channel-form-path-contract/20260606-side-channel-form-path-focused-proof/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-side-channel-form-path-focused-proof/`

What it proves:

- Five candidate marker contracts were promoted in the manager fixture V1
  catalog and verified by a focused direct marker proof.
- Six formerly pending rows are accepted by the marker-contract focused proof:
  `tm-v1-diag-window-find-form-marker`, `tm-v1-form-summary`,
  `tm-v1-checkbox-true`, `tm-v1-button-inert`, `tm-v1-table-items` and
  `tm-v1-group-main`.
- Two diagnostic count rows are accepted by typed manager side-channel
  contracts using `manager_case_event.after.result_preview`, not by direct
  wire marker observation.
- The diagnostic form-path row is accepted by a typed manager side-channel
  contract using `manager_case_event.after.result_preview` marker
  `form_path_attempted=`, not by direct wire marker observation.
- All nine formerly pending manager fixture V1 readonly rows now have accepted
  contract-backed mappings.

Included files:

- `contract_promotion_summary.md`
- `contract_promotion_summary.json`
- `summary.md`
- `summary.json`
- `runtime_summary.md`
- `runtime_summary.json`
- `frame_join_report.md`
- `frame_join_report.json`
- `corpus_cases.jsonl`

## Demo Button Safe-Action Pilot Decision `20260610-demo-button-blocked-publication`

Path:
`docs/protocol-research/evidence/demo-button-safe-action/20260610-demo-button-blocked-publication/`

What it proves:

- A real demo10413 button target was selected from source evidence:
  `demo10413-operation-goods-toggle-activity`.
- The target was classified before execution as `business_mutation` because it
  is tied to document register-record activity state.
- The guarded capture stopped before TestClient connection, pre-state recheck
  or click, producing a safe blocked result.
- The final pilot status is `routed_to_v3`; accepted V2 safe-action mapping
  output is intentionally empty.

Included files:

- `publication_summary.md`
- `pilot_decision.json`
- `pilot_decisions.jsonl`
- `ui-evidence.md`

Related accepted-mapping output:

- `docs/protocol-research/evidence/accepted-mappings/demo-button-safe-action-20260610/`

## Demo Real Mutation Corpus Pilot `20260610-blocked-pilot`

Path:
`docs/protocol-research/evidence/demo-real-mutation-corpus/20260610-blocked-pilot/`

What it proves:

- The first real demo10413 mutation row reuses the reviewed document-form
  button `demo10413-operation-goods-toggle-activity` from card 60.
- The row explicitly declares `mutates_business_data=true` and remains blocked
  before UI action because live pre-state and a reviewed recovery wrapper are
  missing.
- The capture-mode live runtime preflight passed, so the blocker is the
  mutation evidence contract, not basic lab availability.
- No demo data was changed, no raw capture was created and accepted mutation
  mapping output is intentionally empty.

Included files:

- `publication_summary.md`
- `pilot_decision.json`
- `pilot_rows.jsonl`
- `ui-evidence.md`

Related accepted-mapping output:

- `docs/protocol-research/evidence/accepted-mappings/demo-real-mutation-corpus-20260610/`

## Demo Real Mutation Executed `20260610-warehouse-donotuse-real-mutation`

Path:
`docs/protocol-research/evidence/demo-real-mutation-corpus/20260610-warehouse-donotuse-real-mutation/`

What it proves:

- The first **real, recoverable business-data mutation** on a real demo form
  was executed end to end, superseding the prior `blocked` pilot.
- On `vanessa_client` (disposable demo copy), the boolean attribute
  `НеИспользовать` of catalog `Справочник.Склады` element `Средний`
  (code `000000003`) was toggled false→true, written and confirmed by a
  database reread (`Перечитать`), then restored true→false and confirmed again.
- The lab runtime (vanessa manager + TestClient) was brought up and driven via
  the vanessa-mcp reference oracle; no demo data residue remains.
- This run proves the action and runtime, not a decoded protocol frame: it ran
  through the reference oracle, not the qa-mcp capture proxy, so accepted
  protocol mapping output stays intentionally empty. Capturing the same action
  through the proxy is the documented next step.

Included files:

- `publication_summary.md`
- `mutation_decision.json`

## Demo Real Mutation Protocol Capture `mut-warehouse-donotuse-20260610`

Path:
`docs/protocol-research/evidence/demo-real-mutation-corpus/20260610-warehouse-donotuse-protocol-capture/`

What it proves:

- The same real warehouse `НеИспользовать` toggle was re-run **through the
  qa-mcp capture pipeline** (new `-Scenario demo-catalog-mutation`), so its
  TestClient protocol frames were captured through the recording proxy.
- The mutation and recovery are DB-confirmed (`Нет`→`Да`→`Нет`) and the run
  status is `mutation_and_recovery_confirmed`.
- 1723 frames were captured; the **action-write** phase is isolated to
  **28 frames / 7512 bytes**, cleanly separated from bootstrap, read and
  recovery traffic by the recorded UTC phase timeline.
- This is the first protocol-level evidence of a real business-data mutation
  in qa-mcp, and it is now **`accepted`**: a repeat capture is `fully_stable`
  (byte-identical normalized hash), and a **Python-manager-driven probe** (no
  Vanessa manager) replayed the full 861-frame flow live with zero divergence,
  its action-write phase normalized hash matching the Vanessa reference
  (`python_manager_acceptance.json`, verdict `accepted`). `TestedFormButton.Click`
  is promoted to `accepted_reviewed` — the project's first confirmed mapping.

Included files:

- `publication_summary.md`
- `frame_isolation.json` (compact per-frame metadata, no raw payload)
- `decode-findings.md` (dynamic-field map; `fully_stable` normalizer)
- `write_template_fieldmap.json` (compact write-template field map)
- `stability_first_vs_repeat.json`, `acceptance_gate_demo.json`
- `python_manager_probe_attempt.md` (first replay attempt; diverged at frame 2)
- `python_manager_probe_accepted.md` + `python_manager_acceptance.json`
  (generalized adaptive replay; full flow; `accepted`)

Tooling: `tools/protocol-research/compare_probe_reference.py`,
`adaptive_replay_probe.py`, `scope_tracker.py`,
`src/qa_mcp/protocol/mutation.py`.

Raw streams, parsed frames and the full write template stay under ignored
`runtime/protocol-research/`.

## Card 115 8.5 Genuine List-Form Capture

Path:
`docs/protocol-research/evidence/card115-8-5-genuine-capture-2026-06-25/`

What it proves:

- Vanessa TestManager on 8.5, using a real HOME profile, drove an 8.5
  TestClient against `/opt/1c-dev/vanessa_client_85`.
- The scenario connected the client, opened the `Товары` catalog list form,
  selected the first list row and read the `Наименование` dynamic-list column.
- The captured traffic was converted into a 45-record JSONL stream that parses
  with the production `CaptureBootstrap` loader: 24 manager-to-client records
  and 21 client-to-manager records.
- This is a genuine 8.5 capture-path proof for the card-98-equivalent read
  scenario; it does not claim replay acceptance or a promoted protocol mapping.

Included files:

- `README.txt`
- `qa-85-listform-read.feature`
- `8-5-card98-listform-traffic.jsonl`

The local source pcap (`8-5-listform.pcap`) remains outside git under the
repository `*.pcap` ignore rule.

## Card 120 Windows Host-Agent Display Subset

Path:
`docs/protocol-research/evidence/card120-windows-host-agent-2026-06-26/`

What it proves:

- The model-B remote-client display subset can route through a Windows
  host-side agent for version/health, window-list, screenshot and OS input.
- The final Go agent binary reported version `0.1.0-card120` and SHA256
  `1fe93f6f7e447dacdb536b1d6da3fd4e662e3b2450c045dcfe68e45f0c336d9f`.
- A Windows-rendered 1C TestClient received genuine Unicode input through the
  remote backend: the final PNG proof shows `WOK-Ж120` in the managed-form
  field `Наименование` with `save=false`.
- The protocol readback remained false, matching the earlier SendInput spike;
  this evidence proves UI input delivery and screenshot recovery, not DB
  persistence.

Included files:

- `findings.md`
- `summary.json`

## Protocol Corpus Evidence Contract

The row contract is defined in
`docs/protocol-research/corpus-evidence-contract.md`, and runner usage is
documented in `docs/protocol-research/protocol-corpus-runner.md`. Future
reviewed corpus output belongs under
`docs/protocol-research/evidence/corpus/`. Raw captures and generated replay
output stay under ignored `runtime/protocol-research/` paths.
