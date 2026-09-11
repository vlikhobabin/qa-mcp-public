## Context

Downstream V2 cards need a shared manifest shape before they add fixture-side
safe-action markers or manager-side execution. Without a manifest contract,
the client fixture could define targets one way, the manager harness could run
actions another way, and evidence tooling could classify candidate rows with
incomplete safety facts.

The existing `safe-ui-action-scope.md` already names a first safety class and
some allowed action families. This change sharpens that scope into fields that
must appear before V2 work can execute an action.

## Goals / Non-Goals

Goals:

- Define a V2 manifest row shape with stable identifiers, target markers,
  pre/post state, recovery expectation, safety flag, allowlisted family and
  expected result markers.
- Make `mutates_business_data=false` mandatory for V2 rows.
- Keep the allowed family list small and reviewable.
- Make excluded mutation/action families fail closed before capture.

Non-goals:

- Do not create client fixture markers or manager harness actions.
- Do not capture or replay safe-action traffic.
- Do not design V3 mutation rollback semantics.
- Do not accept V2 action protocol mappings.

## Decisions

### Manifest Rows Must Be Complete Before Execution

Each V2 row should carry all review fields before the manager runner executes
it. This avoids collecting action traffic whose target, expected result or
recovery route is unclear.

Required row fields:

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

### Allowed Families Are Explicit, Not Pattern-Matched

V2 should accept only these first families:

- `focus_existing_element`
- `activate_existing_window_or_form`
- `switch_fixture_page`
- `select_local_table_row`
- `expand_or_collapse_menu_or_group`

The exact string names may be refined during implementation, but the semantic
set should stay within those five families. Anything outside the set is not a
V2 safe action.

### Exclusions Route To Later Cards

Text input, checkbox/value toggles, business command clicks, object writes,
save, post, delete, fill, import, export and external side effects belong to
later mutation or recovery cards. Even if a command appears inert in the demo
fixture, V2 should not accept it unless the manifest classifies it as one of
the allowed non-mutating families.

## Risks / Trade-offs

- A strict manifest may delay useful experiments. Mitigation: V2 is a safety
  boundary; unsupported rows can be recorded as blocked or routed to V3/V4.
- Table row selection can be ambiguous if selection changes local fixture
  state. Mitigation: require local-only target markers, post-state markers and
  recovery expectation.
- Menu expansion can accidentally execute a command if modeled poorly.
  Mitigation: allow expand/collapse of menu/group state only, not command item
  execution.

## Migration Plan

No migration is required. Implementation updates docs and evidence contract
wording only. Downstream cards should then implement fixture and manager
manifest consumers against this contract.

## Open Questions

- Whether row field names should be represented as JSON Schema in a later
  tooling card or remain documented Markdown until the first V2 runner exists.
- Whether `activate_existing_window_or_form` should split into separate window
  and form families once the manager runner has concrete API calls.
