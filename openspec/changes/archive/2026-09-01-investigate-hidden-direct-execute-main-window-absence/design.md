## Context

The blocked S7 candidate composes published S1-R1 through S6 and is forbidden
to change those certified files. Its offline gates pass. The tracked EPF opens
the expected non-empty form in a visible Windows `/Execute` run. On the exact
hidden contour, however, synthetic lifecycle and the real S3 TestClient pass,
while S4 first reported `EnumDesktopWindows / ERROR_INVALID_DATA` and, after a
diagnostic bounded retry, waited sixty seconds at `main_not_ready`.

This is an investigation, not a protocol-capture claim. It observes Win32
process/job/desktop/window state already used by S1-S4 and hashes exact argv,
environment and fixture identity. No native TestClient traffic frames,
dynamic-field normalization or replay strategy changes.

## Goals / Non-Goals

**Goals:**
- Identify whether the missing S4 main identity is caused by process exit,
  `/Execute` admission, hidden-desktop placement, window class/owner timing,
  security-prompt state or another exact observable boundary.
- Reproduce the classification twice with the tracked fixture on the existing
  authorized target.
- Publish a decision that either enables an evidence-only correction or defines
  one bounded separately authorized replacement.
- Preserve exact-owned cleanup and privacy.

**Non-Goals:**
- Modify or republish S1-R1 through S6 or the S7 production payload.
- Admit a public route, prompt action, retry policy or new cleanup authority.
- Substitute an infobase, platform, principal, bridge or EPF.
- Capture protocol traffic, screenshots, OCR, UI text or credentials.

## Decisions

1. Build diagnostics from a clean composition of the exact published S6 plus
   blocked S7 test inputs, but keep every additional diagnostic source outside
   production packages/callers. Hash predecessor and S7 production files before
   and after each run.
2. Compare S3 and S4 as a timeline rather than as final statuses. Record only
   monotonic offsets, bounded process ids/exit codes, job membership booleans,
   desktop hashes, top-level window counts, class-name hashes/allowlisted class,
   owner relations and observer stages. Raw captions, UIA values and paths are
   excluded.
3. Sample both process liveness and hidden/operator desktop inventories through
   launch, listener readiness, `/Execute`, first window, terminal child exit and
   cleanup. An enumeration API error is a diagnostic event; it is neither
   ignored nor converted into admission success.
4. Use the tracked `run-1.epf` and exact S4 argv/environment. A control S3 run
   differs only by the published S3 contract. A visible run is prior fixture
   compatibility evidence, not a hidden-success substitute.
5. Require repeated evidence for the root-cause decision. If the correction is
   limited to test/runbook orchestration and preserves published bytes, record
   the exact S7 resume step. If production or a certified predecessor must
   change, create a bounded replacement/authorization card; do not patch S7.
6. Cleanup removes only current-run task, stage, process/job/desktop/TPort and
   restored configuration state. Retained evidence is ignored, hash/count only,
   and explicitly records preservation of unrelated resources.

## Risks / Trade-offs

- [Sampling changes timing] -> Use passive bounded sampling and confirm the
  classification with an uninstrumented exact S4 rerun.
- [Process exit is mistaken for `/Execute` rejection] -> Bind exit timing to
  listener/window/desktop stages and retain the bounded platform exit code.
- [Window class drift leaks raw UI] -> Retain only the allowlisted class or a
  class-name hash and structural owner relation.
- [A diagnostic retry weakens admission] -> Keep retry instrumentation test-only
  and require the final decision to preserve published fail-closed semantics.
- [Dirty S7 and OSS-07 files enter investigation scope] -> Use explicit manifest
  paths and predecessor hashes; never stage broad worktree state.

## Migration Plan

1. Prove exact baseline hashes, free target and owned cleanup preflight.
2. Add hostile/offline tests for the bounded diagnostic schema and no-production-
   caller invariant.
3. Run exact S3 control and two S4 timeline diagnostics, followed by one
   uninstrumented confirmation.
4. Classify the causal boundary and write the successor/resume decision.
5. Clean all owned runtime state, validate evidence/privacy/scope and request a
   fresh high-risk review.

Rollback removes the test-only diagnostics and ignored evidence. No production
or external publication state is changed.

## 1C Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason | Residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Read-only hidden 1C S3/S4 process, job, desktop, window and exit lifecycle on the authorized historical-user contour | Exact host/principal/platform/target preflight; published S3 control; repeated instrumented and uninstrumented S4 timelines; exact-owned cleanup | `scenario_log`, `active_window`, `cleanup_evidence` as privacy-safe hashes, counts, allowlisted classes, stages and exit codes | `.runtime/changerail/evidence/oss-06-s7-i1-investigate-hidden-direct-execute-main-window-absence/` | provided | N/A | Sampling exposed multiple exact lifecycle outcomes; S4-R1 owns deterministic stabilization before admission | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Managed form layout | Tracked EPF marker observation only; no form source or layout change | No visual mutation or screenshot plan; exact marker hash is deferred to stabilized S4-R1 passive UIA | N/A | N/A | N/A | This investigation changes no managed form and project privacy policy forbids raw UI retention | Marker hash remains uncertified until S4-R1 | `/opt/ai-dev-suite-for-1c/qa-mcp` |

The provided runtime row covers these retained outcomes: the published real S3
control exited zero; the first S4 matrix retained no admitted main class or
status token; fresh exact S4 rows varied between `main_not_ready` and
`window_inventory_failed`; and a later bounded receipt matrix reached listener
readiness with seven job-owned windows before `0xC0000005` exits without main
admission. No retained receipt proves hidden-main/passive-UIA admission. The
historical-user postflight restored exact config bytes/ACL, removed all owned residue
and preserved the named protected task, Docker and boot identities.

## Remaining Follow-up

- S4-R1 must make the worker/job/desktop observation lifetime deterministic
  and derive the tracked marker hash from a stabilized passive UIA run before
  S7 certification resumes.
