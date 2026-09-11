## Context

OSS-01 created the common executor contract. After OSS-04C an application can
carry a target, but operation results and artifacts do not yet enforce or
retain target/session identity.

## Goals / Non-Goals

**Goals:**
- Gate MCP and scenario execution once at the common boundary.
- Stamp all verdicts and artifacts with bounded provenance and policy.

**Non-Goals:**
- Create lifecycle attachment/session state.
- Change tool schemas or concrete protocol/display handlers.
- Run live 1C verification.

## Decisions

1. Compare application target, session target and attachment generation before
   `QAExecutor.execute`; tool-by-tool checks were rejected as drift-prone.
2. Preserve existing executor protocol signatures and stamp returned results in
   the common wrapper, keeping downstream fake executors compatible.
3. Strip physical artifact paths for `sanitized`; retain bounded paths only for
   approved `full_local`.

## Risks / Trade-offs

- [Older fake executors omit identities] → The common wrapper supplies them and
  contract tests cover every verdict class.
- [Endpoint/display fields permit stale routing] → Bound requests compare them
  with the current attachment before adapter invocation.

## Migration Plan

Additive result fields remain optional in unbound mode. Rollback removes the
gate/stamping without changing executor implementations. No runtime cleanup is
applicable.

## Open Questions

- None. No protocol capture/replay surface changes.
