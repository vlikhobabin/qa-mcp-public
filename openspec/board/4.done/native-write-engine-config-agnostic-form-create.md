# qa-mcp native write engine: config-agnostic form addressing + fill→save create flow

## Status
4.done

## Owner
qa-mcp

## OpenSpec Stage
archived

## Source
- 2026-06-30 fresh-code e2e on `demo10413` (Stage 4). Root e2e card:
  `../../../openspec/board/1.backlog/e2e-real-dev-contracts-catalog-on-demo10413.md`
  (finding **#16**; deepens the 2026-06-26 finding #1). The launcher libgcc
  defect (#1) is FIXED this run — the TestClient launches/runs and the READ side
  works end to end; the gap is now on the WRITE side.

## Problem
The native write/commit engine cannot drive a UI **create** of a record on an
arbitrary (uncaptured) managed form, so the e2e's UI→DB create+assert could not
run for the new `ДоговорыКонтрагентов` catalog:

1. **No config-agnostic `open_link` for writes.** `read_form_descriptor`
   introspects ANY form by nav-link (`open_link="e1cib/data/Справочник.X"`,
   `enumerate_live=true`) with no per-form capture. The write tools
   (`write_form_value(s)`, `set_table_date_cell`, `click_command`,
   `run_write_scenario_tool`) have NO `open_link` — they open the form via a
   bundled capture fixture (`PF_EDIT_STRING`/`commit-conn`/…) and re-target a field
   off that fixture. So they address only pre-captured fixture forms, not a new
   catalog's element form.
2. **No fill→save session chaining.** Each write tool runs a fresh
   NativeWriteSession (open → commit one/few values → read-back) and closes.
   `run_write_scenario_tool` reports non-write steps (e.g. the `Записать` command)
   as unsupported. So multiple fields cannot be filled AND the record saved on one
   session — a new multi-field record cannot be persisted to the DB through the UI.
3. **Form-level date fields have no clean writer.** `set_table_date_cell` targets
   GRID date cells via mouse-calendar; a form-level date EditField (e.g.
   `ДатаДоговора`) has no equivalent, and the auto-name handler needs both the date
   and the number filled.

Net: UI render + read are GREEN (forms introspect, list grids read), but a
genuine "create a contract from the UI and assert the auto-built Наименование +
Основной" cannot be performed via qa-mcp. The business logic was instead proven
by-identity (the identical object-module handler, proven via Designer `/Execute`
on 2026-06-26) and is platform-valid (`ibcmd config check` passed).

## Scope (proposed)
1. Add a config-agnostic `open_link` (and live field addressing) to the write
   path, mirroring `read_form_descriptor`, so any form can be opened+written
   without a per-form capture.
2. Support a stateful create flow: open form → set N fields (incl. reference +
   form-level date fields) → invoke a write/save command → confirm persistence on
   ONE session (a `run_write_scenario_tool` that accepts command steps, or a
   dedicated `create_record` tool).
3. Add a form-level date-field writer (typed input or picker) distinct from the
   grid `set_table_date_cell`.

## Acceptance
- A new record on an arbitrary catalog element form (no per-form capture) can be
  created via qa-mcp: set reference/string/date/boolean fields, save, and the row
  appears in the catalog list + is read-back-verifiable (UI→DB).
- Re-running the demo10413 e2e Stage 4 can create a `ДоговорыКонтрагентов`
  contract from the UI and assert the auto-built `Наименование` and `Основной`.

## Related
- root e2e card `e2e-real-dev-contracts-catalog-on-demo10413.md` (finding #16; #1).
- memory `qa-mcp-testclient-launcher-libgcc` — the launcher #1 context (now fixed).
- `openspec/changes/archive/2026-06-30-native-write-open-link-addressing/`
- `openspec/changes/archive/2026-06-30-native-write-create-flow/`
- `openspec/changes/archive/2026-06-30-native-write-form-date-input/`

## Notes
- Separately: the qa-mcp default env `.ai1c/vanessa-qa-mcp.env` still targets the
  retired `vanessa_client` infobase (thin). The e2e used the
  `demo10413/.ai/qa-demo10413.env` override. Repoint the default (or document the
  per-project env) so qa-mcp defaults to a live demo target — the qa-mcp analog of
  e2e finding #5.

## Change Set
- `native-write-open-link-addressing`
- `native-write-create-flow`
- `native-write-form-date-input`

## Verify
- FF: `openspec validate native-write-open-link-addressing --strict`
- FF: `openspec validate native-write-create-flow --strict`
- FF: `openspec validate native-write-form-date-input --strict`
- FF: `openspec validate --all`
- FF: `git diff --check -- openspec/changes openspec/board`
- Do: `.venv/bin/python -m pytest tests/test_mcp_server.py tests/test_scenario_runner.py tests/test_native_write.py -q` - 123 passed.
- Do: `.venv/bin/python -m pytest -q` - 555 passed.
- Do: `.venv/bin/python -m compileall src/qa_mcp` - passed.
- Do: Linux demo10413 runtime preflight passed, then live create targeting was blocked because `e1cib/data/Справочник.ДоговорыКонтрагентов` is invalid without owner context. Evidence retained under `.artifacts/openspec/native-write-*/20260630-0708-do/`.
- Do: matrix archive gates passed for all three changes, with provider gaps for live create/save/date proof.
- Do: `openspec validate native-write-open-link-addressing --strict`, `native-write-create-flow`, `native-write-form-date-input`, and `openspec validate --all` - passed.
- Do: `git diff --check -- src/qa_mcp/mcp_server.py src/qa_mcp/scenario/runner.py tests/test_mcp_server.py tests/test_scenario_runner.py openspec/changes openspec/board` - passed.

## Archive
- `openspec/changes/archive/2026-06-30-native-write-open-link-addressing/`
- `openspec/changes/archive/2026-06-30-native-write-create-flow/`
- `openspec/changes/archive/2026-06-30-native-write-form-date-input/`

## Result
Delivered and archived the qa-mcp tool-surface and scenario-runner changes for config-agnostic open-link writes,
write-scenario command/save orchestration, and form-level date input. `write_form_value`, `write_form_values`,
`write_form_date`, and `run_write_scenario_tool` now accept explicit `open_link` routes; date values validate as
`DD.MM.YYYY`; command steps fail closed without an executor; and open-link create scenarios expose provider-gap
persistence metadata instead of claiming unverified data-layer success.

Live demo10413 proof found a real remaining boundary: the generated subordinate catalog create form for
`ДоговорыКонтрагентов` does not open from the ownerless URL `e1cib/data/Справочник.ДоговорыКонтрагентов`; 1C reports
`Invalid URL`. The foreground replay is now bounded so invalid links fail closed, and create steps can carry an
explicit `open_link`; save/persistence remains blocked until owner-aware create navigation and cleanup evidence are
available.

## Next
- Follow-up: `openspec/board/1.backlog/native-write-subordinate-owner-create-cleanup.md`.

## Change 1: `native-write-open-link-addressing`

### Why
The read path can open and introspect an arbitrary managed form through `open_link`, but the protocol write path still starts from captured fixture setup frames.

### Goal
Allow native write sessions and MCP write tools to open a target form by nav-link, resolve its live form reference, and address fields on that form without a per-form capture.

### Scope
- Extend the write session setup to accept `open_link`.
- Reuse the existing fixture-free foreground/navigation resolver where possible.
- Preserve the current capture-template defaults for fixture tests.
- Add offline tests for open-link setup selection and field retargeting.

### Acceptance
- `write_form_value` and `write_form_values` can target a form opened by `open_link`.
- The result reports the opened form and the addressed field.
- Existing fixture-backed write tests remain green.

### Depends On
- none

### Related
- `openspec/changes/native-write-open-link-addressing/`

### Notes For `$openspec-ff-change`
- Modified capability: `qa-mcp-protocol-lab`.

## Change 2: `native-write-create-flow`

### Why
Creating a record through the UI requires several field writes and a save command to run on one live form session.

### Goal
Teach the write scenario path to execute fill and command steps on the same session and verify persistence by UI/list or data read-back evidence.

### Scope
- Add a stateful create/write scenario API path instead of one call per field.
- Support command/save steps such as `Записать` after field input.
- Record per-step results, unsupported step diagnostics, and persistence verification.
- Keep data-changing execution explicit and scoped to operator-requested tool calls.

### Acceptance
- A scenario can open a create form, set multiple fields, invoke save, and report a persisted/read-back result.
- Unsupported write scenario steps fail closed with the step name and reason.
- Existing read-only scenario behavior is unchanged.

### Depends On
- `native-write-open-link-addressing`

### Related
- `openspec/changes/native-write-create-flow/`

### Notes For `$openspec-ff-change`
- Modified capability: `qa-mcp-protocol-lab`.

## Change 3: `native-write-form-date-input`

### Why
Form-level date edit fields are not grid cells, so `set_table_date_cell` does not cover create forms that need date attributes.

### Goal
Add a clean form-level date-field writer for managed form edit fields and make it usable from the create flow.

### Scope
- Support `DD.MM.YYYY` form-level date input through the same field-addressing/write route as other edit fields or a bounded XTEST fallback.
- Keep the grid date-cell calendar path separate.
- Add offline validation for date parsing/normalization and scenario wiring.

### Acceptance
- A form-level date field can be set on an arbitrary open-link form.
- The write result distinguishes form-field date input from grid-cell calendar input.
- Date write verification has retained runtime evidence or an explicit provider-gap record.

### Depends On
- `native-write-open-link-addressing`

### Related
- `openspec/changes/native-write-form-date-input/`

## Log
- 2026-06-30 created from the fresh-code e2e Stage 4 (UI create on demo10413):
  launcher #1 fixed (client runs); read/introspect work on any form; write engine
  cannot address an uncaptured form or chain fill→save, so the UI create+assert
  could not run.
- 2026-06-30T07:06:00Z decomposed via `$opsx-deliver`: moved to `2.todo`,
  created three apply-ready OpenSpec changes, and prepared FF validation gates.
- 2026-06-30T07:28:31Z live demo10413 proof passed runtime preflight but blocked on ownerless subordinate create
  URL; no save was attempted and owned TestClient/Xvfb cleanup completed with Apache active.
- 2026-06-30T07:35:00Z implementation verified, matrix archive gates passed with provider gaps, specs synced and
  changes archived.
