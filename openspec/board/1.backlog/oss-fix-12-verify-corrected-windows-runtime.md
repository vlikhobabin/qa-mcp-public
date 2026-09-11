# Verify the corrected Python and Windows bridge runtime together

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-12

## Order Index

406.31

## OpenSpec Stage

operator-refined backlog draft; not admitted

## Priority

release gate

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage code review, 2026-09-05, finding R1-R9 integration, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- The symptom and required regression are restated here; ignored local review files are optional context, not clean-clone prerequisites. Original reproduction tests asserted the bug and must be inverted into desired-behavior regressions.

## Summary

Go tests and cross-builds do not prove the native consumer behavior after Python composition/target/evidence fixes. Verify one separately authorized Windows bridge target with exact source and executable identity through the public Python entrypoints.

## Acceptance

### Requirement: Admit one exact native contour

#### Scenario: Correction 12 control 1

- WHEN the operator approves exact target, artifact, commands and effects, THEN Linux preflight and Windows target/session/desktop readiness succeed before execution; cross-compilation alone and old-source reports cannot satisfy admission.

### Requirement: Verify the real public integration

#### Scenario: Correction 12 control 2

- WHEN the admitted matrix runs through the composed Python API, THEN authenticated handshake/relay, owned lifecycle, default BDD read/assertion, lifecycle-addressed display and evidence retention/refusal behave as specified; current settings and logical target never cross-route.

### Requirement: Verify recovery without collateral cleanup

#### Scenario: Correction 12 control 3

- WHEN the matrix completes or aborts, THEN only run-owned process/handles/listeners/staging are cleaned, unrelated sessions/resources are preserved, and retained evidence binds executable hash, source, target/session, verdict and before-after inventory without raw UI or credentials.

## Scope

- `Windows-native standalone bridge/TestClient qualification; Linux orchestration; ignored current-run evidence`
- Focused regression tests: `tests/test_standalone_host_bridge.py`, `tests/test_display_backend.py`, `tests/test_target_bound_evidence_cleanup.py`.
- Direct updates to the governing canonical specs and consumer documentation only when the corrected contract changes. No new legacy lifecycle artifacts.

## Affected Capabilities

- One corrected Python source and Windows bridge artifact pair has native lifecycle/route/display/evidence proof with exact-owned cleanup.

## Non-Goals

- No Linux-native qualification, bridge API redesign, new installer workflow, business mutations by implication, release publication, migration pilot or hidden external-processor retry.
- No unrelated changes, automatic publication or authority to execute this card from a planning request.

## Depends On

- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`
- `openspec/board/4.done/oss-fix-02-reject-unproven-project-attach.md`
- `openspec/board/4.done/oss-fix-03-enforce-native-operation-admission.md`
- `openspec/board/4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md`
- `openspec/board/4.done/oss-fix-04b-isolate-testclient-transport-settings.md`
- `openspec/board/4.done/oss-fix-04c-isolate-workspace-and-ownership-roots.md`
- `openspec/board/4.done/oss-fix-05-preserve-standalone-screenshot-evidence.md`
- `openspec/board/4.done/oss-fix-06-preserve-display-failure-verdicts.md`
- `openspec/board/2.todo/oss-fix-07-make-bound-window-reads-useful.md`
- `openspec/board/2.todo/oss-fix-08-bind-artifacts-at-trusted-production.md`
- `openspec/board/1.backlog/oss-fix-09a-admit-default-bdd-session-and-reads.md`
- `openspec/board/1.backlog/oss-fix-09b-admit-stateful-and-nested-bdd-steps.md`
- `openspec/board/1.backlog/oss-fix-09c-control-session-independent-bdd-steps.md`

## Change Set

- `oss-fix-12-admit-and-check-windows-matrix`
- `oss-fix-12-prove-owned-windows-cleanup`

## Design

Prepare exact evidence using existing Linux shell/Python orchestration. No new PowerShell/cmd/bat/WSL workflow is introduced. Native target/operator access is a prerequisite, not assumed. The bridge binary must identify the source actually under test; do not deploy the review's local cross-build as if it were a release. Product corrections are separate work.

## Implementation Plan

1. After separate target/command approval and successful preflight, execute the bounded authenticated Python-to-bridge matrix and current-source negative controls.
2. Verify exact lifecycle/process/relay cleanup, keep unrelated resources untouched, and retain sanitized source/artifact-bound evidence.
3. Complete focused evidence after final Result/Log edits; the authorized outer runner owns independent review, final verification, done, commit and push.

## Delivery Budget

- primary_invariant: One corrected Python source and Windows bridge artifact pair has native lifecycle/route/display/evidence proof with exact-owned cleanup.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 1
- estimated_product_files: 0
- estimated_production_loc: 0

## Budget Notes

Provisional estimate for one pre-admitted native qualification contour and its delivery checks, not a wall-clock promise or READY verdict. Product-file estimates exclude tests and docs; changes outside the named product seam require re-sizing, not a silent scope expansion.

## Canonical Specs

- `openspec/specs/qa-mcp-standalone-host-bridge/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`
- `openspec/specs/qa-mcp-shared-core-extension/spec.md`

## Verify

- `uv run pytest -q tests/test_standalone_host_bridge.py tests/test_display_backend.py tests/test_target_bound_evidence_cleanup.py`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests`
- `./bin/openspec validate --specs --strict --no-interactive`
- `go test -race ./...` and `go vet ./...` in `host-agent/windows-display-agent/`; cross-build plus separately admitted native proof, not cross-build as certification.

## Runtime And Authority

This plan does not grant runtime authority. Before delivery, agree the exact target, commands, allowed effects and recovery inventory; consult docs/development/runtime-lab-context.md and the corpus evidence contract. Report runtime_gap before execution if admission cannot be established. Only the admitted run may touch its exact-owned resources.

## Related

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `docs/development/local-changerail-delivery.md`
- `docs/development/legacy-board-transition.md`

## Result

not started; planning only. No finding is closed by this card's creation.

## Next

- Qualification requires FIX-04A/B/C and FIX-09A/B/C at the final tested source; the superseded FIX-04/FIX-09 aggregates are not completion prerequisites. Partial safe read-only BDD delivery cannot satisfy this gate.
- Review the draft at a clean tracked fingerprint, then perform local FF/admission before any todo transition. Numeric size checks alone do not authorize execution.
- Existing historical in-progress cards and the separately unapproved migration pilot remain unchanged. Resolve delivery readiness by the local workflow; never clean or publish unrelated work to satisfy a gate.

## Change 1: `oss-fix-12-admit-and-check-windows-matrix`

### Why

Go tests and cross-builds do not prove the native consumer behavior after Python composition/target/evidence fixes. Verify one separately authorized Windows bridge target with exact source and executable identity through the public Python entrypoints.

### Goal

After separate target/command approval and successful preflight, execute the bounded authenticated Python-to-bridge matrix and current-source negative controls.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- Card-level dependencies above.

### Ordered Tasks

1. After separate target/command approval and successful preflight, execute the bounded authenticated Python-to-bridge matrix and current-source negative controls.
2. Run `uv run pytest -q tests/test_standalone_host_bridge.py tests/test_display_backend.py tests/test_target_bound_evidence_cleanup.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Change 2: `oss-fix-12-prove-owned-windows-cleanup`

### Why

The first checkpoint alone does not prove the full card invariant; verify its required consumer/policy controls.

### Goal

Verify exact lifecycle/process/relay cleanup, keep unrelated resources untouched, and retain sanitized source/artifact-bound evidence.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- `oss-fix-12-admit-and-check-windows-matrix`.

### Ordered Tasks

1. Verify exact lifecycle/process/relay cleanup, keep unrelated resources untouched, and retain sanitized source/artifact-bound evidence.
2. Run `uv run pytest -q tests/test_standalone_host_bridge.py tests/test_display_backend.py tests/test_target_bound_evidence_cleanup.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-05T08:38:59Z Replaced aggregate FIX-04/FIX-09 prerequisites with all six named successor drafts; final-source/runtime authority gates unchanged.
