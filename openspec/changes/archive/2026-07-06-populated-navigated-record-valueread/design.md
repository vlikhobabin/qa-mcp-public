## Context

Epic 82 shipped a capture-free navigated value-read that REACHES a real record
form on a second config (`e1cib/data/Справочник.Валюты` on demo БСП opens
`Валюта (создание)`) and resolves per object-attribute field (`Код` /
`Наименование` / …) against the navigated form's `S.F`. The remaining gap is
proof: the only form reached was a NEW/EMPTY create-form, whose fields carry no
`e0 4b 53` «стал равен» envelope, so the value-read correctly returned 0 values.
A `xdotool type` attempt to populate failed because the navigated form was not
the focused OS window. There is no NON-EMPTY proof.

This change closes the proof gap. It is mostly COMPOSITION of already-shipped
tools plus one live verify, unblocked by the card-98 dynlist reads
(`read_list_row(where=…)` / `read_list_grid`) which can position on a row and
yield a ref.

## Goals / Non-Goals

**Goals:**

- Open an EXISTING POPULATED catalog/document record capture-free.
- Value-read its object-attribute fields against the navigated form's `S.F`.
- Prove ≥1 non-empty value matches OData on a real config.
- Add a unit/shape test and a retained evidence note.

**Non-Goals:**

- Any mutation of the record or infobase (read-only).
- New wire-protocol decoding — the value envelope (`e0 4b 53`) and the
  descriptor field enumeration are already decoded.
- Vanessa, EDT or meta involvement.
- General multi-config robustness sweeps beyond one real populated record
  (one solid non-empty proof is the bar; further configs are a bonus).

## Decisions

- **Open route — prefer ref nav-link, fall back to row-drill.** Try
  `e1cib/data/Справочник.X?ref=<guid>` first (decode/confirm the ref nav-link
  resolves to a record form's `S.F`). If the ref nav-link form does not resolve
  cleanly, drill from a positioned list row: `read_list_row(where=…)` to land on
  a known record, then `open_card` to open that record's form, then value-read.
  Record which route produced the proof.
- **Value-read target.** Reuse `read_form_descriptor` value-read with the
  navigated form's `S.F` override (`_retarget_read_to_groups(form_ref=…)`) and
  the zero-group field enumeration (`extract_descriptor_fields` matching
  `ManagedForm[F].EditField[name]` with no enclosing Group — record-object
  attributes; columns excluded).
- **Oracle.** Read the same record's same field from OData (live-mcp /
  `query_odata`) and assert equality. Pick a record + field whose value is
  stable and unambiguous (e.g. `Наименование` of a well-known catalog item).
- **Empty vs failure.** The result must distinguish "read succeeded, value
  empty" from "form not reached / read failed" so an empty-form read can never
  be mistaken for a populated-record proof.
- **Cold-client boundary.** Honor the one-materialised-dynlist-read-per-fresh-
  `launch_test_client` boundary when the open route uses a dynlist read; sequence
  the record open + value-read within a single cold session.

## Risks / Trade-offs

- [Risk] The ref nav-link form (`e1cib/data/...?ref=`) may not resolve to a
  record `S.F` the same way the list/create nav-links do. Mitigation: the
  row-drill route (`open_card`) is the fallback and is already partly built.
- [Risk] The cold-client boundary may force the record open and the value-read
  into one tightly-sequenced session. Mitigation: open the record directly (ref)
  to avoid spending the single dynlist materialisation, or sequence row-drill
  carefully and re-boot on cache reset.
- [Risk] OData field naming vs form attribute naming can differ (synonym vs
  identifier). Mitigation: compare on the platform identifier and pick a field
  with a 1:1 name.
- [Risk] Focus/window issues seen with `xdotool type` — avoided here because the
  approach reads an ALREADY-populated record and never types into the form.

## Migration Plan

- Confirm or extend the open-by-ref path (`_open_form_by_link` for
  `e1cib/data/...?ref=`); keep the row-drill (`open_card`) fallback.
- Run a live cold-boot: open a known populated record, value-read its attributes,
  read the same field from OData, assert equality.
- Capture evidence; add the shape/unit test; sync the spec.

## Open Questions

- Which real config + record gives the cleanest stable oracle — `vanessa_client`
  Товары `Наименование`, or a demo БСП catalog record?
- Does `e1cib/data/Справочник.X?ref=<guid>` open a record form whose `S.F` the
  existing splice chain can retarget, or is `open_card` row-drill the only
  reliable route on the lab configs?
