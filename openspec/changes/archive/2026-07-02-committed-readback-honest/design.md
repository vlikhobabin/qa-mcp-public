# Design - Honest native write read-back

## Problem

`NativeWriteSession.write` and `set_table_cell` currently treat any read-back that starts with the requested value as
committed. That is too broad for general strings: an old value `123456` can make a no-op write of `123` look committed.

At the same time, `read_field_value_near` only accepts ASCII runs with length `2..40`. It misses valid values that are
Cyrillic, a single character, or longer than 40 bytes. That makes actual commits look uncommitted.

## Read-back extraction

The read-back extractor should decode the value envelopes already present near `EditField[<field>]` rather than looking
for a printable ASCII run with a narrow length byte. The implementation should:

- keep the existing latin1 anchor for ASCII fixture names;
- keep the UTF-16LE field-leaf anchor for Cyrillic field names;
- decode the adjacent 1C length-prefixed value as UTF-8 or UTF-16LE where the envelope indicates it;
- accept 1-character values and values longer than 40 bytes when the length prefix and buffer are valid;
- return `None` only when no value for the target field can be decoded.

If a full generic parser is too large for this change, a bounded local extractor is acceptable as long as the new tests
cover Cyrillic, single-character and long values and preserve existing ASCII behavior.

## Commit matching

Protocol write commit matching should use a helper with a narrow contract:

- normalize requested and read-back values by trimming field padding and applying stable string normalization;
- return true for exact equality;
- allow a date-specific prefix only when the field/date path has explicitly opted into date/time suffix tolerance;
- never accept a generic prefix match for text fields.

`NativeWriteSession.write` and `set_table_cell` should use that helper. A failed read-back is `committed: false`, not a
hard error by itself, but it must not produce `true`.

## Tests

Offline tests should cover:

- requested `"123"` with read-back `"123456"` is not committed;
- requested Cyrillic value read back from the target field is committed;
- requested `"5"` read back from the target field is committed;
- requested long value (>40 bytes) read back from the target field is committed;
- existing table-cell and date formatting behavior remains intentionally accepted where documented.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol write verification | native write read-back extraction and `committed` matching | Offline read-back fixtures plus live write regression with exact/normalized value checks | `source_preflight`, `qa_testclient_scenario`, `scenario_log`, `data_assertion` | `.artifacts/openspec/committed-readback-honest/2026-07-02/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL diagnostics | no BSL files changed | N/A because this change edits Python protocol code only | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | no BSL module is modified | no BSL behavioral surface |
