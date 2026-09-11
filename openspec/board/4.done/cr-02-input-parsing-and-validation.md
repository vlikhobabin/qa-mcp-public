# CR-02 — Input parsing & validation correctness

## Status
4.done

## Order Index
2

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Multi-agent code review 2026-07-02, findings S1, S5, S6, m2, and the Gherkin
  parser-family notes. Full report: `docs/code-review-2026-07-02.md`.

## Summary
Several inputs are silently mis-parsed or accepted out of range, so a scenario
can "pass" while doing the wrong thing, or a value/date/match-mode is quietly
corrupted. All fixes are **offline-testable** (pure parsing/validation, no live
client). Grouped because they share one theme: reject or correctly parse bad
input instead of silently degrading.

## Problems (verified against code)

### S1 — Gherkin quoted values with an inner quote are silently truncated
`src/qa_mcp/scenario/gherkin.py:41` (`_q`): the pattern
`['\"](?P<name>[^'\"]*)['\"]` stops at the **first** quote of either kind and
accepts mismatched delimiters. Verified:
`... я ввожу текст 'ООО "Ромашка"'` transpiles (not "unmapped") with
`new_value == 'ООО '` — the wrong value is then actually typed into the form and
the scenario can still pass. Real 1C names/values contain `"…"` routinely. This
also breaks round-tripping of `read_form_descriptor`'s generated
`стал равен "V"` lines when `V` contains a quote.

### S5 — `data/odata.py` `match_value` treats an unknown mode as `equals`
`src/qa_mcp/data/odata.py:122-130`: unknown `mode` falls through to
`actual_s == expected`. Contrast the UI-side `mcp_server._match_value` which
raises on unknown mode. `assert_data(match="numeric")` (a mode the UI assert
supports) silently degrades to string equality — `"120,50"` vs `"120.5"` → false
red; a typo like `"conatins"` → false green when the strings happen to be equal.

### S6 — `set_table_date_cell` accepts out-of-range dates + leaks an open calendar
`src/qa_mcp/mcp_server.py:2143-2145` and `:2296-2298`: the date is `int()`-parsed
into `d, m, y` with **no range check** (unlike `write_form_date`'s
`_normalize_form_date`), so `date="99.99.2026"` passes and drives
`calendar_month_cell(99)` / `calendar_day_cell(...)` mouse clicks at nonsense
coordinates on the live form. Related: `_drive_calendar_pick` opens the calendar
dropdown **before** the backward-year guard, so a `status: "blocked"` return
leaves the popup open — state leaks into the next screenshot/click.

### m2 — Rare non-deterministic bootstrap crash from the counter base
`src/qa_mcp/protocol/bootstrap_synth.py:178`: `counter_base` is drawn uniformly
in `[10000, 99999]`, but frame 4 uses `base + 3` (`counter_delta: 3`). A base
≥ 99997 raises `ValueError("counter 100000 does not fit the fixed 5-digit
field")` — a ~1/30000 random session-bootstrap crash.

### Gherkin parser family (grouped with S1)
`src/qa_mcp/scenario/gherkin.py`: a second `Примеры:` block's header row is
consumed as a data row (`:464-470`) → a bogus extra scenario; triple-quoted
`"""` pystrings are unsupported (their lines become steps/unmapped); `\|`-escaped
pipes in table cells are not handled (`_split_row:353`).

## Recommended remediation
- **S1:** make `_q` require matching delimiters and allow the *other* quote char
  inside — e.g. two alternatives `"(?P<name>[^"]*)"` / `'(?P<name>[^']*)'`. Add a
  transpile test for values containing `"…"` and `'…'`.
- **S5:** raise `ValueError` on unknown mode in `odata.match_value` (mirror
  `mcp_server._match_value`); add the `numeric` mode if `assert_data` advertises
  it, or document the supported set. Unit test: unknown mode raises; `numeric`
  handles `"120,50"` vs `"120.5"`.
- **S6:** parse the date via a single shared validated parser (reuse/extend
  `_normalize_form_date`) that rejects out-of-range `d/m/y`; return
  `status: "blocked", reason: "invalid_date"` **before** opening the calendar,
  and ensure any early-return path closes the popup (or never opens it).
- **m2:** cap the random range at `99999 - max_counter_delta` (compute
  `max_delta` from the template rather than hard-coding 3).
- **Gherkin family:** skip the header row of every `Примеры:` block (not just the
  first); either support or explicitly reject `"""` docstrings with a clear
  unmapped reason; handle `\|` escaping in `_split_row`.

## Acceptance
- Transpiling a step whose value is `'ООО "Ромашка"'` yields the full value
  `ООО "Ромашка"` (and the symmetric `"…'…'…"` case) — new test in
  `tests/test_scenario_gherkin.py`.
- `odata.match_value(actual, expected, mode="__bogus__")` raises `ValueError`;
  `numeric` mode compares numerically — new test in `tests/test_odata.py`.
- `set_table_date_cell(date="99.99.2026", ...)` returns a structured
  `blocked/invalid_date` result **without** clicking calendar coordinates and
  without leaving a calendar popup open; a valid date still works — new test.
- `bootstrap_synth` cannot raise the 5-digit-counter `ValueError` for any base in
  its random range — new test drives the boundary (base at max).
- A feature with two `Примеры:` blocks generates exactly the expected scenarios
  (no bogus header-row scenario) — new test.
- `uv run pytest -q` green.

## Suggested change decomposition (for `$opsx-ff`)
- **Change 1 — `gherkin-quote-and-examples`** (capability: scenario gherkin):
  S1 + Examples/docstring/escaped-pipe handling.
- **Change 2 — `assert-and-date-validation`** (capability: data-layer assert +
  date-cell): S5 + S6 + the shared validated date parser.
- **Change 3 — `bootstrap-counter-bound`** (capability: protocol bootstrap): m2.

## Change Set
1. `openspec/changes/archive/2026-07-02-gherkin-quote-and-examples/` — preserve Gherkin quoted values, examples
   blocks, escaped pipes and explicit docstring handling.
2. `openspec/changes/archive/2026-07-02-assert-and-date-validation/` — fail closed on OData match modes and invalid
   table date-cell input.
3. `openspec/changes/archive/2026-07-02-bootstrap-counter-bound/` — keep synthesized bootstrap random counters within
   fixed-width bounds.

## Change 1: `gherkin-quote-and-examples`

### Why
Gherkin feature text can be silently corrupted before execution when quoted values contain the other quote character,
when a second examples block is parsed, or when a DataTable cell contains an escaped pipe.

### Goal
Make Gherkin parsing preserve the intended input or fail closed with an unmapped diagnostic for unsupported docstrings.

### Scope
- `src/qa_mcp/scenario/gherkin.py`
- focused offline tests in `tests/test_scenario_gherkin.py`
- `qa-mcp-protocol-lab` delta spec

### Acceptance
- `'ООО "Ромашка"'` and the symmetric double-quoted/single-quote value transpile without truncation.
- Multiple examples blocks expand data rows only.
- `\|` remains a literal pipe inside a table cell.
- Triple-quoted docstrings are reported as unsupported/unmapped rather than executable steps.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-gherkin-quote-and-examples/`

## Change 2: `assert-and-date-validation`

### Why
Unknown data assertion match modes and impossible table date-cell dates currently degrade silently, producing false
assertions or unsafe live calendar clicks.

### Goal
Reject unsupported match modes and invalid dates before misleading comparisons or UI interaction, while preserving valid
numeric and date paths.

### Scope
- `src/qa_mcp/data/odata.py`
- `src/qa_mcp/mcp_server.py`
- focused offline tests in `tests/test_odata.py` and `tests/test_mcp_server.py`
- `qa-mcp-protocol-lab` delta spec

### Acceptance
- `odata.match_value(..., mode="__bogus__")` raises `ValueError`.
- `numeric` mode compares locale-formatted decimals such as `120,50` and `120.5`.
- `set_table_date_cell(date="99.99.2026", ...)` returns `blocked/invalid_date` before calendar activation/clicks.
- Valid table date input still routes to the existing calendar picker.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-assert-and-date-validation/`

## Change 3: `bootstrap-counter-bound`

### Why
The synthesized bootstrap default counter can rarely choose a base whose later frame counter no longer fits the fixed
five-digit field.

### Goal
Compute a safe random counter-base range from template counter deltas while keeping explicit invalid bases fail-fast.

### Scope
- `src/qa_mcp/protocol/bootstrap_synth.py`
- focused offline tests in `tests/test_bootstrap_synth.py`
- `qa-mcp-protocol-lab` delta spec

### Acceptance
- The highest generated random base renders frames 1..4 without counter overflow.
- Explicit invalid bases still raise `ValueError`.
- Existing independent-session and platform-version synthesis tests stay green.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-02-bootstrap-counter-bound/`

## Verify
- `uv run pytest tests/test_scenario_gherkin.py -q` — 18 passed.
- `uv run pytest tests/test_odata.py tests/test_mcp_server.py -q` — 58 passed.
- `uv run pytest tests/test_bootstrap_synth.py -q` — 10 passed.
- `uv run pytest tests/ -q` — 603 passed after the final change.
- `uv run python -m compileall -q src/qa_mcp` — passed.
- `openspec validate gherkin-quote-and-examples --strict` — passed before archive.
- `openspec validate assert-and-date-validation --strict` — passed before archive.
- `openspec validate bootstrap-counter-bound --strict` — passed before archive.
- Matrix preflight and archive-gate checks passed for all three changes:
  `.artifacts/openspec/gherkin-quote-and-examples/2026-07-02/`,
  `.artifacts/openspec/assert-and-date-validation/2026-07-02/`,
  `.artifacts/openspec/bootstrap-counter-bound/2026-07-02/`.
- `openspec validate --all` — passed after archiving all three changes.
- `git diff --check` — passed after whitespace cleanup.

## Archive
- `openspec/changes/archive/2026-07-02-gherkin-quote-and-examples/`
- `openspec/changes/archive/2026-07-02-assert-and-date-validation/`
- `openspec/changes/archive/2026-07-02-bootstrap-counter-bound/`

## Related
- `docs/code-review-2026-07-02.md` (S1, S5, S6, m2)
- CR-03 reuses the shared validated date parser if it lands here first.
- `openspec/changes/archive/2026-07-02-gherkin-quote-and-examples/`
- `openspec/changes/archive/2026-07-02-assert-and-date-validation/`
- `openspec/changes/archive/2026-07-02-bootstrap-counter-bound/`

## Result
Delivered and archived. Gherkin parsing now preserves embedded opposite quotes, skips each examples-block header,
preserves escaped table pipes and reports unsupported docstrings explicitly. OData assertions now fail closed on
unknown match modes and support numeric comparison. Table date-cell input is validated before UI interaction, and the
backward-year calendar guard no longer opens an unreachable dropdown. Synthesized bootstrap random counters now leave
room for all generated frame counters. Specs synced to `qa-mcp-protocol-lab`; offline verification is green. Published
by `$opsx-pub`.

## Next
- none

## Log
- 2026-07-02 card created from the code-review report (S1, S5, S6, m2, gherkin family).
- 2026-07-02 `$opsx-ff`: decomposed into three apply-ready changes, generated proposal/design/spec/tasks artifacts
  with verification matrix rows, and moved the card to `2.todo`.
- 2026-07-02 `$opsx-do`: implemented all three changes, added offline regression tests, synced +7 requirements into
  `qa-mcp-protocol-lab`, archived all three changes, and moved the card to `4.done`.
- 2026-07-02 `$opsx-pub`: committed the scoped delivery set and prepared it for `origin/main`.
