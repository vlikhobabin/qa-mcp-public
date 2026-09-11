# Compose Project Target Readiness

## Status
4.done

## Owner
unassigned

## Series
oss-04c

## Order Index
4033

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Goal
Compose one resolved target into `ApplicationContext`, server startup and doctor
readiness while preserving ordinary unbound standalone behavior.

## Acceptance
- Bound server instances receive one immutable resolution and isolated state.
- Startup fails closed on an invalid configured handoff and stays unbound when
  the handoff is absent.
- Doctor reports a secret-safe ordered runtime-target readiness check.
- No lifecycle process starts during resolution/readiness.
- The payload stays at or below `300` added production LOC.

## Change Set
1. `compose-qa-mcp-project-target-readiness` -
   `openspec/changes/compose-qa-mcp-project-target-readiness/`

## Dependencies
- [OSS-04B](../4.done/oss-04b-resolve-provider-target-profile.md).

## Verify
- Bound/unbound application isolation, startup and doctor tests.
- Read-only Linux/Windows adapter preflight with no runtime process creation.
- Focused/full non-live, compilation, strict OpenSpec and review preflight.
- Test-first focused RED: `5 failed, 71 passed`; the failures observed the
  absent composition/readiness boundary before implementation.
- Focused application/MCP/doctor/startup suite: `253 passed` after rescue 2.
- Exact non-live CI/coverage gate: `1006 passed`, `73.53%` coverage after rescue 2.
- Python compilation, diff check and strict OpenSpec validation: passed.
- Linux exact-worktree readiness preflight: passed; listener count `39 → 39`,
  existing Xvfb identity unchanged, owned temporary profile removed.
- Windows exact-wheel readiness smoke: passed on
  `HISTORICAL-LAB-HOST\\User`; listener identity unchanged, no tracked process
  delta and owned staging removed.

## Result
One validated immutable resolution is now composed per application and exposed
as the first secret-safe doctor readiness check. Explicit, configured and
ordinary unbound startup are isolated; invalid or contradictory binding fails
closed before later runtime probes. No lifecycle authority was added. The
payload adds `181` production lines, below the `300`-line ceiling.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Archive
- `openspec/changes/archive/2026-08-25-compose-qa-mcp-project-target-readiness/`

## Next
- done

## Log
- 2026-08-25 created by the OSS-04 complexity investigation as payload C.
- 2026-08-25 unblocked by published OSS-04B; next sequential child.
- 2026-08-25 entered the supervised delivery pipeline from a clean synchronized `main`.
- 2026-08-25 implementation, cross-platform read-only evidence, focused/full
  gates and capability-spec sync completed.
- 2026-08-25 change archived after all eight tasks completed; card remains in
  `3.inprogress` for the independent review and publish gate.
- 2026-08-25 independent review cycle 1 returned `NO-GO`: self-consistent
  forged resolutions could bypass typed validation, and the composed
  `runtime_target` field was reassignable. Rescue attempt 1 closed both with
  secret-safe contract validation, write-once context semantics, regression
  coverage and refreshed exact-source Linux/Windows evidence.
- 2026-08-25 independent review cycle 2 returned `NO-GO`: structural
  self-consistency still could not prove resolver provenance, and nested target
  metadata remained mutable. Rescue attempt 2 replaced ad-hoc reconstruction
  checks with resolver-only validation sealing, froze resolver target metadata,
  added regression coverage and refreshed exact-source cross-platform evidence.
- 2026-08-25T09:45:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
