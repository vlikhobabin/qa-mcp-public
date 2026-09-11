## Context

The pilot crosses from planning into live runtime behavior only after target
selection and safety classification have completed. The capture path must
protect the local infobase, clean only owned processes and preserve enough
evidence to distinguish a safe candidate from a V3 mutation blocker.

## Goals / Non-Goals

**Goals:**

- Execute zero or one reviewed demo-button row.
- Preserve pre/action/post/recovery phase evidence and capture summaries.
- Fail closed when safety gates are incomplete or runtime state does not match
  the manifest.
- Record blocked or rejected results as valid pilot outcomes.

**Non-Goals:**

- Clicking unknown business buttons.
- Attempting rollback-dependent business mutations.
- Promoting accepted mappings from capture evidence alone.
- Committing raw TCP captures, platform logs or generated replay payloads.

## Decisions

- Treat the classification manifest as the only executable input. If it is
  missing, incomplete or unsafe, write a blocked summary and stop before click.
- Re-read the active form/window and target marker immediately before action.
  Mismatch between expected and observed pre-state fails closed.
- Retain phase labels separately: pre-read, action-start, action-end,
  post-read and recovery or recovery-read.
- Keep raw runtime output in ignored runtime paths and publish only compact
  summaries in reviewed artifacts or docs.
- Any failure after a permitted click must run the documented recovery route
  when it is safe to do so and record the final state.

## Risks / Trade-offs

- [Risk] Live demo state can drift after classification. Mitigation: pre-state
  recheck gates execution.
- [Risk] Recovery may be unavailable after a partial action. Mitigation: the
  manifest must define recovery expectation before execution; missing recovery
  blocks capture.
- [Risk] Candidate capture can be mistaken for accepted protocol knowledge.
  Mitigation: publication must keep accepted status proof-gated by replay,
  direct probe or typed contract evidence.

## Migration Plan

- Load the classification decision.
- If capture-eligible, run the Windows-native guarded capture once.
- If not capture-eligible, retain a blocked summary without clicking.
- Pass compact capture or blocked evidence to
  `publish-demo-button-safe-action-decision`.

## Open Questions

- Which run id should be assigned when the pilot stops before click because the
  selected target is unsafe or unavailable?
