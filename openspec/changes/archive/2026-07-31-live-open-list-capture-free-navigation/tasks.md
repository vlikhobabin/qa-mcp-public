## 1. Endpoint Contract Tests

- [x] 1.1 Add focused RED tests proving omitted and blank `capture` select the template-backed path instead of capture resolution, while a non-blank bundled capture still uses explicit derivation.
- [x] 1.2 Add preflight regressions proving a missing file, loadable
  template sets missing frames 8, 9, 10 or 218, and a malformed splice marker
  return `open-list-navigation-unavailable` without constructing a TestClient
  session or attempting a protocol write.
- [x] 1.3 Keep the attach-aware endpoint registry test green for both template-backed and explicit-capture `open_list` paths; document why these tests observe the public dispatch boundary and would fail on the historical default regression.

## 2. Capture-Free Navigation Implementation

- [x] 2.1 Add an asset-preflight helper that resolves the bundled bootstrap,
  loads the selected value-read templates, renders bootstrap frames 8–10 and
  the required no-form splice header, and synthesizes bootstrap state before
  any connection opens.
- [x] 2.2 Route omitted/blank `capture` through the preflighted live navigation helper, preserve non-blank explicit capture replay, and return a sanitized typed capability diagnostic for preflight failures.
- [x] 2.3 Update the `open_list` public documentation/schema description to explain template-backed default navigation, the explicit capture compatibility selector, and safe no-write failure behavior.

## 3. Verification And Evidence

- [x] 3.1 Run the focused endpoint/protocol tests and `python3 -m compileall -q src/qa_mcp`; record commands and observed outcomes.
- [x] 3.2 Run `uv run --with pytest --with pyyaml pytest -q`, `openspec validate live-open-list-capture-free-navigation --strict`, `openspec validate --all --strict`, and `git diff --check`.
- [x] 3.3 Run the Linux runtime preflight before any local live probe; then retain a bounded Windows/remote TestClient attach-open-list-cleanup proof under `.runtime/changerail/evidence/live-open-list-capture-free-navigation/`, or record a typed runtime gap and resume condition if the authorized contour is unavailable.
- [x] 3.4 Confirm the verification matrix: form-command/navigation and runtime-delivery rows have evidence; BSL, metadata, role, posting, report, and migration rows remain `N/A` because no 1C source or persisted state changed; no protocol evidence index update is needed because the implementation reuses the existing frame-14 navigation claim.

## Evidence

- RED: the focused endpoint command covering the new cases plus the existing
  endpoint registry returned `31 failed, 1 passed` before implementation. The
  failures were the missing template-backed helper/signature and the old
  `invalid-arguments` result for `navigation_templates`.
- GREEN focused:
  `uv run --with pytest --with pyyaml pytest tests/test_mcp_server.py::test_open_list_omitted_or_blank_capture_uses_navigation_templates tests/test_mcp_server.py::test_open_list_preflights_before_attached_endpoint_liveness tests/test_mcp_server.py::test_open_list_explicit_bundled_capture_keeps_legacy_derivation tests/test_mcp_server.py::test_open_list_missing_navigation_template_fails_before_session tests/test_mcp_server.py::test_open_list_incomplete_navigation_template_fails_before_session tests/test_mcp_server.py::test_open_list_navigation_template_without_splice_marker_fails_before_session tests/test_mcp_server.py::test_open_list_explicit_bundled_navigation_template_preflights_before_open tests/test_mcp_server.py::test_open_list_public_default_contains_no_development_capture_name tests/test_mcp_server.py::test_attach_endpoint_contract_for_action_tools tests/test_mcp_server.py::test_open_list_explicit_capture_uses_attached_endpoint -q`
  -> `40 passed in 2.54s`; `python3 -m compileall -q src/qa_mcp` -> passed.
- Test adequacy: these tests call the decorated public function, assert the
  omitted/blank versus explicit dispatch boundary, load the real shipped
  bundled template before a stubbed live open, and exercise syntactically valid
  template files with each required bootstrap/splice frame or marker removed.
  `TestClientSession` is replaced with a constructor that fails if any of those
  incomplete assets reaches connection setup. Active stale-attachment cases
  also assert that liveness is never called for invalid assets, while a success
  case asserts the order `asset preflight -> attachment liveness -> live open`.
  Reintroducing the historical default, `/work` empty-path resolution, or any
  pre-preflight socket makes them fail.
- Full Python: `uv run --with pytest --with pyyaml pytest -q` -> `892 passed in
  75.93s` after review-rescue cycle 3.
- Final static/OpenSpec: `python3 -m compileall -q src/qa_mcp` -> passed;
  `openspec validate live-open-list-capture-free-navigation --strict` ->
  passed; `openspec validate --all --strict` -> `20 passed, 0 failed`;
  `git diff --check` -> passed; untracked planning/card files contain no
  trailing whitespace; sanitized runtime summary parses as JSON.
- Runtime preflight: the configured local MCP provider recorded a pre-execution
  `runtime_gap` (`bearer-token-env-missing`, `testclient-tport-unreachable`).
  The authorized Windows target preflight then passed on `HISTORICAL-LAB-HOST` with
  the demo infobase marker present and unique proof ports free.
- Windows/live: current working-tree source invoked `open_list` with omitted
  `capture` through an SSH loopback tunnel and returned `ok=true`,
  `accepted=true`, `navigation_method=template-backed`, `opened=Валюты`, and
  target `e1cib/list/Справочник.Валюты`. Review-rescue cycle 2 reran the proof
  with lifecycle-handle-only cleanup; the provider-owned lifecycle stopped
  cleanly and proof ports, task, stage, transient script, and tunnel are absent.
  Review-rescue cycle 3 reran the proof after moving preflight ahead of
  attachment resolution. Exact sanitized commands and observed outcomes are
  retained in
  `.runtime/changerail/evidence/live-open-list-capture-free-navigation/commands-cycle3.md`
  and summarized by `verification-summary.json`; no port-wide process cleanup
  fallback remains.
- Verification matrix: form-command/navigation and runtime-delivery rows are
  provided by the focused/full suite plus the live result and cleanup proof.
  BSL, metadata, role, posting, report, and migration remain `N/A` because no
  1C source or persisted state changed. No protocol evidence index update is
  required because the implementation reuses the established frame-14 claim.
