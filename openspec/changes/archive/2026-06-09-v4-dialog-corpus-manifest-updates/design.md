## Context

The V2 safe-action and V3 mutation contracts require manifest rows with
pre-state, action, post-state and recovery expectations. V4 needs the same
fail-closed discipline plus fields for dialog family, expected text,
diagnostic markers, bounded waits and expected-error classification.

## Goals / Non-Goals

**Goals:**

- Define required V4 manifest fields before capture or publication.
- Keep expected errors visible as expected results only when diagnostic markers
  match.
- Publish compact evidence links and keep raw runtime material ignored.
- Align V4 rows with existing candidate/accepted/rejected/blocked/timeout
  gates.

**Non-Goals:**

- Implementing fixture handlers or recovery commands.
- Accepting any V4 protocol mapping from a single capture.
- Adding platform-version portability claims.

## Decisions

- Use one V4 row shape with a `scenario_family` field instead of separate
  ad hoc row types for warning, question, modal, expected error and wait. This
  keeps comparison tooling predictable while allowing family-specific fields.
- Require `mutates_business_data=false` for every V4 fixture row. A row that
  needs business data, external files, OS dialogs or background jobs is routed
  to a separate card.
- Require `bounded_duration_ms` for wait/progress rows and expected diagnostic
  markers for expected-error rows. Missing family-specific fields fail closed.
- Treat expected errors as a distinct result classification in reports while
  preserving infrastructure failure as a separate non-accepted outcome.

## Risks / Trade-offs

- [Risk] One manifest shape may contain fields that are not relevant to every
  family.
  [Mitigation] Define family-specific required fields and explicit N/A markers
  instead of omitting safety-critical data.
- [Risk] Reporter changes could regress V1/V2/V3 output.
  [Mitigation] Keep V4 fields scoped to V4 rows and validate existing reports
  during implementation.
- [Risk] Expected-error classification could hide infrastructure failures.
  [Mitigation] Require diagnostic markers and publish mismatch reasons.

## Migration Plan

- Add V4 manifest docs and sample rows after V4 scenario families are defined.
- Extend reporters or comparison tooling only behind V4 row detection.
- Keep existing V1/V2/V3 corpus rows unchanged.

## Open Questions

- Should V4 report status include a first-class `expected_error` status, or
  should expected errors remain accepted/candidate rows with a result subtype?
- Which docs should own the durable V4 row contract: corpus evidence contract,
  protocol corpus runner docs, or a dedicated V4 fixture page?
