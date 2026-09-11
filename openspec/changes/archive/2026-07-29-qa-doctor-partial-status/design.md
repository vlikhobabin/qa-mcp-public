## Context

The doctor already returns ordered checks with `pass`, `fail`, or `skipped`
status. Operators need a clearer machine-readable distinction between required
checks that block readiness and optional probes that are useful but unavailable
on a contour.

## Goals / Non-Goals

**Goals:**
- Mark doctor checks with a `required` boolean.
- Keep required failures blocking (`ok=false`, `status=fail`).
- Keep optional skips partial but non-failing (`ok=true`, `status=partial`).
- Cover auth-missing and optional effective-user skips in offline tests.

**Non-Goals:**
- Change the probe order or add live probe types.
- Treat missing optional probes as complete success.
- Execute live 1C runtime, Vanessa MCP, EDT/meta snapshots, or protocol
  captures.

## Decisions

- Add `required` metadata to each check rather than infer optionality from the
  check name outside the result. This keeps diagnostics self-describing for
  doctor consumers.
- Use required failed checks for `ok`, and optional skipped checks for
  `partial`. This preserves strict failure semantics while making optional gaps
  visible.
- Keep effective-user absence optional, but keep effective-user mismatch a
  failing check when the probe returns a concrete conflicting user.

## Risks / Trade-offs

- [Risk] Consumers that compare exact check dictionaries may need to accept the
  new `required` field. -> Mitigation: existing public checks remain ordered
  and keep their status/code/data fields.

## Migration Plan

No migration is required. Consumers may start reading `required`; existing
status fields remain present.

## Open Questions

None.
