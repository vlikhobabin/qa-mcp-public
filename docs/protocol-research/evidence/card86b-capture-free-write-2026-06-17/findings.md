# Card 86b — capture-free write+commit (findings)

Date: 2026-06-17. Builds on 86a (element addressing decoded + proven for reads). 86b applies the same
`retarget_element_leaf` path retarget to the WRITE block (`build_write_frame` →
`NativeWriteSession.write(value, field=…)`), so a value can be written to a field addressed by NAME off the
PF_EDIT_STRING capture template — no per-field capture.

Reproduce (lab-local captures, gitignored): `tools/protocol-research/run_86b_write_test.sh`,
`element_write_86b_probe.py` (single session), `element_write_crossgroup_probe.py` (cross-group).

## Live result — single session (the correct design)

Cross-session separate `write_form_value` calls re-trip the card-80 persistent-form desync (the form stays
open between connections), so the proof uses ONE `NativeWriteSession` (open-once) on a fresh client:

```
write PF_EDIT_STRING   = 'QA86B_AAA'  committed=True  readback='QA86B_AAA'      (baseline)
write PF_EDIT_NUMBER   = '777'        committed=False readback='120,5'          (addressed OK; string-SET != number-SET)
write PF_EDIT_STRING   = 'QA86B_BBB'  committed=True  readback='QA86B_BBB'      (session stayed healthy)
write PF_EDIT_READONLY = 'SHOULDNT'   committed=False readback='PF_EDIT_READONLY_VALUE'  (negative control: addressed, not modified)
```

## What is proven

- **Capture-free element ADDRESSING on the WRITE path** — every target field is addressed correctly via path
  substitution off the PF_EDIT_STRING template: each read-back returns that field's OWN live value
  (PF_EDIT_NUMBER→`120,5`, PF_EDIT_READONLY→its value), with no per-field capture.
- **Capture-free COMMIT for the template's element TYPE (string)** — the baseline write commits, and a second
  string write commits too, so the session is robust (no desync) after a non-committing write.
- **Correct negatives** — a read-only field is addressed but not modified (committed=False, value unchanged).

## Boundaries (clearly scoped to other sub-stories)

- **Cross-TYPE commit (number/date/checkbox)** — a string-format SET frame does not commit on a number field
  (addressed `120,5` unchanged). Each element TYPE needs its own SET template → per-element-TYPE coverage
  (card 86c/88), not an addressing problem.
- **Cross-GROUP / tab-page fields** — the only other writable STRING field, `PF_PAGE_A_FIELD`, lives on a tab
  page (`Group[PF_PAGES_MAIN].Group[PF_PAGE_A]`). A full-path (cross-group) retarget addresses it, but the
  write did not commit (`readback` not the field's value) because the page is not active/realized — the field
  must be navigated to first → card 86d (navigate). So no same-type, same-page second writable field exists in
  the fixture to demonstrate a different-field string commit without navigation.

## Net

86b delivers the capture-free write-addressing machinery and proves it: the SET/read frames reach the named
element (read-back confirms) and commit for the template's type. A different-field *commit* is gated by
per-element-TYPE SET templates (number/date — 86c/88) and by navigation for tab-page fields (86d), both
already on the roadmap. The addressing foundation (86a) now spans reads and writes.

## Code

`src/qa_mcp/protocol/native_write.py` (`build_write_frame`, `NativeWriteSession.write(field=…)`),
`src/qa_mcp/scenario/runner.py` (`run_write_scenario(base_field=…)`, per-step `marker` target),
`src/qa_mcp/mcp_server.py` (`write_form_value`/`write_form_values`/`run_write_scenario_tool` gain
`base_field`). Offline: `build_write_frame` tests + multi-field routing test (full suite 203 passed).
