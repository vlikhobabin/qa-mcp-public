## Context

V1, V2 and V3 define read-only, safe-action and local-mutation fixture
surfaces. V4 adds complex UI behavior: warnings, questions, modal forms,
expected errors, waits and recovery paths. Those scenarios need a common
state model first so later changes can add handlers and evidence without
inventing marker names case by case.

## Goals / Non-Goals

**Goals:**

- Define fixture-local dialog lifecycle markers for baseline, opened,
  answered, closed, failed and recovered states.
- Define deterministic text markers for warning, question and modal-form
  scenarios.
- Keep the reset path aligned with the V1 baseline and V3 recovery model.
- Record safety classification before any runtime action is executed.

**Non-Goals:**

- Implementing dialog handlers or running captures.
- Supporting OS, file, print, mail, crypto or external-service dialogs.
- Accepting protocol mappings or changing Python manager behavior.

## Decisions

- Store V4 dialog state in the fixture form module, following the V3 local
  state pattern. This keeps all state resettable with the fixture and avoids a
  persistence layer.
- Use explicit markers such as dialog family, lifecycle state, expected text
  marker and recovery marker instead of relying on visible captions alone.
  Captions may be localized or platform-shaped, while `PF_*` markers give
  stable evidence anchors.
- Treat modal forms as fixture-owned managed forms only. OS dialogs and file
  dialog result APIs stay out of this card because their cleanup and platform
  behavior need separate evidence.
- Classify every V4 scenario before implementation. A scenario that cannot
  declare `mutates_business_data=false`, bounded lifetime and recovery
  expectation fails closed.

## Risks / Trade-offs

- [Risk] Marker names could drift from V2/V3 naming conventions.
  [Mitigation] Keep marker names in one state model and verify the full marker
  set during reset evidence.
- [Risk] Modal forms can accidentally become business workflow examples.
  [Mitigation] Keep forms fixture-owned, local and isolated from business
  objects.
- [Risk] Dialog lifecycle state may not capture all platform events.
  [Mitigation] Start with observable fixture markers and leave platform API
  expansion to targeted follow-up cards.

## Migration Plan

- Add the state model before handler work.
- Keep existing V1/V2/V3 markers unchanged.
- Roll back by removing the V4 marker set before any handler depends on it.

## Open Questions

- Should modal-form markers include a separate active-window title marker, or
  is a fixture-owned form marker enough for the first V4 proof?
- Which exact `PF_*` names should be reserved for wait/progress state so they
  do not collide with V3 mutation counters?
