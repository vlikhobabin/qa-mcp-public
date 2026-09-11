# Resolve The Provider Runtime Target Profile

## Status
4.done

## Owner
unassigned

## Series
oss-04b

## Order Index
4032

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Goal
Resolve the frozen project handoff against one ignored provider profile and
return a typed, secret-safe target resolution without lifecycle side effects.

## Acceptance
- Exact target id, kind, fingerprint, principal, receipt, generation and
  binding reference reconcile with the frozen handoff.
- Physical env and evidence root are regular allowlisted local paths.
- `sanitized` and approved `full_local` policies are enforced.
- Partial, stale, mismatched or malformed input fails closed without process or
  infobase side effects.
- The payload stays at or below `300` added production LOC.

## Change Set
1. `resolve-qa-mcp-provider-target-profile` -
   `openspec/changes/resolve-qa-mcp-provider-target-profile/`

## Dependencies
- [OSS-04A](../4.done/oss-04a-define-runtime-target-contract.md).
- Frozen `agent-core` contract commit `9bdefadb2861e6998bd2fa845a19fb3fa75f1fb4`.

## Verify
- File/client-server, both evidence policies, mismatch, symlink/path escape,
  partial handoff and secret-redaction tests.
- Focused and full non-live gates plus strict OpenSpec and review preflight.
- Focused resolver/contract suite: `42 passed`.
- Exact non-live CI/coverage gate: `997 passed`, `73.45%` coverage.
- Python compilation, diff check and strict OpenSpec validation: passed.
- Windows-native synthetic resolver smoke: passed on
  `HISTORICAL-LAB-HOST\\User`; no process/listener delta and owned stage removed.

## Result
The public resolver reconciles the complete frozen handoff with one closed,
ignored provider profile and returns immutable, secret-safe binding, profile
and observation models. File and client-server aliases, approved evidence
policies, physical path safety, stale/mismatch rejection and unbound mode are
covered without readiness, lifecycle, process, listener or infobase effects.
The payload is `297` added production lines, below the `300`-line ceiling.
Independent review cycle 5 returned `GO` with all five acceptance criteria
passed, zero findings and no unbacked claims.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-25 created by the OSS-04 complexity investigation as payload B.
- 2026-08-25 entered implementation after published OSS-04A; test-first RED
  proved the resolver export absent before the bounded implementation.
- 2026-08-25 resolver implementation, cross-platform negative coverage,
  Windows-native smoke, exact non-live suite, capability-spec sync and archive
  completed; awaiting independent review and publish.
- 2026-08-25 review cycle 1 returned `NO-GO`: missing evidence directories,
  string profile generations and rejected-value exception chaining were not
  closed strictly enough. Bounded rescue fixed all three, added regression
  coverage and refreshed the exact-source Windows smoke and cleanup evidence.
- 2026-08-25 review cycle 2 returned `NO-GO` because rejected raw JSON,
  UTF-8, policy and NUL-path values could remain in exception internals. The
  second bounded rescue normalizes outside active exception contexts, adds
  recursive sentinel regressions and refreshes the 11-case Windows evidence.
- 2026-08-25 review cycle 3 returned `NO-GO` for oversized decimal generations
  escaping Python's integer conversion limit. The third bounded rescue
  normalizes both handoff and JSON decoder limits, adds Linux/Windows sentinel
  coverage and refreshes the 12-fixture Windows evidence.
- 2026-08-25 review cycle 4 returned `NO-GO` for deeply nested valid JSON
  escaping as `RecursionError`. The fourth bounded rescue normalizes decoder
  recursion, adds the deep sentinel regression and refreshes the 13-fixture
  Windows evidence.
- 2026-08-25 independent review cycle 5 returned `GO` after a systematic
  458-case malformed-input matrix and 1500-case decoder/recursion fuzz found
  no remaining untyped or input-retaining exceptions.
- 2026-08-25T08:09:03Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
