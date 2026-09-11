# bootstrap: version-aware platform selection + capture-coverage guard

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Delivery-system audit 2026-07-06 (5-agent parallel audit). Canonical report (root repo):
  `docs/audits/delivery-system-audit-2026-07-06.md` -> findings **F3 (HIGH)** and **D9**.
- Related existing card: `qa-mcp/openspec/board/1.backlog/118-2026-06-25-p5-multi-version-delivery.md`
  (P5 multi-version) confirms the delivery-proof/docs cleanup for this was not started as of 2026-07-06.

## Problem
bootstrap auto-selects the newest installed 1C platform with a lexicographic sort and greenlights a
deployment whose capture-backed tools are guaranteed to fail.

Three compounding bugs:
1. `qa-mcp/delivery/bootstrap.ps1:116-117`:
   `Get-ChildItem "C:\Program Files\1cv8\*\bin\1cv8.exe" | Sort-Object FullName -Descending |
   Select-Object -First 1` is a **lexicographic** string sort, not a version sort. It picks 8.5.1.x
   over 8.3.27.x, and would even pick 8.3.9.x over 8.3.27.x ("9" > "2" as strings).
2. bootstrap never validates `$PlatformVersion` against supported/covered families; it passes it into
   the container (`-e QA_MCP_PLATFORM_VERSION=...`, `:242`) and reports success.
3. Runtime `resolve_capture_dir()` (`src/qa_mcp/protocol/bootstrap.py:23-44`,
   `src/qa_mcp/_bundled/__init__.py:36-40`) maps 8.5.x -> the empty `_bundled/8.5/` slot with **no
   fallback to 8.3** -> `FileNotFoundError` -> the observed `capture-not-found:nextrow` tool
   failures. Meanwhile `versioning.active_version_key()` declares 8.5 "supported" so nothing fails at
   startup.

Doc contradiction (D9): `qa-mcp/delivery/README.md:19` tells testers 8.3.27.2130 and 8.5.1.1343 are
both supported, but the shipped v0.2.3 image cannot serve capture-backed tools on 8.5.

## Evidence
Verified 2026-07-06 (per audit): the lexical sort at `bootstrap.ps1:116-117`; the empty `_bundled/8.5/`
(only a README; captures live under `_bundled/8.3/`); no 8.5->8.3 fallback in `resolve_capture_dir()`.
Re-verify current line numbers before editing.

## Failure scenario
A tester with 8.3.27 + 8.5.1 installed (exactly the historical-user case) runs bootstrap with defaults ->
everything reports green -> hours later the agent's grid-read tools fail with the opaque
`capture-not-found:nextrow`, looking like product breakage.

## Recommendation
- Version-aware sort: `Sort-Object { [version]($_.Directory.Parent.Name) }`.
- Prefer the newest platform whose family has a **populated** capture bundle.
- Emit a loud warning + `-PlatformExe` hint when the detected/selected family lacks capture coverage;
  do not silently report green.
- DECISION: EITHER implement the 8.5->8.3 capture fallback (the epic-112 "validate-first" design) OR
  stop claiming 8.5 support in `delivery/README.md` and add the D9 caveat. Record the choice.

## Acceptance Criteria
- [ ] Platform selection is version-aware -- given a fixture with both 8.3.27 and 8.5.1 present, it
  selects 8.3.27 (the family with a populated bundle). Add a test/assertion over that fixture.
- [ ] When the detected/selected family lacks capture coverage, bootstrap emits a LOUD warning naming
  `-PlatformExe` and does not silently report green.
- [ ] EITHER an 8.5->8.3 capture fallback is implemented (state the decision + prove a grid read works
  on 8.5 via fallback) OR `delivery/README.md` no longer claims 8.5 support and carries the caveat.
- [ ] The failure no longer surfaces as an opaque `capture-not-found:nextrow` hours after a "green"
  bootstrap -- the coverage gap is surfaced at bootstrap time.

## Reviewer verification
- Run the selection logic against a two-version fixture -> selects the covered family.
- Point bootstrap at an uncovered family -> warning is printed and green is NOT reported.
- `grep -n '8.5' qa-mcp/delivery/README.md` -> support claim matches the chosen decision.

## Scope
- In scope: `qa-mcp/delivery/bootstrap.ps1`, `src/qa_mcp/protocol/bootstrap.py`,
  `src/qa_mcp/_bundled/__init__.py`, `versioning`, `qa-mcp/delivery/README.md`.
- Out of scope: producing new 8.5 captures (that is the broader P5 multi-version card 118).

## Affected Repositories
- qa-mcp. Cross-ref: root `audit-delivery-doc-drift` (D9), qa card 118 (P5 multi-version).

## Related
- root repo: `docs/audits/delivery-system-audit-2026-07-06.md`
- `qa-mcp/delivery/bootstrap.ps1`, `qa-mcp/src/qa_mcp/protocol/bootstrap.py`,
  `qa-mcp/src/qa_mcp/_bundled/__init__.py`, `qa-mcp/delivery/README.md`
- `qa-mcp/openspec/board/1.backlog/118-2026-06-25-p5-multi-version-delivery.md`
- `openspec/changes/bootstrap-platform-capture-coverage/`

## Change 1: `bootstrap-platform-capture-coverage`

### Why
Bootstrap and runtime capture lookup must agree on which platform families have
direct bundled captures and which families use the validated fallback.

### Goal
Make mixed 8.3/8.5 hosts default to a direct-covered platform, keep explicit 8.5
selection diagnosed, and prevent capture-backed tools from failing later with an
opaque `capture-not-found` for the supported fallback case.

### Scope
- `delivery/bootstrap.ps1` platform discovery and diagnostics.
- Python bundled-capture family selection in `src/qa_mcp/_bundled/`,
  `src/qa_mcp/protocol/bootstrap.py`, and accepted-mapping lookup.
- Delivery/bundled-corpus docs and focused tests.

### Acceptance
- Mixed 8.3/8.5 bootstrap fixture selects 8.3 by parsed version/direct coverage.
- Explicit 8.5 selection prints a warning and uses validated 8.3 protocol data.
- Unsupported platform families stop before a green deployment.
- `resolve_capture_dir()` for 8.5 resolves supported capture-backed operations
  through bundled 8.3 data.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-06-bootstrap-platform-capture-coverage/`

### Notes For `$openspec-ff-change`
- The 1C verification matrix is in `design.md`; Windows model-B live smoke is a
  release evidence follow-up, not executable inside this Linux workspace.

## Result
Implemented and archived `bootstrap-platform-capture-coverage`.

Archive:
- `openspec/changes/archive/2026-07-06-bootstrap-platform-capture-coverage/`

Verification:
- `openspec validate bootstrap-platform-capture-coverage --strict` passed before archive.
- `openspec validate qa-mcp-self-hosted-release --strict` passed.
- `openspec validate qa-mcp-protocol-lab --strict` passed.
- `openspec validate --all` passed before and after archive.
- `git diff --check` passed.
- `uv run --with pytest --with pyyaml pytest tests/test_bundled_versions.py tests/test_bootstrap_platform_selection.py` passed: 25 tests.
- `uv run --with pytest --with pyyaml pytest tests/test_replay.py tests/test_native_write.py::test_read_list_grid_keeps_adjacent_duplicate_rows tests/test_native_write.py::test_read_list_grid_empty_socket_response_is_truncated` passed: 4 tests.
- Linux-native 8.5 grid smoke passed after runtime preflight: `read_list_grid`
  on `Справочник.Товары` returned 5 rows through bundled 8.3 `nextrow`
  protocol data while `QA_MCP_PLATFORM_VERSION=8.5.1.1343`; retained sanitized
  evidence under `.artifacts/openspec/bootstrap-platform-capture-coverage/20260706T151132Z/8-5-grid-smoke/`.
- `uv run --with pytest --with pyyaml pytest` passed: 723 tests.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` passed: 0 findings.
- `uv run --with pytest --with pyyaml pytest -m smoke` passed: 2 tests, 721 deselected.
- Matrix preflight and archive gate passed; retained summary:
  `.artifacts/openspec/bootstrap-platform-capture-coverage/20260706T151132Z/verification-summary.md`.

## Next
- None.

## Log
- 2026-07-06 card created from the delivery-system audit (findings F3, D9).
- 2026-07-06 `$opsx-ff`: decomposed to one change,
  `bootstrap-platform-capture-coverage`, and moved to `2.todo`.
- 2026-07-06 `$opsx-do`: implemented bootstrap version-aware direct-coverage
  selection, explicit 8.5 to 8.3 protocol-data fallback, docs/tests/spec sync;
  archived `openspec/changes/archive/2026-07-06-bootstrap-platform-capture-coverage/`.
- 2026-07-06 `$opsx-pub`: committed scoped card delivery and prepared push to
  `origin/main`.
