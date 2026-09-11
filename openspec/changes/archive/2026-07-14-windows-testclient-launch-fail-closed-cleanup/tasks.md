## 1. Source-Bound Launch

- [x] 1.1 Extend the invalid-version test with empty and whitespace-only requests and retain the RED result.
- [x] 1.2 Require a non-empty exact four-component platform version before executable resolution.

## 2. Exact Task Cleanup

- [x] 2.1 Add contract coverage for a Go-owned exact-name unregister command and cancellation-independent bounded context.
- [x] 2.2 Implement idempotent cleanup before launch return, fail closed on explicit cleanup failure and retain an unexpected-return fallback.
- [x] 2.3 Remove the unused lifecycle import reported by review.

## 3. Verification And Handoff

- [x] 3.1 Run focused and full offline Python tests, native Go tests, Windows test cross-build, focused Ruff, strict OpenSpec and `git diff --check`.
- [x] 3.2 Sync both security/endpoint contracts and update the combined QA delivery card with exact evidence.
