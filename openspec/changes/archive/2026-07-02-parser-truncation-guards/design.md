## Context

`src/qa_mcp/protocol/responses.py` scans byte responses for values, captions and
field names. Some scanners index immediately after markers and can raise
`IndexError` when the transport returns a truncated envelope. Field-name scans
also encode candidate names as Latin-1 even though 1C forms commonly contain
Cyrillic names. Separately, `read_list_grid_replay` treats adjacent duplicate
row values as the end of a list, which silently drops legitimate duplicate rows.

## Goals / Non-Goals

**Goals:**
- Convert truncated parser envelopes into partial/`None` results instead of
  exceptions.
- Make non-Latin field names behave like unsupported scanner input rather than
  runtime errors.
- Preserve adjacent duplicate list rows.
- Add explicit stop information when list-grid reads end because a row times
  out or the sweep sees an empty row.
- Cover these cases with offline parser and fake-session tests.

**Non-Goals:**
- No new list-grid protocol command.
- No write/action semantics.
- No broad redesign of response parsing.

## Decisions

- **Guard local index reads:** check bounds before dereferencing bytes after a
  marker. A missing byte returns `None` or leaves the partial result unchanged.
- **Treat encoding failure as not addressable:** wrap field-name Latin-1
  encoding in the same spirit as `read_field_value_near`; unsupported names
  return `None` rather than raising.
- **Remove duplicate-row stop:** adjacent equal values are valid list data. Stop
  on explicit empty rows or timeout classification, not equality with the
  previous row.
- **Expose stop state:** when the public result shape can carry metadata, return
  `truncated` and `stop_reason`. Where a caller expects only values, keep the
  value behavior stable and add metadata through the containing result.

## Risks / Trade-offs

- [Risk] Existing callers may not inspect new truncation metadata. Mitigation:
  values remain backward-compatible and tests assert no silent duplicate stop.
- [Risk] A truly repeated terminal row could now be read as data. Mitigation:
  duplicate rows are legitimate; an explicit empty row or timeout is a safer
  terminal signal.
- [Risk] Returning `None` for non-Latin scanner input may hide a desired value.
  Mitigation: this matches the scanner's current byte-addressing limitation and
  avoids crashing higher-level tools.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Response parser | `_value_after_leaf`, `_window_caption_after`, field-name scanners | truncated blob and Cyrillic field-name fixtures | offline unit tests return partial/None and no `IndexError`/`UnicodeEncodeError` | `tests/` plus `.artifacts/openspec/parser-truncation-guards/2026-07-02/` if retained | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: byte scanner still cannot resolve every non-Latin name |
| List-grid read | `read_list_grid_replay` duplicate and timeout handling | fake replay/session with adjacent equal rows and timed-out row | offline unit tests for all rows returned and explicit stop metadata | `tests/` plus `.artifacts/openspec/parser-truncation-guards/2026-07-02/list-grid/` if retained | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: result-shape compatibility must be preserved for existing MCP callers |
| QA/TestClient live read | `read_list_grid` on Linux `vanessa_client` | optional live read pass after parser/list-grid tests | live read command summary or provider-gap/runtime-gap diagnostic | `.artifacts/openspec/parser-truncation-guards/2026-07-02/live-read/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: live lab availability may block final read evidence |
