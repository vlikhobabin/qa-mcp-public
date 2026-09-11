## Context

The 13 bundled capture dirs (`_bundled/8.3/captures/genuine-card…`) and the
`capture=` defaults referencing them are runtime-exposed (the default strings
appear in the MCP tool input schemas, since `mcp_server.py` stays `.py`). Only the
**bundled** captures ship; the `genuine-card90/96/97-…/traffic-selfcontained`
defaults resolve from the dev `runtime/` tree and are not in the image.

## Goals / Non-Goals

- **Goal:** neutral descriptive names for the **shipped** bundled captures + their
  code defaults, with no behavior change.
- **Non-Goal:** the dev-only (`runtime/`-resolved) capture defaults and the broader
  runtime-exposed-docstring scrub (card 123).
- **Non-Goal:** changing capture contents or the resolution logic.

## Decisions

- **D1 — Rename only the bundled set + its references.** Map each of the 13 bundled
  dirs to a neutral name; update every literal that names a renamed bundled dir
  (`capture=`/`capture_dir=` defaults, `_FOREGROUND_CAPTURE`, `resolve_capture_dir`
  literals) across `mcp_server.py`, `scenario/runner.py`, and the `protocol/`
  modules. Apply the rename to every populated version family (`8.3`; `8.5` when
  populated).
- **D2 — Preserve descriptive meaning.** Names stay self-describing
  (`demo-write`, `listform-read`, `cellread`, `report`, `search`, `advsearch`,
  `viewmode`, `nextrow`, `nextrow-flat`, `rowbyvalue`, `commit-conn`,
  `multiaction-clean`). The card#/date is recoverable from git + the board.
- **D3 — `tm-v1-ro-batchQ3`** carries no card#/date; optional to normalize. Decide
  during `do` (leave, or rename to a clearer neutral like `readonly-batch`) —
  update `default_capture` + all `capture_dir` defaults + the bundled dir together
  if renamed.
- **D4 — Mechanical + test-guarded.** This is a rename, not a logic change; the
  offline suite (which loads these captures) is the guard. Grep to prove no
  remaining reference to an old bundled name in `src/` or tests.

## Risks / Trade-offs

- **Missed reference → FileNotFoundError at runtime.** Mitigated by a full grep
  sweep + the offline suite exercising the renamed captures.
- **Name collision** (two old dirs mapping to one neutral name): the proposed map is
  collision-free; verify during `do`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager code | `capture=` defaults + `resolve_capture_dir` literals | renamed to neutral; all refs updated | grep: zero old bundled names in `src/`+tests | local run log | planned | qa-mcp | — |
| Bundled data | 13 capture dirs renamed | neutral dir names; engine resolves them | offline `pytest` green (captures load + replay) | CI / local run log | planned | qa-mcp | — |
| QA/TestClient runtime | replay parity of a renamed capture | a renamed capture drives a real client | a scenario using a renamed capture runs (lab, optional) | `.artifacts/openspec/neutralize-capture-names/<run-id>/` | planned | qa-mcp | offline replay suffices for the rename; lab optional |

Residual risk: none beyond a missed reference (grep-guarded).
