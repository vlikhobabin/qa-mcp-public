## Context

The architecture review identified dead helpers and exact duplicate utilities.
CR-03 changed part of the dead-code picture: `create_splice` is already gone and
`_splice_window_activate_command` is live through label-locate retry, so cleanup
must be based on current references rather than the original broad list.

## Goals / Non-Goals

**Goals:**

- Remove only verified-dead symbols and exact duplicate helpers.
- Preserve live retry helpers and any module still imported on a live path.
- Keep cleanup after the larger replay/server/version/settings refactors so
  dead references are easier to prove.

**Non-Goals:**

- Do not remove `_splice_window_activate_command`.
- Do not remove `mutation.py` unless `native_mutation` is proven not to be a
  live path or its dependency is replaced safely.
- Do not change protocol behavior or public MCP result shapes.

## Decisions

- Use source search and tests as the acceptance proof for dead symbols.
- Treat duplicate helpers as eligible only when signatures and behavior are
  equivalent or when call sites can be adjusted with focused tests.
- Leave a residual note in tasks/card result when an item is intentionally kept
  because it remains live.

## Risks / Trade-offs

- Deleting a private helper can break runtime-only paths -> require full pytest
  and source checks; keep optional live-regression as additional evidence.
- Some duplicates are similar but not identical -> do not collapse them unless
  tests prove equivalence.
- Removing `mutation.py` may be unsafe if `native_mutation` remains live ->
  explicitly verify before deleting or leave it in place.

## Migration Plan

1. Re-run source searches against current code after the prior refactor changes.
2. Delete verified-dead symbols.
3. Collapse exact duplicate helpers with tests.
4. Run source checks and full pytest.

## Open Questions

- Whether `mutation.py` remains a live dependency after the prior refactors.
