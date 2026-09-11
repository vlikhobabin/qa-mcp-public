## 1. Regression Contract

- [x] 1.1 Add a focused startup/config regression that sets all legacy
  `QA_MCP_LICENSE_*` values, makes broker/subprocess execution fail the test,
  and proves `mcp_server.main()` reaches the MCP run boundary; record the
  pre-implementation RED result.
- [x] 1.2 Update config assertions so legacy product-license variables do not
  appear in `Settings` and arbitrary values cannot raise during settings load.

## 2. Remove Runtime Gate

- [x] 2.1 Remove the license-gate imports, startup enforcement helper/call, and
  license settings/constants from `mcp_server.py` and `config.py`.
- [x] 2.2 Remove `src/qa_mcp/license_gate.py` and retire tests that specify its
  broker decision matrix.

## 3. Verification

- [x] 3.1 Run the focused config/startup tests and a source scan proving the
  Python runtime contains no `ai1c-license` call or `QA_MCP_LICENSE_*` startup
  setting; record command and outcome.
- [x] 3.2 Run the focused startup regression in the available Windows-native
  verification contour, or retain a concrete runtime-gap result if that
  authorized contour cannot execute the changed worktree.
- [x] 3.3 Run `openspec validate short-circuit-qa-mcp-product-license-gate
  --strict` and `git diff --check`; protocol capture/evidence indexing is N/A
  because no TestClient protocol knowledge changes.
