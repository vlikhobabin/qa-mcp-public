## Context

The current product decision is validate-first multi-version support: 8.5.1.1343
was live-validated with the existing 8.3 protocol data while synthesized,
foreground and full captured-replay frames declare the live 8.5 version. The empty
`_bundled/8.5` slot is intentional, but the current bootstrap and resolver
behavior do not make that intent executable:

- `bootstrap.ps1` sorts candidate executable paths lexicographically and can
  prefer 8.5 only because the path string sorts later.
- `resolve_capture_dir()` asks `_bundled/8.5` for captures and then fails or
  falls through to dev runtime data, never to the validated bundled 8.3 corpus.
- Docs claim 8.5 support while the shipped capture-backed tools can fail with
  `capture-not-found:nextrow`.

## Decisions

- **Default auto-selection prefers direct coverage.** When no `-PlatformExe` is
  supplied, bootstrap sorts installed 1C executables by parsed `[version]` and
  selects the newest candidate whose family has direct bundled capture coverage
  (`8.3` today). This avoids silently booting a family whose bundle is empty.
- **Explicit 8.5 remains allowed and diagnosed.** If an operator passes an 8.5
  executable, bootstrap keeps it, passes the full version to
  `QA_MCP_PLATFORM_VERSION`, and prints a warning that 8.5 uses the validated
  8.3 protocol-data fallback until `_bundled/8.5` is populated.
- **Python fallback is explicit and central.** Add a dependency-free helper in
  `_bundled` that maps a requested family to the capture-data family. `8.5`
  maps to `8.3`; direct-covered families map to themselves. Runtime loaders use
  that helper before checking bundled capture and accepted-mapping paths.
- **Full replay streams still declare the live platform.** Capture-data fallback
  chooses byte sources, not the session's platform identity. Shared replay code
  stamps captured 8.3 platform-version bytes to the live version before GUID
  rebinding/sending.
- **Unsupported families still fail closed.** `active_version_key()` continues
  to reject unsupported families. The fallback is only for declared-supported
  families with an explicit compatibility decision.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `delivery/bootstrap.ps1` platform discovery and warnings | version-sorted fixture assertions over script text/helpers plus diff review | focused pytest over bootstrap script contract; `git diff --check` | `.artifacts/openspec/bootstrap-platform-capture-coverage/20260706T151132Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Windows PowerShell execution is not available inside the Linux workspace. |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | No 1C configuration source, metadata or BSL is edited. | None. |
| Delivery or runtime apply | Python capture lookup and replay stamping for 8.5 fallback | 8.5 requests resolve to bundled 8.3 capture data while full replay frames declare live 8.5 | focused pytest for `_bundled`, `resolve_capture_dir()` and `ReplaySession` version stamping | `.artifacts/openspec/bootstrap-platform-capture-coverage/20260706T151132Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline tests prove source behavior, not a real Windows Docker bootstrap. |
| QA/TestClient runtime | Linux-native 8.5 grid/read smoke through capture fallback | run Linux runtime preflight, launch 8.5 TestClient, read `Справочник.Товары` grid through bundled 8.3 `nextrow` capture | retained preflight, sanitized grid summary and cleanup proof | `.artifacts/openspec/bootstrap-platform-capture-coverage/20260706T151132Z/8-5-grid-smoke/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Verifies Linux-native protocol fallback, not Windows Docker Desktop/bootstrap packaging. |
| QA/TestClient runtime | Real 8.5 grid/read smoke through model-B bootstrap | release-smoke transcript using `QA_MCP_PLATFORM_VERSION=8.5.1.1343` and capture fallback | retained MCP tool transcript or live-regression bundle | `.artifacts/openspec/bootstrap-platform-capture-coverage/<release-run-id>/8-5-release-smoke/` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This Linux delivery does not run Windows Docker Desktop/bootstrap; Linux-native 8.5 proof is retained separately. | Medium: a packaging-only regression could still appear in the Windows release path. |

## Risks

- Choosing 8.3 by default on a mixed 8.3/8.5 host is conservative but may surprise
  an operator expecting the newest installed platform. The warning/docs must name
  `-PlatformExe` for explicit override.
- A silent 8.5 to 8.3 fallback would repeat the audit problem in a different
  form. The fallback must be documented in `_bundled/8.5/README.md`, delivery
  docs and tests.
