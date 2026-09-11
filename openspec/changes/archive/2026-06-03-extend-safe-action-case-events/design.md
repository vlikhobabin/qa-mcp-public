## Context

`protocol_corpus_runner.py` and related comparison tooling currently preserve
read-only case rows and side-channel case events. Safe action captures need a
more detailed event model because the relevant frames may be surrounded by
active-window refresh, form refresh or idle traffic.

This change prepares the offline tooling layer before live action capture. It
extends compact reviewed evidence without changing raw capture ownership or
process cleanup behavior.

## Goals / Non-Goals

Goals:

- Add action case event fields for pre-state, action, post-state, recovery
  expectation and action result markers.
- Preserve action-specific frame-range candidates separately from background
  refresh traffic.
- Extend compact rows with safe action fields while retaining the existing
  corpus evidence fields: case id, API call, target, frame range,
  normalized hash, dynamic fields, operation token, response markers and
  replay status.
- Add offline tests for event parsing, unsupported action status handling and
  refresh-noise separation.

Non-goals:

- Do not run live action capture in this change.
- Do not accept safe action mappings.
- Do not add write/action package APIs.
- Do not rewrite historical read-only evidence rows.

## Decisions

### Extend Rows Additively

Action rows should add fields such as `pre_state`, `action`,
`post_state`, `recovery_expectation`, `action_result_markers` and
`refresh_frame_ranges` without removing existing read-only fields. Existing
tools can then detect the schema and ignore action-only fields when comparing
read-only evidence.

Alternative considered: create an unrelated action row schema. That would
avoid mixed rows but would duplicate normalizer and replay/probe evidence
contracts.

### Keep Background Refresh As Evidence, Not Noise

The analyzer should record background refresh ranges separately from the
action-related range instead of dropping them. Reviewers need to see whether
the action boundary was clean or whether frames were filtered.

Alternative considered: discard frames outside the action marker window. That
would hide timing and refresh ambiguity that may explain replay failures.

### Offline Verification First

The implementation should use fixture events or synthetic case rows to prove
classification behavior before a Windows runtime capture is required. This
matches the package and protocol-tool policy in `openspec/config.yaml`.

## Risks / Trade-offs

- Action marker timing may not align exactly with TCP chunk counters ->
  mitigate by preserving both candidate action ranges and refresh ranges.
- Additive row fields may grow the evidence contract -> mitigate with focused
  docs and tests for the action schema.
- Existing comparison tools may not understand action rows -> mitigate by
  adding explicit status handling instead of relying on read-only defaults.

## Migration Plan

Existing evidence remains unchanged. New action evidence should use a new
evidence id and should not rewrite historical read-only corpus output.

## Open Questions

- Whether action capture will use a new `safe-action` seeded case set or a
  custom JSON manifest supplied to the existing runner.
- Which result markers are stable enough for menu expansion and tab switching
  before direct replay/probe evidence exists.
