## Context

The V4 surface model defines markers, but protocol research still needs
runtime-visible scenarios that exercise complex UI behavior. The first
scenario layer must stay deterministic, bounded and fixture-local so error and
wait traffic can be reviewed separately from infrastructure failures.

## Goals / Non-Goals

**Goals:**

- Implement warning, question and fixture-owned modal scenarios with stable
  visible text and `PF_*` result markers.
- Implement expected-error scenarios whose diagnostic text is controlled and
  distinguishable from capture infrastructure failures.
- Implement bounded wait/progress scenarios with observable start, progress,
  completion, cancel and timeout markers.
- Keep every scenario resettable to the V1 baseline.

**Non-Goals:**

- Unbounded waits, background jobs or asynchronous external services.
- OS dialogs, file dialogs, printing or platform portability claims.
- Business command execution or writes to application data.

## Decisions

- Keep wait/progress behavior bounded by a fixed fixture-local duration and a
  named timeout marker. That makes waits reproducible and prevents runaway
  capture sessions.
- Emit controlled expected errors through fixture-local commands and label them
  as expected results. Infrastructure errors remain separate and must not be
  hidden behind the expected-error marker.
- Use fixture-owned modal forms rather than external platform dialogs. This
  gives the lab reset control and avoids OS cleanup risks.
- Treat cancel and retry as explicit scenario outcomes rather than incidental
  UI cleanup. Each outcome gets its own result marker.

## Risks / Trade-offs

- [Risk] Expected errors could mask real failures.
  [Mitigation] Require expected diagnostic markers and keep infrastructure
  failure markers separate in evidence.
- [Risk] Bounded waits may still overlap with background refresh traffic.
  [Mitigation] Require start/progress/completion markers and isolate action
  ranges during recovery verification.
- [Risk] Modal lifecycle can differ across platform builds.
  [Mitigation] Retain platform version in evidence and avoid portability claims
  until repeated proof exists.

## Migration Plan

- Add scenarios only after the V4 marker model is available.
- Verify each scenario independently before adding it to corpus manifests.
- Disable or remove individual scenario commands if recovery evidence fails.

## Open Questions

- What maximum wait duration should be used for the first proof: short enough
  for tests, but long enough to produce observable progress frames?
- Should expected-error scenarios use a single generic diagnostic command or
  one command per error family?
