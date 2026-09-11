## Why

`set_table_date_cell` handles grid date cells through a mouse/calendar path, but create forms also need form-level date edit fields such as `ДатаДоговора`. Without a form-date writer, a UI create flow cannot set the date and number values that feed business auto-name logic.

## What Changes

- Add a form-level date-field writer distinct from table date-cell handling.
- Make date input usable from the open-link write path and create scenario flow.
- Normalize/validate accepted date input format before touching the live client.
- Retain explicit evidence for live date-field write claims or provider gaps.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: native write helpers can set managed-form date edit fields and distinguish them from tabular date-cell calendar writes.

## Impact

- Touches protocol write helpers, MCP wrapper surface and tests.
- May use the pure protocol field-write path or a bounded XTEST fallback depending on field behavior.
- Requires live TestClient evidence for runtime acceptance, but offline validation covers parsing and routing.
