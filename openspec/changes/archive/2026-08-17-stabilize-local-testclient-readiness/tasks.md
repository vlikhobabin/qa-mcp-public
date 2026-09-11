## 1. Lifecycle

- [x] 1.1 Add non-consuming listener and stable-process readiness checks.
- [x] 1.2 Return bounded secret-safe post-listener diagnostics.
- [x] 1.3 Clean ownership-matched Xvfb when the client already exited.
- [x] 1.4 Refuse occupied TPorts and persist ownership before readiness waits.

## 2. Runtime Profile And Diagnostics

- [x] 2.1 Load settings from `QA_MCP_TARGET_ENV_FILE` with explicit env taking precedence.
- [x] 2.2 Make doctor bearer defaults transport-aware.
- [x] 2.3 Classify manager handshake drift as a protocol diagnostic.

## 3. Verification

- [x] 3.1 Add focused lifecycle, settings, doctor and diagnostic regression tests.
- [x] 3.2 Run focused and full offline qa-mcp tests (`933 passed, 5 skipped`).
- [x] 3.3 Run strict OpenSpec validation and `git diff --check`.

## 4. Live Matrix

- [x] 4.1 Repeat the connected-project thick/thin launch and retain the observed result.
- [x] 4.2 Verify no owned TestClient/Xvfb/listener remains after each run.
- [x] 4.3 Exercise doctor, pure Gherkin tools, OData and descriptor diagnostics.
- [x] 4.4 Record N/A for BSL, metadata, roles and business-data mutation.
