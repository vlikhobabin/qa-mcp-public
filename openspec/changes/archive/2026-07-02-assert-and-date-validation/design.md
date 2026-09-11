## Context

This change spans two validation surfaces in Python manager code. `src/qa_mcp/data/odata.py::match_value` compares
read-only data assertion values and currently falls through to equality for every unknown mode. `src/qa_mcp/mcp_server.py`
has validated managed-form date input through `_normalize_form_date`, but table date-cell paths still split integers
directly and can activate the calendar for impossible dates.

The date-cell tool can drive a live UI in normal use, so invalid dates must be rejected before any protocol activation,
screenshot or mouse click is attempted. The fix is still offline-verifiable by using injected fakes and checking that
invalid input returns a blocked result without calling the activation path.

## Goals / Non-Goals

**Goals:**

- Fail closed on unknown OData match modes.
- Support numeric matching for locale-formatted values such as `120,50` vs `120.5`.
- Reuse one date validator for form-level and table-cell date inputs.
- Reject invalid table-cell dates before calendar localization or clicks.
- Ensure backward-year calendar blocking does not leave an opened dropdown.

**Non-Goals:**

- No OData endpoint behavior changes beyond local value comparison.
- No new date-cell UI strategy or live capture evidence.
- No live write, save, post, delete, import/export or cleanup operation.

## Decisions

- Mirror the MCP-side fail-closed mode contract by raising `ValueError` for unsupported OData match modes. Silent
  equality fallback is the bug.
- Implement numeric matching using `Decimal` after normalizing comma decimal separators. This avoids binary float
  rounding and keeps the dependency footprint unchanged.
- Add a small table-date normalization helper that delegates to `_normalize_form_date` and returns integer day/month/year
  only after calendar-valid parsing succeeds.
- Move the backward-year guard before clicking the calendar dropdown in `_drive_calendar_pick`. If the target cannot be
  reached safely, the function returns `blocked` while the UI state remains as it was after cell activation.

## Risks / Trade-offs

- Unknown OData modes now raise where callers may have received a false equality result. This is intended compatibility
  tightening; callers with typos must fix their mode.
- Numeric mode is decimal-string oriented, not a full 1C type parser. Inputs that cannot normalize to decimal raise a
  comparison failure through `ValueError` rather than silently comparing strings.
- The open calendar from date-cell activation may still exist for other blocked localization cases. This change fixes
  the invalid-date preflight and backward-year guard leak named by the card; wider popup recovery stays out of scope.
