## Context

Safe action captures need a final classification pass before they can change
protocol knowledge or Python-manager descriptors. This change consumes compact
action evidence, compares frame ranges and hashes where repeated rows exist,
and attempts replay or direct Python-manager probing only for actions that can
be exercised without business-data mutation.

The existing read-only comparison rules provide the pattern: accepted mappings
require stable reviewed wire evidence and accepted replay or probe status.
Safe action mappings add pre/post-state and action result markers to that
gate.

## Goals / Non-Goals

Goals:

- Classify every safe action row as accepted, pending, unsupported, partial,
  timeout, rejected or blocked.
- Separate action frames from background refresh frames before considering a
  row accepted.
- Attempt replay or direct Python-manager probing for at least one supported
  non-mutating action when current tooling can do so safely.
- Publish accepted or unresolved safe-action evidence with lineage back to
  capture ids and compact row paths.

Non-goals:

- Do not accept mappings from a single ambiguous capture with no replay/probe
  confirmation.
- Do not add text input, command execution, write or rollback semantics.
- Do not rewrite historical read-only or action capture evidence.
- Do not promote package descriptors when evidence remains unresolved.

## Decisions

### Use Read-Only Acceptance Rules Plus Action Markers

An accepted safe action mapping must retain frame range, normalized hash,
dynamic fields, operation token, response markers and replay/probe status,
plus pre-state, post-state, recovery expectation and action result markers.
This keeps action acceptance comparable with the read-only dictionary while
making UI state transition evidence explicit.

Alternative considered: accept action rows from successful Vanessa scenario
logs alone. That would prove the scenario ran but not that the native protocol
request shape is stable or replayable.

### Publish Unresolved Action Rows Deliberately

Rows with unsupported targets, ambiguous refresh traffic, missing hashes or
failed probes should be published as unresolved evidence with owner routes.
They remain useful research output but cannot become working protocol
knowledge.

Alternative considered: omit failed rows from accepted-mapping output only.
That would lose the reason future protocol passes need to fix.

### Keep Replay/Probe Narrow

Replay or direct Python-manager probing should only exercise the selected
non-mutating action and should not attempt to recover by running commands or
writes. If the current package lacks a safe probe path, the row stays
`unsupported` or `pending`.

## Risks / Trade-offs

- Single-run action evidence may not prove hash stability -> mitigate by
  classifying as non-accepted unless repeated evidence or direct proof is
  sufficient.
- Replay tooling may not support action frames yet -> record a provider or
  project gap instead of forcing acceptance.
- Background refresh can mimic action markers -> require separate refresh
  ranges and action result markers before acceptance.

## Migration Plan

Implementation writes new comparison, classification and accepted-mapping
evidence directories. Existing read-only package descriptors remain unchanged
unless a safe action descriptor is explicitly evidence-backed.

## Open Questions

- Which action family can be probed directly without introducing write or
  command semantics.
- Whether accepted safe action descriptors should live beside read-only
  descriptors or in a separate action contract once evidence exists.
