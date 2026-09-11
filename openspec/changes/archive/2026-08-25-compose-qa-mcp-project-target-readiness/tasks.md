## 1. Application Composition

- [x] 1.1 Add optional immutable runtime-target resolution to `ApplicationContext` with per-instance isolation.
- [x] 1.2 Compose explicit/configured resolution once in MCP server startup while preserving absent-handoff standalone mode.
- [x] 1.3 Add ordered secret-safe doctor/readiness output and fail closed on configured resolution errors.
- [x] 1.4 Confirm added production LOC is at most `300` and lifecycle calls remain outside this payload.

## 2. No-Side-Effect Verification

- [x] 2.1 Test bound/unbound instance isolation, injected settings, startup errors and doctor serialization.
- [x] 2.2 Run Linux and authorized Windows-native read-only profile/readiness preflight and retain zero-process/listener mutation evidence.

## 3. Delivery Gate

- [x] 3.1 Run focused application/MCP/doctor tests, compilation, exact non-live CI/coverage, diff check and strict OpenSpec validation.
- [x] 3.2 Sync the capability spec and prepare the completed change for archive; deterministic preflight and fresh review remain card gates.
