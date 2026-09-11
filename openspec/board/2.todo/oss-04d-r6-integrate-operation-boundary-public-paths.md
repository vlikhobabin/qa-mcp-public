# Integrate Operation Boundary Public Paths

## Status
2.todo

## Owner
qa-mcp

## Series
oss-04d-r6

## Order Index
4034.87

## OpenSpec Stage
blocked / superseded handoff

## Parent Epic
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/2.todo/oss-04d-a3-authorize-operation-boundary-integration.md","authorization_id":"oss-04d-a3-authorize-operation-boundary-integration"}`

## Goal
Integrate published R5 with pure route admission and both real public paths.

## Acceptance
- Malformed, foreign and asymmetric bound state blocks before Local/Windows;
  current bound, true pre-session and declared unbound controls remain.
- Evidence scope opens after admission and closes in `finally`; serialization
  cannot retry or change route authority.
- Success/blocked/ambiguous/failure have identical trusted provenance and
  taxonomy through real MCP and ScenarioRunner.
- Both real paths execute this exact URL table:

| Depth | Credential path | Authority userinfo | Paired control | Outcome |
| ---: | --- | --- | --- | --- |
| 1 | encoded assignment | encoded `user@` and `user:pass@` | benign path encoded once, no-userinfo authority | hostile absent with no original/decoded fragment; control canonical |
| 2 | encoded assignment | encoded `user@` and `user:pass@` | benign path encoded twice, no-userinfo authority | hostile absent with no original/decoded fragment; control canonical |
| 3 | encoded assignment | encoded `user@` and `user:pass@` | benign path encoded three times, no-userinfo authority | hostile absent with no original/decoded fragment; control canonical |
| 4 | encoded assignment | encoded `user@` and `user:pass@` | benign path encoded four times, no-userinfo authority | hostile absent with no original/decoded fragment; control canonical |
| 5 | encoded assignment | encoded `user@` and `user:pass@` | benign path encoded five times | all reject non-fixed; no fragments |

- Every public result stays total within the R5 envelope.
- Added production lines are at most 300; no lifecycle/new authority/wire.

## Scope
- Pure route and Local/Windows/MCP/ScenarioRunner integration over R5.
- No OSS-04E lifecycle, resolver, protocol capture or live mutation.

## Change Set
none; fast-forward required.

## Depends On
- `oss-04d-r4-r1-replace-exhausted-boundary-investigation`
- `oss-04d-r5-implement-core-operation-boundary`
- `oss-04d-a3-authorize-operation-boundary-integration`

## Blocks
- none; superseded R6 cannot unblock OSS-04E.

## Verify
- Test-first route/verdict matrix through Local/Windows and real MCP/scenario.
- For each depth 1–5, each path runs credential assignment, `user@`,
  `user:pass@` and paired control with the exact table oracle.
- The public matrix is exactly `40 = 5 × (3 hostile + 1 control) × 2 paths`
  cells; every hostile cell asserts absence of both original and every decoded
  fragment outside the absent URL field.
- Focused/full non-live, coverage, compile, strict OpenSpec, LOC, scope/diff.
- Exact-source Windows offline integration proof with owned cleanup.
- Fresh independent review.

## Result
Superseded before delivery because R5/A3 cannot publish. No runtime
implementation or external evidence belongs to this card.

## Next
- Do not deliver R6. Follow R5-R2 → A4 → R7 → A5 → R8.

## Log
- 2026-08-25 created by R4-R1 with the exact public URL table.
- 2026-08-26 blocked/superseded; R8 is the only planned public integration
  successor that can unblock OSS-04E.
