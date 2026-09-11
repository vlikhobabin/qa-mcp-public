## Context

Version-family selection is shared by bundled protocol assets and regression
tools. The implementation currently lives in `regression.versioning`, while
protocol modules use lazy imports to avoid a cycle because regression code also
imports protocol lifecycle helpers.

## Goals / Non-Goals

**Goals:**

- Move active version-family selection into a cycle-free `qa_mcp.versioning`
  leaf module.
- Keep `regression.versioning` as a compatibility re-export for callers.
- Replace protocol lazy imports with normal top-level imports.
- Preserve existing accepted environment values and unsupported-version errors.

**Non-Goals:**

- Do not change bundled asset layout or add a new platform family.
- Do not change capture selection defaults.
- Do not remove regression-facing compatibility imports in this change.

## Decisions

- The new module owns pure parsing/detection helpers only. It must not import
  `protocol`, `regression` or runtime-heavy modules.
- `regression.versioning` imports and re-exports the leaf helpers, retaining any
  regression-only wrappers in place if needed.
- Protocol modules import from `qa_mcp.versioning` at top level. Lazy import
  comments become unnecessary and are removed.

## Risks / Trade-offs

- Compatibility imports can hide stale call sites -> tests and `rg` checks must
  verify protocol callers import from the leaf module.
- Environment parsing can drift during the move -> keep focused tests for bare
  family values, full platform versions and unsupported versions.

## Migration Plan

1. Add `src/qa_mcp/versioning.py`.
2. Re-export from `src/qa_mcp/regression/versioning.py`.
3. Update protocol imports.
4. Run focused versioning tests and full pytest.

## Open Questions

- none
