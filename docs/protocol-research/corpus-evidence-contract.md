# Protocol Corpus Evidence Contract

This document defines the reviewed evidence row used by the protocol corpus.
It is the contract between capture tooling, replay/probe tooling and compact
evidence committed under `docs/protocol-research/evidence/`.

Raw TCP captures, generated replay payloads, process logs and temporary probe
output remain under ignored `runtime/protocol-research/` paths. Reviewed
corpus rows keep only the compact facts needed to reproduce and compare a
protocol claim.

## Case Row

Each promoted corpus case MUST be represented by one JSON-compatible row.

| Field | Required | Semantics |
| --- | --- | --- |
| `case_id` | yes | Stable slug for one protocol case, for example `active-window-title`. |
| `scenario` | yes | Runner scenario, Vanessa scenario or manual case label that produced the capture. |
| `api_call` | yes | 1C testing API operation under study, for example `TestedApplication.GetActiveWindow`. |
| `ui_target` | yes | Target window, form or element. Use `null` only when the operation has no UI target. |
| `expected_state` | yes | Short observable state expected before the API call is evaluated. |
| `acceptance_contract` | no | Typed non-wire acceptance rule from the manifest, for example a manager side-channel `result_preview` contract. |
| `action_id` | safe action | Stable V2 safe-action manifest id. |
| `target_id` | safe action, mutation or dialog | Stable target id from the fixture target map, manager manifest, mutation manifest or V4 dialog manifest. |
| `target_marker` | safe action, mutation or dialog | Observable marker proving the intended target is present. |
| `pre_state` | safe action, mutation or dialog | Observable state before a `safe_ui_action`, V3 mutation or V4 dialog scenario; omitted for legacy read-only rows. |
| `action` | safe action, mutation or dialog | Allowed action family and concrete interaction path. |
| `post_state` | safe action, mutation or dialog | Expected observable state after the action. |
| `recovery_expectation` | safe action, mutation or dialog | How the lab returns to a known UI state or why no cleanup is required. |
| `mutates_business_data` | safe action, mutation or dialog | Must be `false` for V2 safe-action, V3 mutation sandbox and V4 dialog/wait rows. |
| `allowed_action_family` | safe action | One of the V2 allowlisted families from `safe-ui-action-scope.md`. |
| `mutation_id` | mutation | Stable V3 mutation manifest id; may match `case_id` when there is no separate alias. |
| `mutation_family` | mutation | One of the reviewed V3 families: `text_input`, `number_input`, `date_input`, `checkbox_toggle` or `inert_button`. |
| `dialog_scenario_id` | dialog | Stable V4 dialog, expected-error or bounded-wait manifest id; may match `case_id`. |
| `scenario_family` | dialog | One of `warning`, `question`, `fixture_modal`, `expected_error`, `bounded_wait_complete`, `bounded_wait_cancel` or `bounded_wait_retry`. |
| `dialog_family` | dialog | Fixture marker family such as `PF_V4_WARNING`, `PF_V4_QUESTION`, `PF_V4_MODAL`, `PF_V4_EXPECTED_ERROR` or `PF_V4_WAIT`. |
| `dialog_lifecycle` | dialog | Expected lifecycle marker after the action, for example `PF_V4_WARNING_CLOSED` or `PF_V4_WAIT_COMPLETED`. |
| `expected_text_marker` | dialog | Marker that identifies the expected warning, question, modal, expected-error or wait text. |
| `expected_dialog_result_marker` | dialog | Marker that identifies the selected result, acknowledgement, open/close state or wait outcome. |
| `expected_diagnostic_marker` | dialog | Required for `expected_error` rows; omitted or explicit `N/A` for non-error families. |
| `bounded_duration_ms` | dialog | Required for bounded wait rows; omitted or explicit `N/A` for non-wait families. |
| `expected_action_result_markers` | safe action, mutation or dialog | Markers expected by the manifest before capture or manager-runner execution. |
| `action_frame_range` | safe action, mutation or dialog | Frame range attributed to the action itself, separate from surrounding refresh traffic. |
| `background_frame_ranges` | safe action, mutation or dialog | Adjacent active-window, form, idle or refresh ranges not treated as proof of the action. |
| `recovery_frame_range` | safe action, mutation or dialog | Frame range attributed to reset or recovery traffic, separate from the action shape. |
| `action_result_markers` | safe action, mutation or dialog | Compact markers that show the expected action result was observed. |
| `recovery_result` | mutation | Observed reset or recovery state and compact evidence path. |
| `rerun_determinism` | mutation or dialog | Evidence that the same mutation or dialog scenario can run again after reset, or a candidate reason when proof is incomplete. |
| `mutation_review_status` | mutation | One of `candidate`, `accepted`, `rejected`, `blocked`, `partial` or `timeout`. |
| `dialog_review_status` | dialog | One of `candidate`, `accepted`, `rejected`, `blocked`, `partial`, `timeout` or `expected_error`. |
| `accepted_protocol_mapping` | safe action, mutation or dialog | Boolean publication decision; mutation and dialog rows default to `false` until proof-gated. |
| `element_family` | no | Form element family such as `EditField`, `Button`, `Table` or `CheckBox` when the case targets a form element. |
| `availability` | no | `supported`, `pending` or `unsupported`; omitted legacy rows should be treated as `supported`. |
| `expected_response_markers` | no | Short expected marker labels used to audit whether a capture covers the intended family. |
| `frame_range` | yes | Inclusive manager-frame range or an object with per-direction ranges. |
| `request_size` | yes | Total captured request bytes used for the normalized request signature. |
| `response_size` | yes | Total captured response bytes considered for markers. |
| `dynamic_fields` | yes | List of normalized byte or text fields with ranges and replacement labels. |
| `pre_normalization_hash` | no | SHA-256 hash of request bytes after tail stripping but before dynamic replacements. |
| `normalized_hash` | yes | SHA-256 hash of normalized request bytes, encoded as lowercase hex. |
| `normalization_replacements` | no | Replacement fields that affected `normalized_hash`; mirrors or refines `dynamic_fields` for newer rows. |
| `preserved_fields` | no | Candidate fields deliberately kept in `normalized_hash`, such as semantic operation tokens. |
| `ambiguous_fields` | no | Candidate dynamic fields that need more evidence before replacement. |
| `operation_token` | yes | Command-like byte token or `null` when no stable token has been isolated. |
| `response_markers` | yes | Short strings, GUIDs, numeric values or byte markers that identify the response shape. |
| `replay_status` | yes | One of the statuses defined below. |
| `probe_evidence` | no | Compact direct Python-manager or replay evidence summary used to justify `replay_status`; see Direct Probe Evidence. |
| `side_channel_evidence` | no | Compact manager harness side-channel evidence used to justify `accepted_side_channel`; see Side-Channel Evidence. |
| `acceptance_evidence` | no | Short list of reviewed facts that allowed promotion to `accepted`, such as stable repeated hashes and accepted probe evidence. |
| `evidence_path` | yes | Repository-relative compact evidence path under `docs/protocol-research/evidence/`. |
| `semantic_sources` | no | Help, metadata or EDT references used only to label the row. |
| `notes` | no | Human-readable limitation, hypothesis or follow-up. |

Rows MUST NOT include full request/response payloads, credentials, customer
data, full 1C logs or local secrets.

## Dynamic Fields And Hashing

Normalizers MUST record every replacement that affects `normalized_hash`.
Each `dynamic_fields` item SHOULD include:

- `name`: stable label such as `ack_guid`, `sequence`, `nonce`,
  `managed_form_guid`, `session_guid`, `timestamp` or `operation_token_echo`;
- `source`: `ascii`, `utf16le`, `binary`, `header` or `derived`;
- `direction`: `manager_to_client`, `client_to_manager` or `both`;
- `frame`: frame number when the range is frame-local;
- `offset` and `length` for byte ranges when known;
- `original_class`: broad value class such as `guid`, `uint32`, `uint64`,
  `counter`, `opaque_bytes` or `text`;
- `replacement`: deterministic placeholder used before hashing.

`normalized_hash` is calculated after replacing dynamic byte ranges with their
deterministic placeholders. The replacement set must be narrow enough that a
stable hash still represents the same request family, not a whole unrelated
interaction.

`operation_token` records the smallest currently known command-like token. It
SHOULD remain in the bytes used for `normalized_hash` unless repeated evidence
proves it is session-specific rather than semantic. If several candidate token
ranges exist, the row should keep the most stable one in `operation_token` and
list preserved or ambiguous candidates in `preserved_fields`,
`ambiguous_fields` or `notes`.

Unsupported or pending fixture-gap rows MAY set `frame_range`,
`normalized_hash` and `operation_token` to `null` only when no safe capture
exists for that family in the current lab form. Such rows MUST still keep
`case_id`, `api_call`, `ui_target`, `expected_state`, `availability`,
`replay_status`, `evidence_path` and a `notes` reason. They are coverage
evidence, not confirmed protocol mappings.

V2 safe UI action rows MUST be backed by a complete manifest before capture or
manager-runner execution. The manifest-facing fields are `action_id`,
`target_id`, `target_marker`, `pre_state`, `action`, `post_state`,
`recovery_expectation`, `mutates_business_data`,
`allowed_action_family` and `expected_action_result_markers`.
`mutates_business_data` MUST be `false`.

Safe UI action rows MAY set `action_frame_range` and `frame_range` to `null`
only when the action is explicitly unavailable, unsupported or still pending.
When both action and background traffic are present, `action_frame_range` MUST
describe the selected action candidate and `background_frame_ranges` MUST keep
surrounding refresh or idle frames visible instead of discarding them.

Accepted V2 safe-action output additionally requires compact proof evidence.
A joined `action_frame_range`, stable `normalized_hash` and accepted
`replay_status` are not sufficient by themselves unless the row also retains
accepted replay/probe evidence, `acceptance_evidence` links or an accepted
typed `side_channel_evidence` contract. Rows without that proof remain visible
as non-accepted action evidence with explicit reasons.

V3 mutation sandbox rows MUST be backed by a complete manifest before capture
review or publication. Required fields are `mutation_id`, `target_marker`,
`mutation_family`, `pre_state`, `action`, `post_state`,
`recovery_expectation`, `mutates_business_data=false` and
`expected_action_result_markers`. The only initially reviewed families are
`text_input`, `number_input`, `date_input`, `checkbox_toggle` and
`inert_button`; every row must target fixture-local markers and must not write
catalogs, documents, registers, settings storage, external files, network
resources or other business data. Missing fields, unsupported families,
unreviewed targets or any `mutates_business_data` value other than `false`
fail closed before capture or publication.

V3 mutation rows MAY be published as `candidate`, `rejected`, `blocked`,
`partial` or `timeout` with explicit reasons and compact evidence links.
Promotion to `accepted` additionally requires isolated mutation
`action_frame_range`, separated `background_frame_ranges` and
`recovery_frame_range`, stable normalization metadata, observed action result
markers, recovery proof and same-action replay, direct Python-manager probe or
accepted typed contract proof. Marker-only evidence and raw capture evidence
are never sufficient for accepted mutation protocol mappings.

Real demo mutation pilots are a separate disposable-demo layer. They MAY set
`mutates_business_data=true` only when the row explicitly names the demo10413
lab scope, target marker, live pre-state, expected post-state, recovery or
cleanup plan, residual risk and owner route. A real demo row with theoretical
recovery only, missing live active-form evidence, missing selected object or
register-row pre-state, unapproved external side effects, or no owner-safe
action/recovery wrapper MUST fail closed before execution. Publication MAY
retain such rows as `blocked`, `rejected`, `candidate`, `partial` or `timeout`
with compact evidence links, but accepted output remains empty until the same
mutation also has isolated action/background/recovery ranges, deterministic
recovery or rerun proof and one accepted proof class for the same action.

V4 dialog, expected-error and bounded-wait rows MUST be backed by a complete
manifest before capture review or publication. Required fields are
`dialog_scenario_id`, `scenario_family`, `target_marker`, `dialog_family`,
`dialog_lifecycle`, `expected_text_marker`,
`expected_dialog_result_marker`, `pre_state`, `action`, `post_state`,
`recovery_expectation`, `mutates_business_data=false` and
`expected_action_result_markers`. `expected_error` rows additionally require
`expected_diagnostic_marker`; bounded wait rows additionally require
`bounded_duration_ms`. Every V4 row must target fixture-local markers and must
not use OS dialogs, files, network, print, clipboard, business documents,
catalogs, registers or persisted settings. Missing fields, unsupported
families, unreviewed targets or any `mutates_business_data` value other than
`false` fail closed before capture or publication.

V4 rows MAY be published as `candidate`, `rejected`, `blocked`, `partial`,
`timeout` or `expected_error` with explicit reasons and compact evidence links.
Promotion to `accepted` additionally requires separated dialog/action,
background and recovery frame ranges, stable normalization metadata, observed
dialog/result markers, recovery/rerun proof and V4-specific replay, direct
Python-manager probe or accepted typed contract proof. Marker-only UI evidence
and raw capture evidence are never sufficient for accepted V4 protocol
mappings.

## Replay And Probe Status

`replay_status` is required before a mapping can be used as working protocol
knowledge.

| Status | Meaning |
| --- | --- |
| `accepted` | Replay or direct Python-manager probe reproduced the expected read-only result or safe non-mutating action. |
| `accepted_side_channel` | Manager harness side-channel evidence matched a typed acceptance contract while frame range and normalized hash were retained. |
| `rejected` | Replay/probe reached the client but produced a protocol-level or API-level rejection. |
| `partial` | Replay/probe returned useful data but missed fields, required fallback frames or changed state assumptions. |
| `timeout` | Replay/probe did not complete within the recorded timeout budget. |
| `unsupported` | The current Python manager cannot safely exercise this operation yet. |
| `pending` | Capture and normalization exist, but replay/probe has not been attempted. |

Only `accepted` and `accepted_side_channel` rows should be used as confirmed
dictionary entries. `accepted_side_channel` rows confirm the manager harness
diagnostic contract, not a direct wire marker. Other statuses remain useful
evidence, but they must be treated as hypotheses or known gaps.

## Proof Classes By Risk Tier

Three proof classes are recognized for promotion decisions:

1. same-action replay against a fresh TestClient;
2. direct Python-manager probe of the same operation shape;
3. accepted typed contract proof, including manager side-channel contracts.

The minimum acceptance proof depends on the risk tier of the row. Reviewers
MUST NOT require more proof classes than the tier minimum; repeated
pending-promotion loops that wait for a second proof class on a low-risk row
are process waste, not added safety.

| Risk tier | Rows | Minimum acceptance proof |
| --- | --- | --- |
| `read_only` | read-only context, structure and property rows | Any one proof class, plus the stable normalized hash, frame range and marker facts already required above. |
| `safe_ui_action` | V2 allowlisted non-mutating actions | Any one proof class, plus isolated action/background frame ranges, manifest completeness and recovery expectation. |
| `mutation` / `dialog` | V3 mutation and V4 dialog rows | Any one proof class for the same action, plus isolated action/background/recovery ranges and deterministic recovery/rerun proof. Marker-only or capture-only evidence is never sufficient. |

A second proof class is always welcome additional evidence, but it is not an
acceptance gate. When the only available class is a typed side-channel
contract, the row is promoted as `accepted_side_channel` and must keep the
boundary that it is not a direct wire marker claim.

## Live Runtime Preflight

Live capture, replay and probe runs MUST pass the live runtime preflight
before any 1C process is started or attached:

- `scripts\preflight-live-runtime.ps1 -Mode capture` before capture runs that
  start their own TestClient/proxy/manager processes;
- `scripts\preflight-live-runtime.ps1 -Mode attach` before direct probe or
  replay runs against an already-running TestClient.

The preflight writes a compact `preflight_result.json`. A failed preflight is
a `runtime_gap` outcome recorded before execution, not a mid-card discovery.
`tools\protocol-research\run_protocol_capture.ps1` runs the capture-mode
preflight automatically and fails closed before process startup.

## Direct Probe Evidence

Direct Python-manager probing is valid replay evidence when it is represented
as a compact reviewed link. A corpus row MAY include `probe_evidence` with:

- `status`: one replay/probe status from the table above;
- `kind`: `direct_python_manager`, `replay` or another reviewed probe family;
- `query` or `case_family`: the read-only operation or family confirmed by
  the probe;
- `evidence_path`: repository-relative compact evidence path under
  `docs/protocol-research/evidence/`;
- `source_capture_id` or `probe_id`: short identifier for the capture/probe
  run;
- `response_markers`: markers observed by the probe and used for review;
- `notes`: limitations such as missing request-frame evidence or ambiguous
  case joins.

Rows MUST NOT embed raw probe stdout, raw response payloads, process logs or
local secrets. Full probe output remains under ignored runtime paths.

A read-only row may be promoted to `accepted` only when:

- repeated corpus rows for the same `case_id` have the same non-null
  `normalized_hash`;
- `frame_range`, request/response sizes, dynamic fields, operation token and
  response markers are retained;
- direct probe or replay evidence confirms the same operation and expected
  response markers;
- the row or comparison report links the compact probe evidence path.

A safe UI action row may be promoted to `accepted` only when the read-only
acceptance facts are available for the action request shape and the row also
retains `action_id`, `target_id`, `target_marker`,
`mutates_business_data=false`, `allowed_action_family`,
`action_frame_range`, separated `background_frame_ranges`, pre-state,
post-state, recovery expectation, expected action result markers and observed
action result markers for the same non-mutating action.

A V3 mutation row may be promoted to `accepted` only when it retains a complete
mutation manifest, isolated action/background/recovery frame ranges, recovery
and rerun proof, observed action result markers and replay, direct
Python-manager probe or accepted typed contract proof for the same
fixture-local mutation. Rows without that proof remain candidate or another
explicit non-accepted status.

A V4 dialog row may be promoted to `accepted` only when it retains a complete
V4 manifest, separated dialog/action, background and recovery frame ranges,
recovery and rerun proof, observed dialog/result markers and replay, direct
Python-manager probe or accepted typed contract proof for the same
fixture-local dialog, expected-error or bounded-wait scenario. Expected-error
rows must keep infrastructure failures separate from reviewed expected
diagnostics.

## Side-Channel Evidence

Manager fixture diagnostic rows MAY be promoted to `accepted_side_channel`
when the accepted fact is intentionally emitted by the manager harness instead
of appearing as a direct TestClient wire marker. Such rows MUST include:

- `acceptance_contract.kind`, currently `manager_result_preview_contains`;
- the expected side-channel marker;
- `side_channel_evidence.evidence_source`, normally
  `manager_case_event.after.result_preview`;
- the observed `result_preview`;
- joined manager/client frame ranges and a non-null `normalized_hash`;
- `validation_status: accepted` and an empty mismatch list.

These rows MUST NOT be described as direct wire marker observations. If the
project later adds a parser that extracts the same count from the binary
TestClient response, that parser should produce separate direct probe evidence.

A row with a stable normalized hash but no accepted replay/probe evidence
remains non-accepted, normally `pending`. A row with useful probe output but
missing request-frame or non-null hash evidence remains visible as `partial`,
`pending`, `incomplete_hash` in comparison evidence, or another explicit
non-accepted status with a `notes` reason.

## Semantic Enrichment Policy

`help-mcp`, `meta-mcp`, `config-mcp`, `bsl-mcp`, `admin-mcp` and `live-mcp` may
enrich corpus rows with object-model terms, form metadata, source-authoring
context, diagnostics, platform command evidence, read-only runtime checks,
element names, method names and type hints. That context is supporting evidence
only. Retired `edt-mcp` references are historical evidence only.

Approved semantic source boundaries and current readiness evidence are
documented in `docs/protocol-research/semantic-source-inventory.md`.

A semantic source cannot replace:

- captured manager-to-client and client-to-manager frames;
- the normalized dynamic-field list;
- the normalized request hash;
- replay or direct Python-manager probe status.

When semantic labels disagree with wire evidence, the row must keep the wire
evidence as primary and record the semantic mismatch in `notes`.

## Read-Only First Scope

The first accepted corpus scope is limited to read-only operations for:

- `TestedApplication`;
- `TestedClientApplicationWindow`;
- `TestedForm`;
- form elements and their basic properties.

Click, text input, command execution, navigation that mutates business data
and recovery behavior stay out of the accepted corpus until read-only
classification is repeatable and rollback behavior is documented.

The first non-mutating action layer is governed by
`docs/protocol-research/safe-ui-action-scope.md`. Safe UI action rows use
`safety_class: safe_ui_action`, keep transient UI state changes separate from
read-only evidence, and must not promote deferred read-only fixture or element
hash evidence into accepted action protocol knowledge.

Safe action case events add `action_start` and `action_end` side-channel
events around the normal `case_start`, `case_step`, `case_result` and
`case_end` sequence. These events record pre-state, action, post-state,
recovery expectation, action result markers and any separated background frame
ranges without injecting markers into the TCP stream.

V2 safe-action runners must fail closed when a manifest row is missing,
incomplete, has `mutates_business_data` set to anything other than `false`, or
uses an action family outside the allowlist in `safe-ui-action-scope.md`.

V3 mutation runners and reviewers must fail closed when a mutation row is
missing required manifest fields, targets an unreviewed marker, uses a family
outside the V3 mutation sandbox list or cannot prove reset/recovery back to the
V1 baseline. Candidate publication is allowed with explicit missing-proof
reasons; accepted publication is proof-gated.

V4 dialog runners and reviewers must fail closed when a dialog row is missing
required manifest fields, targets an unreviewed marker, uses a family outside
the V4 dialog/wait list, omits the expected diagnostic marker for an
expected-error row, omits the bounded duration for a wait row, or cannot prove
reset/recovery back to the V1 baseline. Candidate publication is allowed with
explicit missing-proof reasons; accepted publication is proof-gated.

## Reviewed Evidence Boundary

Reviewed evidence under `docs/protocol-research/evidence/` may include:

- `corpus_cases.jsonl` or equivalent compact JSON rows;
- summary Markdown files;
- manifests with source capture identifiers and tool versions;
- normalized hashes, marker summaries and replay/probe outcomes.
- compact direct-probe evidence links and accepted-mapping summaries;
- mutation proof-decision summaries and empty accepted-mapping outputs when
  rows are intentionally candidate-only.
- V4 dialog/wait manifest samples and expected-error review summaries when
  rows are intentionally candidate-only.

Reviewed evidence must reference the runtime capture identifier instead of
embedding raw payloads. Runtime directories may be deleted and regenerated,
but reviewed rows should still explain which frames, normalizers and statuses
produced each protocol claim.
