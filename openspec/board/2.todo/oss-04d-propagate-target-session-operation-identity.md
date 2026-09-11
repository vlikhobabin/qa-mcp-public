# Propagate Target And Session Operation Identity

## Status
2.todo

## Owner
qa-mcp

## Series
oss-04d

## Order Index
4034

## OpenSpec Stage
artifacts / unpublished exhausted lineage

## Parent Epic
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Goal
Extend the public shared-core operation contract so MCP and scenario paths gate
and report one target/session identity for every verdict class.

## Acceptance
- Common execution blocks foreign targets, sessions, generations and endpoints
  before invoking local or Windows adapters.
- Results and artifact references carry bounded target/session/operation
  provenance for success, blocked, ambiguous and failure verdicts.
- Evidence policy removes physical artifact paths under `sanitized` and permits
  them only under approved `full_local`.
- The payload stays at or below `300` added production LOC.

## Change Set
1. `propagate-qa-mcp-target-session-operation-identity` -
   `openspec/changes/propagate-qa-mcp-target-session-operation-identity/`

## Dependencies
- [OSS-04C](../4.done/oss-04c-compose-project-target-readiness.md).

## Verify
- MCP and scenario executor tests for all verdict classes and mismatch gates.
- Downstream fake-executor compatibility and credential/path redaction tests.
- Focused/full non-live, compilation, strict OpenSpec and review preflight.

## Result
Two unpublished implementation lineages reached fresh cycle-3 `NO-GO` after
rescue budget `2/2`. The exact R1 final payload and an older OSS-04D checkpoint
remain recoverable in named stashes; exact recovery of the final OSS-04D tree
is not claimed. Their verdict/history evidence remains retained and neither
payload is publishable. OSS-04D-R2 is the required investigation before a new
implementation successor.

## Next
- Do not deliver or publish this source card.
- Continue only through OSS-04D-R2, OSS-04D-A1 and OSS-04D-R3 in order.

## Log
- 2026-08-25 created by the OSS-04 complexity investigation as payload D.
- 2026-08-25 unblocked by published OSS-04C; next sequential child.
- 2026-08-25 source OSS-04D and linked OSS-04D-R1 each exhausted two review
  rescues without publication; operator authorized OSS-04D-R2 investigation.
