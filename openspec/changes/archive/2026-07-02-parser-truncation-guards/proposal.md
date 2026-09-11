## Why

Transport truncation and timeout-like reads currently surface as parser
exceptions or silent list truncation. Read tools should return partial results,
explicit truncation state, or `None` for unsupported field-name scans instead of
crashing or silently dropping rows.

## What Changes

- Guard response parser indexing so truncated value and window-caption envelopes
  cannot raise `IndexError`.
- Make non-Latin field-name scans return `None` consistently instead of raising
  `UnicodeEncodeError`.
- Remove adjacent-duplicate rows as an end-of-list signal for list-grid reads.
- Surface list-grid timeout or empty-row stops through explicit truncation or
  stop-reason fields.
- Add offline tests for truncated blobs, Cyrillic field names, duplicate rows,
  and timeout/stop classification.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: response parsing and list-grid extraction are guarded
  against truncated responses and expose explicit stop information instead of
  raising parser errors or silently truncating duplicate rows.

## Impact

- Touches Python manager code under `src/qa_mcp/protocol/responses.py` and
  `src/qa_mcp/protocol/native_write.py`.
- Touches offline parser/list-grid tests.
- Does not change MCP provider setup, OpenSpec workflow, or runtime lab config.
- Requires offline parser and fake-session evidence; a live read pass remains
  useful regression evidence for unchanged user-visible values.
