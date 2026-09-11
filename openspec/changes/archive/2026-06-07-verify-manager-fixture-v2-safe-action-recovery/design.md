## Context

The runner can execute candidate actions and emit boundaries, but V2 remains
unsafe unless the lab proves that focus/page/row/menu state can be restored or
explicitly left in a documented known state.

## Goals / Non-Goals

**Goals:**

- Verify recovery for every executable V2 safe-action row.
- Keep recovery traffic separate from candidate action evidence.
- Prove rerun determinism after recovery for the first supported subset.
- Preserve blocked or residual-risk labels when cleanup cannot be proved.

**Non-Goals:**

- Business rollback, reposting or object cleanup.
- V3 value mutation recovery.
- Protocol mapping acceptance without reporter/comparison proof.

## Decisions

- Treat recovery as required evidence for every action row. A row without
  recovery proof remains non-accepted even if the action appears to work.
- Prefer reset to the V1 baseline when possible, otherwise record a documented
  known state with residual risk.
- Require rerun proof for the first focused subset to catch hidden state
  leakage.
- Keep recovery markers in compact evidence instead of raw logs.

## Risks / Trade-offs

- [Risk] Reset can restore visual state but not hidden selected/focused state.
  [Mitigation] Read target markers after recovery and rerun a case.
- [Risk] Cleanup traffic can be mistaken for action traffic.
  [Mitigation] Record recovery frame ranges separately.
- [Risk] Some safe actions may not have reliable cleanup on the first platform
  build.
  [Mitigation] Keep those rows blocked or candidate with explicit owner route.

## Migration Plan

- Add recovery verification after boundary events are available.
- Run recovery proof on the smallest supported candidate set first.
- Keep incomplete rows candidate or blocked until proof exists.

## Open Questions

- Should `activate_existing_window_or_form` rows require restoring the exact
  original window or only any fixture-owned baseline window?
- How many reruns should be required before the first focused proof consumes a
  row?
