## Context

The package reads `QA_MCP_*` variables from several modules. Some values are
captured at import time and others are parsed per call, so tests and operators
cannot reason about runtime policy from one place. The most visible duplicates
are remote-client truth parsing and OData defaults.

## Goals / Non-Goals

**Goals:**

- Add one settings model and accessor for supported qa-mcp environment values.
- Keep default values and public CLI/MCP behavior unchanged.
- Centralize remote-client boolean parsing and OData defaults.
- Provide tests that isolate environment changes without process restarts.

**Non-Goals:**

- Do not add new required environment variables.
- Do not change live provider credentials or local `.ai/*.env` files.
- Do not convert every constant in the codebase if it is not backed by
  `QA_MCP_*`.

## Decisions

- Implement `Settings.from_env(env: Mapping[str, str] | None = None)` in
  `src/qa_mcp/config.py`. Passing an explicit mapping keeps tests deterministic.
- Add lightweight module-level accessors only where a module genuinely needs
  lazy per-call environment reads.
- Move OData defaults to the settings module and import them from both the OData
  client and regression CLI.
- Keep remote-client parsing permissive only for the values the current code
  treats as true; document false/default behavior in tests.

## Risks / Trade-offs

- Import-time settings can preserve existing behavior but hide runtime changes
  -> prefer per-call accessor for values that already had per-call semantics.
- A broad sweep can cause unrelated churn -> migrate only `QA_MCP_*` reads and
  duplicates named in the card.
- OData default changes can break external scripts -> assert the exact old
  default values in tests.

## Migration Plan

1. Add settings model and tests for boolean/default parsing.
2. Migrate remote-client and OData duplicate parsing.
3. Migrate remaining `QA_MCP_*` reads in small groups.
4. Run focused config tests and full pytest.

## Open Questions

- none
