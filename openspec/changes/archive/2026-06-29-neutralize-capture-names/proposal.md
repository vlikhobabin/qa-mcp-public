## Why

The bundled capture directories carry R&D-trace names —
`genuine-card98-demo-write`, `genuine-card97-ch3-cellread-20260619`,
`genuine-multiaction-clean-20260617`, … — that embed **card numbers and capture
dates** in the **shipped** surface (the `_bundled` tree and the `capture=` default
values exposed in the MCP tool schemas). Even with the data encrypted at rest
(`encrypt-bundled-data`), the directory names appear as readable default-argument
strings in the (still-`.py`) `mcp_server.py` tool signatures. Neutral,
descriptive names remove the internal trace from the product surface while keeping
the descriptive meaning, so research lookup is unaffected (the card number + date
live in git + the board).

This is the **only in-repo source change** in card 122. It touches **Python
manager code** (the `capture=` defaults + `resolve_capture_dir` references) and the
**bundled data dir names**; it requires **only offline capture evidence** (the
renamed captures still resolve and the offline suite stays green).

## What Changes

- Rename the **13 bundled** capture directories under
  `src/qa_mcp/_bundled/<version>/captures/` from `genuine-cardNN-<topic>-<date>` to
  **neutral-descriptive** names (`<topic>`), e.g.:
  - `genuine-card98-demo-write` → `demo-write`
  - `genuine-card98-listform-read` → `listform-read`
  - `genuine-card98-nextrow` / `-flat` / `genuine-card98-rowbyvalue` →
    `nextrow` / `nextrow-flat` / `rowbyvalue`
  - `genuine-card97-ch3-cellread-20260619` → `cellread`,
    `genuine-card97-ch3-report-20260619` → `report`,
    `genuine-card97-ch4-search/-advsearch/-viewmode-20260619` →
    `search` / `advsearch` / `viewmode`
  - `genuine-commit-conn` → `commit-conn`,
    `genuine-multiaction-clean-20260617` → `multiaction-clean`
  - (`tm-v1-ro-batchQ3`, the read-only default, carries no card#/date — optionally
    normalize to a clearer neutral name; otherwise leave it.)
- Update the **code defaults that reference the renamed bundled captures**: the
  `capture=` / `capture_dir=` tool defaults in `mcp_server.py`, the
  `_FOREGROUND_CAPTURE` constant, and any `resolve_capture_dir(...)` literal that
  names a renamed bundled dir, plus the same defaults in `scenario/runner.py` and
  the `protocol/` modules that reference them.
- **Research-safe:** the descriptive meaning is preserved; the card number + date
  move to git history + the board. No protocol logic changes.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: the bundled captures carry **neutral, descriptive
  identities** (no card numbers / dates) in the shipped data tree and in the
  `capture=` default values exposed by the tool schemas, while the engine resolves
  and replays them unchanged.

## Impact

- **Bundled data:** rename the 13 capture dirs under `_bundled/<version>/captures/`
  (apply the same rename to every populated version family present, e.g. `8.3`).
- **Python manager code:** `src/qa_mcp/mcp_server.py` (`capture=`/`capture_dir=`
  defaults, `_FOREGROUND_CAPTURE`), `src/qa_mcp/scenario/runner.py`, and
  `protocol/` modules (`native_write.py`, `native_xtest.py`, `navigation.py`,
  `responses.py`) where a **renamed bundled** capture is referenced.
- **Tests:** update any test that names a renamed bundled capture.
- **Out of scope (related, not this change):** the **dev-only** captures referenced
  as tool defaults but not in the bundled set (`genuine-card90-…`, `genuine-card96-…`,
  the `runtime/`-resolved `…/traffic-selfcontained` defaults) — those resolve from
  the dev tree and do not ship; the broader runtime-exposed-string scrub is card 123.
- **No `_bundled` re-encoding, no API/schema shape change** (only default-value
  strings change). Offline `pytest` stays green.
