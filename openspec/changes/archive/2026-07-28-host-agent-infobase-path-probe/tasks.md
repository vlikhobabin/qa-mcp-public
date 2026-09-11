## 1. Regression Tests

- [x] 1.1 Add host-agent tests for successful marker hit, missing marker,
  missing host path, non-directory host path, and secret-safe response shape.
- [x] 1.2 Add fail-closed validation tests for empty path, NUL path, marker path
  separators, absolute markers, `.` and `..`.
- [x] 1.3 Add auth tests proving `POST /path/infobase` rejects missing or wrong
  tokens before probing.

## 2. Host-agent Implementation

- [x] 2.1 Register `POST /path/infobase` under the existing authenticated route
  wrapper.
- [x] 2.2 Implement bounded request validation and marker-only filesystem
  probing.
- [x] 2.3 Return only stable booleans, marker filename, response id, path kind,
  and sanitized failure reason.

## 3. Documentation And Specs

- [x] 3.1 Document the host-agent infobase marker probe in `host-agent/README.md`.
- [x] 3.2 Sync the `qa-mcp-windows-host-agent-security` delta spec.

## 4. Verification And Archive

- [x] 4.1 Record RED evidence for the focused host-agent test set before
  implementation.
- [x] 4.2 Run `go test ./...` in `host-agent/windows-display-agent`.
- [x] 4.3 Run `openspec validate host-agent-infobase-path-probe --strict`,
  `openspec validate qa-mcp-windows-host-agent-security --strict`,
  `openspec validate --all --strict`, and `git diff --check`.
- [x] 4.4 Archive the change after implementation, verification, and spec sync.
- [x] 4.5 Retain Windows-native host-agent endpoint evidence against the
  authorized lab target.

Verification evidence:

- RED before implementation:
  `go test -run 'TestInfobasePathProbe' ./...` in
  `host-agent/windows-display-agent` failed with expected `404 page not found`
  for `/path/infobase`.
- Focused GREEN:
  `go test -run 'TestInfobasePathProbe' ./...` in
  `host-agent/windows-display-agent` -> passed.
- Full host-agent GREEN:
  `go test ./...` in `host-agent/windows-display-agent` -> passed.
- Windows endpoint evidence:
  `.runtime/changerail/evidence/host-agent-path-demo10413-20260728T205000Z.json`
  confirms host `HISTORICAL-LAB-HOST`, current cross-built host-agent endpoint,
  `C:\1C_BASES\demo10413\1Cv8.1CD` marker existence, missing host path
  classification, auth failure, invalid marker rejection, and no submitted path
  leakage in response bodies.
- OpenSpec:
  `openspec validate host-agent-infobase-path-probe --strict` -> passed;
  `openspec validate qa-mcp-windows-host-agent-security --strict` -> passed;
  `openspec validate --all --strict` -> 17 passed, 0 failed.
- Whitespace: `git diff --check` -> passed.
- Archive:
  `openspec archive host-agent-infobase-path-probe --yes` archived the change
  as `openspec/changes/archive/2026-07-28-host-agent-infobase-path-probe/`.
