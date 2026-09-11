## Why

The capture-free navigated value-read mechanism (epic 82) already REACHES a real
catalog/document RECORD form on a second config and resolves per object-attribute
field against the navigated form's `S.F`, but it was only verified against a
NEW/EMPTY create-form — fields with no `e0 4b 53` «стал равен» envelope read back
0 values. That is a correct read of an empty form, but it leaves no proof that a
POPULATED record's real attribute values can be read back capture-free. Now that
the card-98 dynlist reads (`read_list_row` / `read_list_grid`) can position on a
row and return a ref, the populated-record value-read is unblocked: the remaining
work is composition + one live verify, not new protocol decoding.

## What Changes

- Open an EXISTING POPULATED catalog/document record capture-free (no Vanessa),
  by record ref (`e1cib/data/Справочник.X?ref=<guid>` nav-link) and/or by
  row-drill (`open_card` from a positioned `read_list_row(where=…)` row), and
  value-read its object-attribute fields against the navigated form's `S.F`.
- Assert ≥1 non-empty object-attribute value read back matches OData for a real
  config (read-only verification, no mutation).
- Add/confirm a unit/shape test for the populated-record value-read path and a
  retained evidence note describing the live verification.
- This change touches the Python manager (`read_form_descriptor` value-read,
  `_open_form_by_link`, `_retarget_read_to_groups`, `read_list_row`/`open_card`
  composition) and protocol-lab behavior; it does not add a new wire decode.
- It requires a live 1C TestClient (cold-client boundary applies) plus OData for
  the oracle. No Vanessa, no EDT/meta snapshot.

## Capabilities

### New Capabilities
<!-- none — this extends the existing protocol-lab capability -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: The capture-free navigated record value-read is proven
  end-to-end against a POPULATED record (not just an empty create-form): a real
  catalog/document record is opened capture-free by ref or row-drill, ≥1
  non-empty object-attribute value is read back, and the value is asserted
  against OData.

## Impact

- Python manager: `src/qa_mcp/mcp_server.py` (`read_form_descriptor` value-read,
  `_open_form_by_link`, `_retarget_read_to_groups`, `read_list_row`/`open_card`
  composition), `src/qa_mcp/protocol/responses.py` (`extract_descriptor_fields`).
- Tests: a populated-record value-read shape/unit test.
- Evidence: `.artifacts/openspec/populated-navigated-record-valueread/<run-id>/`
  plus the existing `evidence/card98-navigated-record-valueread-2026-06-20/`.
- Runtime: live 1C TestClient (cold boot) + OData oracle; read-only, no mutation,
  no Vanessa. Cold-client boundary (one materialised dynlist read per fresh
  `launch_test_client`) and the navigated-form `S.F` retarget are the watch items.
