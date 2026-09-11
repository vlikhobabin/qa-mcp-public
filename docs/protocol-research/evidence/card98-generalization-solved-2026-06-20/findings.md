# Card 98 change-1 generalization — SOLVED: live form-field enumeration with NO per-form capture

**Date:** 2026-06-20. **Result:** the change-1 generalization is **built and live-verified**.
`read_form_descriptor(enumerate_live=True)` enumerates the open form's fields **live**, with **no per-form
capture** for the field list — overcoming the blocker characterized earlier (`card98-generalization-2026-06-20`,
which is now superseded). The unlock is the **splice-replay** technique proven for `get_window_list_testclient`.
**45 MCP tools, 319 tests.**

## The previous blocker — and why it's overcome

The earlier attempt tried to replay the captured get_form_analysis enumeration frames: a single-frame raw replay
returned only an ACK, and a generated template DESYNCED (the descriptor frames carry dynamic content the template
tooling doesn't model). Conclusion then: "blocked until the descriptor frames' dynamic fields are fully modeled."

The **window-list work** then proved a different replay path — a genuine query that *also* fails raw replay
(«Сеанс работы завершен») works when its command body is **spliced onto a live value-read frame header** (so the
live session GUIDs are inherited). The same technique applies here.

## Capture + decode (genuine Vanessa manager)

Booted the genuine manager, connected a client, opened the fixture form, and `tcpdump`'d a `get_form_analysis`
call (`genuine-card98-formanalysis-20260620`, gitignored). The **descriptor query** (chunk#44, 206 B) shares the
`… cb 53 81 a3 cb 23 95` header with the value-read and embeds the form path as `9a 66
SecondaryFrame[S].ManagedForm[F]` then opcode `88 81 81 e1 82 81 81 81 81 81 81`. Its **response** (≈71 KB,
3 chunks) is the form descriptor: a sequence of `(Group[g]\.)+EditField[name]` element paths (ASCII for ASCII
names, UTF-16LE for Cyrillic) — **46 EditFields + 24 Buttons + 6 Tables + 144 Groups**, each path followed by
`81 fa <len> <name>`.

## The splice replay (the unlock)

`native_write.splice_descriptor_query(rendered_value_read_frame, S, F)`: render a value-read frame live (the
engine rebinds the session GUIDs), keep its header up to `cb 23 95`, graft the descriptor command body with the
form path **retargeted to the live SecondaryFrame/ManagedForm** (extracted from the rendered frame), and send. A
raw replay of the genuine query is rejected (session-GUID validation); the splice is accepted and returns the
full live descriptor. `responses.extract_descriptor_fields(blob)` parses it into `[(field_name, [Group names])]`
(ASCII + UTF-16) — the live equivalent of `_enumerate_capture_fields`.

## Productized + live-verified

`_enumerate_live_fields(handle)` renders a live header → splices the descriptor query → parses the field list.
`read_form_descriptor(enumerate_live=True)` uses it instead of the per-form capture; the value-read sweep
(form-independent, reads any field by path) is unchanged. **Live (`read_form_descriptor_live_verify.py`, fresh
/TESTCLIENT):**

```
LIVE  enumeration: 46 fields decoded / 46 queried
CAPTURE enumeration: 43 fields decoded / 43 queried
oracle 46; LIVE∩oracle 43; VALUE-MATCH 42/43   (the 1 diff = live-state PF_SELECTED_ROW_MARKER)
LIVE got, NOT in the capture path: PF_REPORT, PF_SELECTED_ROWS, PF_TABLE_SNAPSHOT
```

Live enumeration found **3 fields the capture sweep didn't have**, decoded the Cyrillic Контрагент, and matched
the oracle 42/43 — all with **no per-form field-list capture**.

## Scope / what's still form-specific (honest)

- **Field-list enumeration is now capture-free** (the headline). The value-read sweep is form-independent.
- The **form OPEN** still uses the fixture's open frames (11-17). To introspect a DIFFERENT form, open it first
  via the existing machinery (`open_list` / `open_card` / a nav-link), then `read_form_descriptor(enumerate_live=
  True)`. Wiring a generic "open form X then introspect" is the natural next step.
- The descriptor also enumerates Buttons / Tables / Groups (the full element TREE — the `ui_read_tree` surface);
  `read_form_descriptor` reads the EditField value surface, so a tree-shaped tool is a small follow-up on the
  same descriptor.

## Artifacts

- Code: `src/qa_mcp/protocol/responses.py` (`extract_descriptor_fields`),
  `src/qa_mcp/protocol/native_write.py` (`DESCRIPTOR_QUERY_PREPATH/POSTPATH`, `splice_descriptor_query`),
  `src/qa_mcp/mcp_server.py` (`_enumerate_live_fields`, `read_form_descriptor(enumerate_live=…)`). Tests:
  `tests/test_form_descriptor.py` (+5). **319 tests.** Probes:
  `form_descriptor_query_splice_probe.py` (the splice — works), `read_form_descriptor_live_verify.py` (the tool —
  46 fields, no capture). Capture feature: `qa-card98-introspect-capture.feature`.
