## Why

Two validation paths accept or degrade invalid input: OData data assertions treat unknown match modes as equality, and
table date-cell writing parses `DD.MM.YYYY` with integers but no calendar range validation. Both defects can produce
false greens, false reds or unsafe live clicks from malformed input.

## What Changes

- Make `qa_mcp.data.odata.match_value` fail closed on unknown match modes instead of falling back to equality.
- Add numeric matching to the OData assertion path so the advertised data assertion mode compares locale-formatted
  numeric values correctly.
- Reuse the managed-form date validator for table date-cell tools so out-of-range dates are rejected before any
  calendar activation or mouse clicks.
- Keep backward-year calendar guard behavior from leaving the popup open by checking that guard before opening the
  dropdown.
- Add focused offline tests for match-mode validation, numeric comparison and invalid table-date blocking.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: data-layer assertions and table date-cell writes must fail closed on unsupported match modes
  and invalid dates before executing unsafe or misleading behavior.

## Impact

- Touches Python manager code under `src/qa_mcp/data/odata.py` and `src/qa_mcp/mcp_server.py`.
- Adds offline tests under `tests/test_odata.py` and `tests/test_mcp_server.py`.
- Does not require live 1C runtime for verification; the date-cell safety regression uses injected display/session
  fakes and must not start a TestClient.
