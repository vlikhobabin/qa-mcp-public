## Context

The prior focused V2 proof remains candidate-only. A real demo-button pilot can
therefore end in several legitimate states: no safe target, blocked
classification, blocked capture, candidate evidence, accepted evidence or V3
mutation routing. Publication must keep those states visible.

## Goals / Non-Goals

**Goals:**

- Publish a compact final decision for the pilot.
- Link target selection, classification, capture or blocked evidence and
  recovery status.
- Keep accepted mapping output proof-gated.
- Record V3 routing when the result is unsafe, mutating or rollback-dependent.

**Non-Goals:**

- Running a new live capture.
- Promoting accepted status from visual success alone.
- Hiding rejected or blocked pilot outcomes.

## Decisions

- Use final statuses `accepted`, `candidate`, `rejected`, `blocked`,
  `unsupported`, `partial`, `timeout` or `routed_to_v3`.
- Publish accepted status only when same-action replay, direct Python-manager
  probe or typed contract proof is reviewed for the non-mutating action.
- Candidate status is valid when target/classification/capture evidence exists
  but accepted proof is missing.
- V3 routing is required when the selected button writes data, executes a
  business command, needs rollback or falls outside the V2 allowlist.
- Accepted-mapping output must remain empty for candidate, blocked, rejected or
  V3-routed results.

## Risks / Trade-offs

- [Risk] A blocked pilot can look like a failed delivery. Mitigation: publish
  blocked and V3-routed outcomes as explicit safe results when no unsafe click
  occurs.
- [Risk] Evidence links can expose raw runtime details. Mitigation: reviewed
  docs link compact summaries only.
- [Risk] Accepted status can be overclaimed. Mitigation: require replay,
  direct probe or typed contract proof before accepted mapping output changes.

## Migration Plan

- Gather outputs from selection, classification and capture.
- Publish compact evidence and final status.
- Update evidence index and accepted-mapping or candidate directories.
- Link V3 routing follow-up when mutation behavior is detected.

## Open Questions

- If the pilot routes to V3, should the existing V3 mutation evidence card be
  reopened through a new card or should this publication only link the blocker?
