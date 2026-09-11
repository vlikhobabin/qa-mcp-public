## Context

The project is moving from read-only V1 coverage into a V2 safe-action layer.
That layer is intentionally narrow: focus/activation, existing window/form
activation, fixture page switching, local table row selection and menu/group
expand-collapse can be studied only when the manifest states that business data
is not mutated.

The current local protocol research skill says to prefer read-only operations
unless the user explicitly asks for write/action behavior. That is good as a
general safety rule, but it leaves too much room for V2: a user asking for a
click should not be enough to classify the click as safe V2 work.

## Goals / Non-Goals

Goals:

- Align `AGENTS.md` and local protocol research skills with the V2 manifest
  contract.
- Make V2 action planning fail closed when a manifest row is missing or outside
  the allowlist.
- Route mutating actions to later cards that include rollback/recovery design.
- Preserve Windows-first runtime cleanup rules.

Non-goals:

- Do not update global Codex skills outside this repository.
- Do not change MCP provider definitions.
- Do not implement any action runner behavior.
- Do not relax read-only safety rules for V1 or protocol evidence acceptance.

## Decisions

### User Intent Is Necessary But Not Sufficient

Explicit user intent can authorize planning for a UI action, but it cannot by
itself make the action a V2 safe action. The action also needs a reviewed V2
manifest row and must be within the allowlist.

### Agent Instructions Should Name The Exclusions

The safety instructions should list excluded families directly. Terms like
"click" are too broad in 1C: a click may focus an element, open a menu, run a
business command or mutate object state. V2 instructions should route broad or
ambiguous clicks to manifest review rather than executing them.

### Later Mutation Cards Own Rollback Semantics

Text input, checkbox/value toggles and business commands can be valid future
research, but only after V3/V4 cards define rollback, cleanup and recovery.
V2 instructions should point there instead of inventing ad hoc recovery.

## Risks / Trade-offs

- Overly strict instructions can slow exploratory work. Mitigation: allow
  explicit fixture-local manifest rows for the first V2 families.
- Under-specified instructions can produce unsafe captures. Mitigation: require
  `mutates_business_data=false` and expected result markers before execution.
- Skill updates can diverge from docs. Mitigation: keep wording tied to
  `docs/protocol-research/safe-ui-action-scope.md`.

## Migration Plan

No migration is required. During implementation, update local instructions in
place and preserve existing cleanup, evidence and raw-runtime boundaries.

## Open Questions

- Whether downstream cards should add a small lint/check for prohibited V2
  action family names in manager manifests.
