## 1. Runtime Diagnostics

- [x] 1.1 Add an MCP diagnostic tool that echoes received `open_link` and arbitrary JSON argument values unchanged.
- [x] 1.2 Add structured mojibake warnings for replacement characters and long question-mark runs without rewriting caller values.
- [x] 1.3 Add a direct HTTP streamable-MCP UTF-8 request-body gate for non-UTF-8 charsets and invalid UTF-8 bytes.
- [x] 1.4 Preserve normal direct HTTP dispatch for valid UTF-8 JSON request bodies.

## 2. Documentation And Examples

- [x] 2.1 Update active Windows/PowerShell JSON-RPC examples to use UTF-8 bytes and `application/json; charset=utf-8`.
- [x] 2.2 Document the echo diagnostic and the non-UTF-8 failure mode in the install/troubleshooting runbooks.
- [x] 2.3 Sweep docs for manual Cyrillic JSON-RPC examples that omit explicit UTF-8 handling.

## 3. Tests And Evidence

- [x] 3.1 Add offline pytest coverage for clean Cyrillic echo diagnostics.
- [x] 3.2 Add offline pytest coverage for mojibake/replacement-character warnings.
- [x] 3.3 Add offline pytest coverage for the direct HTTP UTF-8 body gate.
- [x] 3.4 Record a retained pytest/docs-sweep summary under `.artifacts/openspec/jsonrpc-navlink-utf8-hardening/<run-id>/`.
- [x] 3.5 Record Windows model-B `read_list_grid` smoke as N/A for this Linux workspace unless a Windows host/TestClient is attached.

## 4. Validation

- [x] 4.1 Run focused pytest for the changed MCP server behavior.
- [x] 4.2 Run `openspec validate jsonrpc-navlink-utf8-hardening --strict`.
- [x] 4.3 Run `git diff --check`.
