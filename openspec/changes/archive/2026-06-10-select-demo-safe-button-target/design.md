## Context

The first focused V2 safe-action proof is published as candidate-only evidence.
It does not make real demo buttons safe by inference. This pilot therefore
starts by choosing one specific demo configuration button as a target for later
classification while preserving the V2 fail-closed boundary.

## Goals / Non-Goals

**Goals:**

- Identify one concrete demo form and button-like element for the pilot.
- Record enough target context for reviewers to understand what would be
  clicked if later changes permit execution.
- Preserve rejected, unavailable or ambiguous buttons as visible planning
  outcomes.

**Non-Goals:**

- Clicking the selected button.
- Proving any action protocol mapping.
- Treating fixture V2 candidate evidence as proof that demo buttons are safe.
- Selecting save, post, delete, fill, import, export, exchange or external
  side-effect commands.

## Decisions

- Prefer read-only discovery routes: Vanessa active-window/form tree, metadata
  context and static demo form inspection. The selection summary must state
  which route was used and whether it observed the live target.
- Select at most one primary button. Additional buttons can be recorded as
  rejected or deferred candidates, but the downstream pilot should stay small.
- Require a target record with form path, element path, visible caption or
  marker, current enabled/visible state, likely command family, target owner
  and artifact paths.
- Fail closed when no target can be identified without ambiguity. A blocked
  selection summary is a valid result for this change.

## Risks / Trade-offs

- [Risk] A target found in metadata may be hidden or disabled at runtime.
  Mitigation: prefer runtime form-tree evidence when available and record
  residual risk when only static evidence exists.
- [Risk] A visually harmless caption can mask a business command. Mitigation:
  this change only selects a target; the classification change must review
  command semantics before any execution.
- [Risk] Demo data can vary by infobase. Mitigation: record infobase path,
  platform version and observed form/window markers in the selection summary.

## Migration Plan

- Review the demo configuration surface using read-only evidence.
- Write the target-selection summary and rejected-target notes.
- Hand the selected target to `classify-demo-button-safety-contract`.

## Open Questions

- Which demo form currently exposes the safest visible target in the local
  `vanessa_client` infobase?
- Is runtime form-tree evidence available in the delivery session, or must
  classification start from static metadata only?
