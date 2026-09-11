## Context

Client fixture V2, manager fixture V2 runner and V2 safe-action tooling are
archived. The current manager V2 publication delivered compact candidate
evidence with `accepted_count=0`, so the first focused proof must choose a
small candidate subset and keep every selected row inside the documented V2
safety boundary.

## Goals / Non-Goals

**Goals:**

- Choose the smallest useful manager fixture V2 action subset for first proof.
- Prefer `switch_page` and then `focus_element` when both are complete and
  reviewable.
- Preserve rejected, unsupported or deferred rows with owner and residual risk.
- Hand a reviewed manifest or selection summary to the live capture change.

**Non-Goals:**

- Executing live 1C actions.
- Accepting protocol mappings.
- Selecting text input, checkbox/value toggles, business command clicks, real
  demo buttons or persisted data mutations.

## Decisions

- Treat `switch_page` as the first candidate when its row is complete because it
  is fixture-local and has clear page-state markers. If it is not executable,
  select the next safest reviewed row and record why the preferred row was
  deferred.
- Limit the first subset to two rows. More rows increase review noise before the
  first action-frame proof path is understood.
- Store raw source catalogs under existing runtime or artifact locations and
  publish only a compact reviewed selection. The subset selection is evidence
  input, not protocol proof.
- Fail closed on missing target marker, pre-state, post-state, recovery
  expectation, action result marker, safety flag or allowlist family.

## Risks / Trade-offs

- [Risk] A visually harmless row can still drift from the client fixture target
  map. [Mitigation] Require target-map and manager-catalog cross-checks before
  selection.
- [Risk] Selecting two rows could hide a first-row failure. [Mitigation] Keep
  row status independent and allow the capture step to execute only the first
  row if the second is unsafe.
- [Risk] Candidate rows can be misread as accepted proof. [Mitigation] Label the
  output as focused input only and keep accepted status out of this change.

## Migration Plan

- Review archived V2 target-map, catalog and tooling manifest outputs.
- Write the focused selection summary and any deferred-row notes.
- Pass the reviewed subset to `capture-focused-v2-safe-action-run`.

## Open Questions

- Which concrete run id should be used for the first live focused proof?
- If `switch_page` is blocked, should the first row fall back to `focus_element`
  only or wait for catalog repair?
