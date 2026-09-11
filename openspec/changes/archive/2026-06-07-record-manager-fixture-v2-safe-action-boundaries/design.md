## Context

The V2 tooling pipeline already understands phase-aware dry-run events. Live
action proof now needs the manager runner to emit real event boundaries around
the action and recovery phases.

## Goals / Non-Goals

**Goals:**

- Emit event boundaries around each safe action and recovery path.
- Preserve chunk or frame correlation inputs for the V2 reporter.
- Keep background refresh visible but not accepted as action proof.
- Mark ambiguous boundaries as candidate, partial or blocked.

**Non-Goals:**

- Changing the TCP proxy or injecting markers into protocol traffic.
- Accepting mappings from boundary events alone.
- Capturing V3 mutation or V4 dialog behavior.

## Decisions

- Continue using manager harness side-channel events rather than protocol
  marker injection. This matches V1/V2 tooling and avoids changing the wire.
- Emit both `action_start` and `action_end` so the reporter can separate the
  candidate action window from pre/post reads.
- Store background and recovery ranges explicitly. Dropping them would make
  later comparison look cleaner while hiding ambiguity.
- Treat missing frame/chunk correlation as non-accepted evidence.

## Risks / Trade-offs

- [Risk] Event timing may not align exactly with TCP frames.
  [Mitigation] Keep candidate ranges conservative and preserve background
  ranges.
- [Risk] More event fields can regress V1 reporting.
  [Mitigation] Scope V2-only fields to `safe_ui_action` rows and run V1 tests.
- [Risk] Action result markers may be emitted too late.
  [Mitigation] Record post-read and recovery-read phases separately.

## Migration Plan

- Add V2 event fields without changing V1 read-only event rows.
- Validate dry-run compatibility and then live runner output.
- Keep rows candidate until reporter and comparison accept the boundary shape.

## Open Questions

- Should background ranges be attached per action row or per capture summary
  when refresh traffic overlaps several actions?
- How should timeout boundaries be represented when no `action_end` event is
  emitted?
