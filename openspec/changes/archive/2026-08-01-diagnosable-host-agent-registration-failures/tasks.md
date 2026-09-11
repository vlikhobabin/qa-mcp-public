## 1. Regression Contracts

- [x] 1.1 Add RED Go tests for HTTP-status health fields, 512-byte
  response-snippet bounding, credential redaction, escaped single-line logging,
  stale-status clearing, and endpoint-less URL warning behavior.
- [x] 1.2 Add a RED cross-repository pytest/Go contract harness that starts the
  real root `team_registry.py` router on loopback, invokes the Go registration
  client with `/v1/bridges/register`, and checks HTTP success plus the
  `bridge_registration/status:ok` audit row.

## 2. Host-Agent Diagnostics

- [x] 2.1 Implement `registry-rejected-<status>` and structured
  `last_http_status` state, including clearing stale HTTP status on success and
  non-HTTP failures without changing retry or health availability behavior.
- [x] 2.2 Log every non-2xx status with a response snippet redacted before it is
  bounded to 512 bytes and emitted with control-character escaping; never log
  registry credentials or bridge tokens.
- [x] 2.3 Add the one-line explicit registry URL startup warning for empty or
  slash-only paths and prove the configured URL is still used verbatim.

## 3. Verification And Evidence

- [x] 3.1 Run `gofmt`, focused Go tests, `go test ./...`, `go test -race ./...`,
  `go vet ./...`, and the focused real-router pytest contract with a passing,
  non-skipped result.
- [x] 3.2 Cross-build the Windows host agent and focused Go test executable,
  confirm `HISTORICAL-LAB-HOST` through explicit SSH to
  `historical-user@192.0.2.205`, run the focused diagnostics tests from a uniquely
  owned temporary directory, retain secret-free local evidence, and remove
  only those temporary remote files.
- [x] 3.3 Run the repository offline pytest floor,
  `openspec validate --all --strict`, and `git diff --check`; attempt the
  suite-root public-surface scanner and record its root-only contract as not
  applicable when no component contract exists; record exact outcomes in the
  delivery manifest/card without raw captures.
