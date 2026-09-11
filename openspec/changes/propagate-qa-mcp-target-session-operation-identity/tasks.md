## 1. Result And Artifact Contract

- [ ] 1.1 Extend `OperationResult` and `ArtifactReference` with optional bounded target/session/operation/binding provenance and secret-safe serialization.
- [ ] 1.2 Preserve unbound/downstream fake-executor compatibility and confirm added production LOC is at most `300`.

## 2. Common Identity Gate

- [ ] 2.1 Gate MCP/scenario execution on application target, session target, attachment identity/generation and supplied endpoint/display fields.
- [ ] 2.2 Stamp every verdict class and apply `sanitized` versus approved `full_local` artifact path retention.
- [ ] 2.3 Add tests that fail when local/Windows executors are invoked for stale, foreign or mismatched identity.
- [ ] 2.4 Run a Windows-native offline executor-contract smoke; no TestClient process is required.

## 3. Delivery Gate

- [ ] 3.1 Run focused core/MCP/scenario tests, compilation, exact non-live CI/coverage, diff check and strict OpenSpec validation.
- [ ] 3.2 Sync/archive and pass deterministic preflight plus fresh independent review before publication.
