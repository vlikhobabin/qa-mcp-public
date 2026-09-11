## Context

The selected target may be a visible button, but V2 safe-action policy only
allows reviewed non-mutating action families. Text input, checkbox/value
toggles, business command clicks, writes and external side effects stay outside
V2. This change decides whether the selected target can proceed to a guarded
capture or must be routed to V3 mutation work.

## Goals / Non-Goals

**Goals:**

- Classify the selected target before execution.
- Produce a complete manifest row only when `mutates_business_data=false` is
  justified and the action family is allowlisted.
- Record explicit V3 routing when the button is mutating, business-owned or
  requires rollback.

**Non-Goals:**

- Clicking the button.
- Accepting a protocol mapping.
- Broadening V2 to include business command clicks or generic button actions.

## Decisions

- Classification outcomes are `safe_ui_action`, `inert_local_action`,
  `business_mutation`, `unsupported` and `blocked`.
- A row can proceed to capture only when it satisfies the V2 manifest contract:
  target marker, pre-state, concrete action, post-state, recovery expectation,
  expected action result markers, allowlisted family and
  `mutates_business_data=false`.
- Treat `inert_local_action` as capture-eligible only when evidence proves the
  button updates transient UI state or local markers without business writes,
  external side effects or rollback needs. Otherwise route it to V3.
- Any unknown command, object write, save/post/delete/fill/import/export,
  exchange, print, file, network or persisted settings behavior fails closed.

## Risks / Trade-offs

- [Risk] Static metadata can miss runtime side effects. Mitigation: require the
  classification evidence to state source confidence and residual risk.
- [Risk] An inert-looking demo command may still mutate business data.
  Mitigation: require `mutates_business_data=false` justification and a
  recovery expectation before capture.
- [Risk] A safe classification can be misread as accepted protocol proof.
  Mitigation: classification only gates capture; accepted status still requires
  frame and replay/probe or typed contract evidence.

## Migration Plan

- Read the target-selection summary.
- Review command semantics using read-only evidence.
- Publish a classification decision and manifest row, or publish a V3 routing
  decision.
- Hand only capture-eligible rows to
  `capture-demo-button-safe-action-pilot`.

## Open Questions

- Can the chosen demo button be tied to a transient UI action family, or does
  its command semantics force a V3 mutation route?
