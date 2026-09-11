## Context

The report tool currently marks non-dry-run traffic as at most `partial`
because timestamp/frame-range join has not been reviewed. The next analyzer
step should map before/after events to proxy chunks, derive frame ranges and
write corpus rows that follow the existing evidence contract.

## Goals / Non-Goals

**Goals:**

- Accept manager fixture V1 captures as corpus inputs.
- Join `case_events.jsonl` to `traffic.jsonl`.
- Preserve unresolved joins with stable reason values.
- Generate normalized rows compatible with existing comparison tooling.

**Non-Goals:**

- No live capture orchestration.
- No new protocol dynamic-field rule without reviewed evidence.
- No accepted mapping promotion without replay/probe status.

## Decisions

1. Prefer chunk ranges first and frame ranges where the frame splitter is
   reliable.
   Rationale: chunk counters are available from the proxy even before a full
   frame decoder handles all cases.

2. Keep row acceptance independent from join success.
   Rationale: a joined row with no replay/probe support should remain
   `pending`.

3. Record precise unresolved reasons.
   Rationale: `no_before_event`, `no_after_event`, `no_proxy_chunks`,
   `overlapping_case_window` and similar reasons are actionable.

## Verification Matrix

This is primarily protocol tooling, but it consumes 1C runtime evidence.
Detailed rows are in `tasks.md`.

## Risks / Trade-offs

- Timestamp-only joins can be imprecise if the manager clock and proxy event
  timestamps differ. The analyzer should prefer explicit counters when they
  are added by runtime output.
- Background refresh can overlap command windows. The row must keep ambiguous
  or overlapping traffic non-accepted.
