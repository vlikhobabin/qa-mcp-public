# Safe UI Action Scope

This document defines the first non-mutating UI action layer for the native
1C TestManager/TestClient protocol lab. It is a safety gate for future capture
and replay work; it is not accepted action protocol evidence by itself.

Raw captures, generated replay payloads, process logs and full UI evidence
remain outside reviewed git changes. Compact reviewed protocol evidence stays
under `docs/protocol-research/evidence/`, and runtime output stays under
ignored `runtime/protocol-research/`.

## Safety Class

Safe UI action cases use `safety_class: safe_ui_action`.

This class is separate from `read_only` because the operation may change
transient UI state such as focus, active window, selected page or expanded menu
state. It must not write persisted business data.

V2 safe-action work is manifest-driven. A candidate action may be captured or
executed by a manager runner only after a reviewed manifest row states the
target, expected pre/post state, recovery route, allowed family and
`mutates_business_data=false`.

## Allowed First Action Families

The first V2 action matrix may include only these families:

| Action family | Allowed target | Expected state transition | Recovery expectation |
| --- | --- | --- | --- |
| `focus_existing_element` | Existing visible form element | Focus or active element changes without editing the value | Return focus to the previous safe element when possible |
| `activate_existing_window_or_form` | Already opened TestClient window or form | Active window/form changes without opening a new business operation | Reactivate the original window/form when possible |
| `switch_fixture_page` | Existing fixture tab or page on the active form | Selected fixture page changes without running a command | Switch back to the original fixture page |
| `select_local_table_row` | Existing local fixture table row with no persisted edit behavior | Selected row marker changes without editing table data | Reselect the baseline row or reset the fixture state |
| `expand_or_collapse_menu_or_group` | Existing menu, command-bar menu or group that can expand/collapse without invoking a command | Menu/group state expands or collapses without executing an item | Collapse, restore baseline expansion, or leave via safe focus/window recovery |

If the current lab form does not expose a target safely, the candidate remains
`unsupported`, `pending`, `partial`, `timeout`, `rejected` or `blocked`; it is
not silently omitted.

## Excluded Mutation Families

The safe action matrix excludes:

- text input into persisted or potentially persisted fields;
- command execution with business side effects;
- business command clicks, even when reached through a visible button or menu;
- checkbox toggles and other value toggles;
- object writes or persisted settings changes;
- table row edits, selection commands that edit data, drag/drop or reorder;
- save, post, unpost, delete, create, fill, import or export commands;
- external side effects such as file, network, exchange, print or clipboard
  operations;
- navigation that opens a write workflow or changes persistent state;
- any operation that needs rollback, repost or data cleanup to restore the
  infobase.

Those cases require a separate V3/V4 mutation-specific card with explicit
rollback and recovery design. V2 runners must fail closed before capture or
execution when a row is outside the allowlist or lacks a complete manifest.

## V2 Manifest Row

V2 candidate rows must use this shape before capture or manager-runner
execution starts:

| Field | Required content |
| --- | --- |
| `action_id` | Stable slug for one V2 safe action, for example `safe-focus-existing-editfield`. |
| `target_id` | Stable target identifier from the fixture target map or manager manifest. |
| `target_marker` | Observable `PF_*` or equivalent marker proving the intended target is present. |
| `pre_state` | Observable state before the action, including active window/form and selected page, row or focus when relevant. |
| `action` | Concrete interaction path the manager runner will attempt. |
| `post_state` | Expected observable transient state after the action. |
| `recovery_expectation` | How the lab returns to a known state or why no cleanup is required. |
| `mutates_business_data` | Must be `false` for every V2 row. |
| `allowed_action_family` | One of the allowlisted V2 families above. |
| `expected_action_result_markers` | Compact markers that distinguish the action result from background refresh or unrelated UI traffic. |
| `case_id` | Optional corpus alias when different from `action_id`; legacy rows may use this as the stable case slug. |
| `api_call` | 1C testing API action under study. |
| `ui_target` | Window, form, element, page or menu target. |
| `safety_class` | `safe_ui_action`. |
| `prerequisite_status` | Accepted, deferred, unresolved, blocked or N/A for dependent read-only evidence. |
| `provider_owner` | `project:qa-mcp`, `/opt/vanessa-mcp-stack` or another explicit owner. |
| `residual_risk` | Short risk statement for deferred or unresolved prerequisites. |

Later compact evidence rows add frame ranges, normalized hashes, dynamic
fields, operation tokens, response markers, replay/probe status and action
result markers.

Rows missing `target_marker`, `pre_state`, `post_state`,
`recovery_expectation`, `mutates_business_data=false`,
`allowed_action_family` or `expected_action_result_markers` are incomplete and
must not be captured, executed or accepted.

## Prerequisite Gates

The current action layer inherits these read-only outcomes:

| Gate | Current outcome | Safe-action decision |
| --- | --- | --- |
| Manager fixture V1 read-only active-window/form mappings | Accepted for active-window and active-form rows in repeated/probe-backed evidence | May support selecting existing window/form targets. |
| Manager fixture V1 formerly pending rows | Accepted by 2026-06-06 follow-up contract-backed evidence: marker-contract proof for form marker, form summary, checkbox, button, table and group rows; typed side-channel contracts for diagnostic count/form-path rows | V1 read-only no longer blocks V2 planning. These rows support target review only; they do not prove action protocol behavior. |
| Controlled fixture target families such as `Button`, `Table`, `CommandBar`, `Page`, `CheckBox` and group/menu surfaces | Current manager fixture V1 route has accepted read-only target evidence where listed in `status-report-2026-06-06.md`; any package descriptor or alternate fixture gap remains explicit when selected | May be used as V2 candidate targets only when the V2 row records target marker, pre-state, post-state, recovery expectation and result markers. |
| `form-element-details` and `typed-input-field-readonly` package-descriptor hash gaps outside the manager fixture V1 closure | Published as unresolved/incomplete for current package descriptors | May inform target review, but cannot promote element action rows without fresh accepted action evidence. |

Deferred read-only evidence is allowed only when the candidate row records the
unresolved status, owner route and residual risk. Deferred evidence cannot be
upgraded into an accepted safe action mapping by inference.

The final V1 readiness state for current V2 planning is
`unblocked_by_v1_readonly`. That readiness removes the former V1 pending-row
blocker, but every V2 action candidate still needs its own safe-action proof.
Rows accepted through typed manager side-channel contracts remain side-channel
facts, not direct TestClient wire marker observations.

## Acceptance Boundary

A safe UI action row becomes working protocol knowledge only after later
capture and classification evidence proves the same non-mutating action with:

- pre-state, action, post-state and recovery expectation;
- action frame range separated from background refresh traffic;
- request/response sizes, normalized hash, dynamic fields and operation token;
- response markers and action result markers;
- accepted replay or direct Python-manager proof when feasible.

Rows without that proof remain unresolved action evidence.

## Current Focused Proof Status

The first focused V2 safe-action proof is published under:

`docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-publication/`

The proof executed two reviewed rows live and isolated action, background and
recovery frame ranges:

- `safe-switch-fixture-page-b`
- `safe-focus-existing-edit-string`

Both rows remain candidate. They have live phase evidence, request/response
sizes, dynamic-field metadata and normalized hash candidates, but no accepted
same-action replay, direct Python-manager probe or typed contract proof.
The accepted-mapping output for
`manager-fixture-v2-first-focused-proof-20260607` is intentionally empty.

This candidate proof does not unblock real demo buttons, text input, checkbox
or value toggles, business command clicks, object writes, persisted settings
changes or external side effects. Those remain later mutation/recovery work.
