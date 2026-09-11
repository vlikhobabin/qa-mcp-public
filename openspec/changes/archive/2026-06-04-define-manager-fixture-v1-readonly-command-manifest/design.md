## Context

The client fixture V1 exposes stable `PF_*` markers across edit fields,
checkboxes, command bars, tables, groups and pages. The manager harness needs
to execute read-only TestManager/TestedApplication commands against those
targets and emit side-channel events that can be aligned with TCP proxy
traffic.

## Goals / Non-Goals

**Goals:**

- Define a stable run manifest accepted by the manager V1 harness.
- Define the read-only command catalog for client fixture V1.
- Define `case_events.jsonl` and `manager_harness_result.json` output records.
- Preserve one command boundary per case, with before/after timestamps and
  result status.

**Non-Goals:**

- No clicks, text input, page switches, row selection, business commands or
  writes.
- No socket or TCP parsing inside 1C.
- No frame range classification; that is produced by capture/report tooling.
- No accepted protocol mapping promotion.

## Decisions

1. Make `case_id` and `command_id` distinct.
   Rationale: `case_id` identifies corpus intent, while `command_id` identifies
   the concrete manager harness command execution and repeat.

2. Require target and expected markers in the manifest.
   Rationale: frame review needs `PF_*` markers and target paths to avoid
   interpreting same-sized responses as equivalent.

3. Store events as JSON Lines and final status as one JSON summary.
   Rationale: JSONL supports streaming before/after records, while the summary
   provides a compact machine-readable run result.

4. Record exceptions as command results.
   Rationale: failed TestManager API calls are still useful protocol evidence
   if their command boundary and error details are preserved.

## Risks / Trade-offs

- Some read-only API calls may return localized strings or platform-dependent
  object class names. Mitigation: store expected markers separately from
  preview values and keep platform/version in the run manifest.
- Manager timestamps may not be enough for perfect frame joins. Mitigation:
  later capture integration records proxy chunk counters and keeps unresolved
  join gaps explicit.
- A single broad command could hide multiple protocol requests. Mitigation:
  V1 catalog entries must be granular and one case must run at a time.

## Migration Plan

1. Add the manifest reader and output writer to the manager harness.
2. Seed the V1 read-only command catalog from the client fixture V1 target map.
3. Run a small subset first: active window, active form and one marker-bearing
   element family.
4. Expand to the full V1 catalog only after event records are stable.

## Open Questions

- Whether table row/column reads should be grouped by table or emitted as one
  case per row/column property in V1.
- Whether command-bar button state should be represented as `TestedFormField`
  detail cases or as a separate command-bar family in the first manifest.
