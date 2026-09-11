# Verify the corrected shared runtime on one authorized Linux target

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-11

## Order Index

406.30

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

Offline fixes cannot alone re-establish the claimed runtime behavior. On one separately approved Linux target, verify the final corrected lifecycle/read/BDD/display/evidence and exact-owned cleanup without reusing older-source certification.

## Acceptance

### Requirement: Require exact prior runtime admission

#### Scenario: Correction 11 control 1

- WHEN the operator approves the named target, exact commands and permitted effects, THEN Linux preflight verifies target, source fingerprint, ownership and recovery; absence/failure records runtime_gap before any live action.

### Requirement: Verify useful behavior and negative gates

#### Scenario: Correction 11 control 2

- WHEN the approved matrix runs, THEN owned lifecycle, default BDD reads/assertions, synthetic-safe display evidence and invalid-route refusals match the corrected contracts; any necessary UI action needs its own explicit safety/authority and no unsupported attach or external processor is certified.

### Requirement: Retain source-bound recovery evidence

#### Scenario: Correction 11 control 3

- WHEN the run completes or fails, THEN current target/session/hash/verdict evidence and before/after inventory are retained safely, only run-owned resources are removed, and required Apache restoration is proven; changed source invalidates dependent proof.

## Scope

- `Linux native TestClient qualification; existing public entrypoints only; ignored current-run evidence`
- Focused regression tests: `tests/test_target_bound_lifecycle_admission.py`, `tests/test_target_bound_evidence_cleanup.py`, `tests/test_scenario_runner.py`.
- Direct updates to the governing canonical specs and consumer documentation only when the corrected contract changes. No new legacy lifecycle artifacts.

## Affected Capabilities

- One final corrected source fingerprint has reproducible Linux runtime evidence and exact-owned cleanup.

## Non-Goals

- No Windows work, infobase provisioning, business mutations by implication, migration pilot, OSS-06 retry or product fixes.
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

- `oss-fix-11-admit-and-check-linux-matrix`
- `oss-fix-11-prove-owned-linux-cleanup`

## Design

Choose one exact fixture target only during separately approved runtime admission; do not embed laboratory identities in the card. Reuse successful final offline evidence at an unchanged fingerprint. This card cannot repair product code; findings return to the owning correction card/successor, after which affected proof is repeated.

## Implementation Plan

1. Prepare the exact read/safe-action matrix and recovery inventory, obtain separate runtime approval, run Linux preflight, then execute the admitted matrix only.
2. Perform exact-owned cleanup, verify target/resource before-after facts and retain a public-safe evidence index linked to the source fingerprint.
3. Complete focused evidence after final Result/Log edits; the authorized outer runner owns independent review, final verification, done, commit and push.

## Delivery Budget

- primary_invariant: One final corrected source fingerprint has reproducible Linux runtime evidence and exact-owned cleanup.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 1
- estimated_product_files: 0
- estimated_production_loc: 0

## Budget Notes

Provisional estimate for one pre-admitted native qualification contour and its delivery checks, not a wall-clock promise or READY verdict. Product-file estimates exclude tests and docs; changes outside the named product seam require re-sizing, not a silent scope expansion.

## Canonical Specs

- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`
- `openspec/specs/qa-mcp-target-bound-testclient-lifecycle/spec.md`
- `openspec/specs/qa-mcp-shared-core-extension/spec.md`

## Verify

- `uv run pytest -q tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py tests/test_scenario_runner.py`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests`
- `./bin/openspec validate --specs --strict --no-interactive`

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

## Change 1: `oss-fix-11-admit-and-check-linux-matrix`

### Why

Offline fixes cannot alone re-establish the claimed runtime behavior. On one separately approved Linux target, verify the final corrected lifecycle/read/BDD/display/evidence and exact-owned cleanup without reusing older-source certification.

### Goal

Prepare the exact read/safe-action matrix and recovery inventory, obtain separate runtime approval, run Linux preflight, then execute the admitted matrix only.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- Card-level dependencies above.

### Ordered Tasks

1. Prepare the exact read/safe-action matrix and recovery inventory, obtain separate runtime approval, run Linux preflight, then execute the admitted matrix only.
2. Run `uv run pytest -q tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py tests/test_scenario_runner.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Change 2: `oss-fix-11-prove-owned-linux-cleanup`

### Why

The first checkpoint alone does not prove the full card invariant; verify its required consumer/policy controls.

### Goal

Perform exact-owned cleanup, verify target/resource before-after facts and retain a public-safe evidence index linked to the source fingerprint.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- `oss-fix-11-admit-and-check-linux-matrix`.

### Ordered Tasks

1. Perform exact-owned cleanup, verify target/resource before-after facts and retain a public-safe evidence index linked to the source fingerprint.
2. Run `uv run pytest -q tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py tests/test_scenario_runner.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-05T08:38:59Z Replaced aggregate FIX-04/FIX-09 prerequisites with all six named successor drafts; final-source/runtime authority gates unchanged.
