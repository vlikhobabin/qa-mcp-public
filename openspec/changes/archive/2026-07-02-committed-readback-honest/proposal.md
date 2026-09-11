## Why

The protocol-layer native write path uses prefix matching for commit decisions and a narrow ASCII-only read-back
scanner. That produces both false positives (`"123"` accepted against `"123456"`) and false negatives for real
Cyrillic, one-character and long values.

## What Changes

- Widen protocol read-back extraction to decode committed values that are Cyrillic, one character, or longer than 40
  bytes.
- Replace `startswith` commit checks with normalized equality for the target field, sharing the same intent as the
  label-route close-value matcher.
- Preserve documented formatting tolerance only where the field surface requires it, such as date read-back with a time
  suffix.
- Add offline read-back and commit-matching regression tests.
- Run the card-level live write regression to prove the write result is honest on the lab client.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: protocol-layer native write results must report `committed: true` only when the target field's
  normalized read-back equals the normalized requested value, and read-back extraction must handle non-ASCII and bounded
  edge-length values.

## Impact

- Touches protocol write/read-back code in `src/qa_mcp/protocol/native_write.py`.
- May factor a small shared value-normalization helper used by protocol-layer writes.
- Adds focused offline tests in `tests/test_native_write.py`.
- Requires live 1C TestClient runtime for final card acceptance via `python -m qa_mcp.regression --include-write`.
