# Unify default BDD execution with the shared operation boundary

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-09

## Order Index

406.28

## OpenSpec Stage

superseded SPLIT_REQUIRED aggregate; planning history only; not a runner input

## Priority

P1

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage code review, 2026-09-05, finding R3, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- The symptom and required regression are restated here; ignored local review files are optional context, not clean-clone prerequisites. Original reproduction tests asserted the bug and must be inverted into desired-behavior regressions.

## Summary

run_scenario defaults to single_session and run_step forces it, but run_single_session invokes handles/resolvers directly. A deny-all executor is never called and raw UI is returned under sanitized policy. Unify operation control without breaking one-bootstrap cursor ordering or useful BDD actions.

This aggregate was decomposed at operator request. Its original Scope, Implementation Plan and Change checkpoints are retained as design history, not an execution plan. Use all named successors below; aggregate creation/decomposition closes no finding.

## Acceptance

### Requirement: Admit before opening the runtime

#### Scenario: Correction 09 control 1

- WHEN a bound run_scenario/run_step has invalid or missing session state, THEN it refuses before socket creation/bootstrap; when a selected executor denies an operation, THEN that operation cannot invoke the protocol handle or fallback resolver.

### Requirement: Preserve real BDD behavior

#### Scenario: Correction 09 control 2

- WHEN an admitted scenario performs read/assert/navigation/action/nested steps, THEN the selected executor controls applicable operations, bootstrap occurs once and cached reads/cursor order remain correct; unsupported steps return explicit blocked outcomes rather than bypassing policy.

### Requirement: Unify verdict and disclosure semantics

#### Scenario: Correction 09 control 3

- WHEN equivalent work runs through multi-session, single-session or default MCP entrypoints, THEN four verdict classes and trusted provenance agree, assertions use trusted internal data, and sanitized preview/error/attachments leak no raw UI or paths.

## Scope

- `src/qa_mcp/scenario/runner.py`
- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/core/operations.py`
- `src/qa_mcp/core/contracts.py`
- `src/qa_mcp/core/boundary.py`
- Focused regression tests: `tests/test_scenario_runner.py`, `tests/test_scenario_actions.py`, `tests/test_positive_operation_boundary_integration.py`, `tests/test_shared_core_extension.py`, `tests/test_mcp_server.py`.
- Direct updates to the governing canonical specs and consumer documentation only when the corrected contract changes. No new legacy lifecycle artifacts.

## Affected Capabilities

- Every default BDD runtime step obeys shared admission/executor/result policy on its one current protocol session.

## Non-Goals

- No protocol algorithm rewrite, additional mutation authority, blanket disabling of BDD to claim completion, private transport implementation or new live qualification.
- No unrelated changes, automatic publication or authority to execute this card from a planning request.

## Depends On

- `openspec/board/4.done/oss-fix-03-enforce-native-operation-admission.md`
- `openspec/board/4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md`
- `openspec/board/4.done/oss-fix-04b-isolate-testclient-transport-settings.md`
- `openspec/board/4.done/oss-fix-04c-isolate-workspace-and-ownership-roots.md`
- `openspec/board/2.todo/oss-fix-07-make-bound-window-reads-useful.md`
- `openspec/board/2.todo/oss-fix-08-bind-artifacts-at-trusted-production.md`

## Change Set

- `oss-fix-09-bind-default-bootstrap-and-reads`
- `oss-fix-09-bind-stateful-step-families`

## Design

The main acceptance path must be real MCP run_scenario with omitted single_session and real run_step, not an extra test-only tool. Preserve the current handle and cached-read semantics; use explicit operation adapters rather than reconstructing a new session per step. Inventory sessionless/provider-data steps as distinct policy classes. Aggregate sizing is provisional and exceeds one-card limits.

## Implementation Plan

1. Plan admission before session creation and shared single-session read/assert adapters with real default entrypoint tests.
2. Plan action/navigation/nested resolver integration, common result policy and bounded attachment handling while preserving existing useful step support.
3. Complete focused evidence after final Result/Log edits; the authorized outer runner owns independent review, final verification, done, commit and push.

## Delivery Budget

- primary_invariant: Every default BDD runtime step obeys shared admission/executor/result policy on its one current protocol session.
- expected_wall_minutes: 50
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 5
- estimated_production_loc: 500

## Budget Notes

SPLIT_REQUIRED remains the historical aggregate disposition. The original 50-minute/five-path/500-LOC estimate above is not a current executable budget. The three named successors have separate complete delivery estimates (85 expected minutes in total, including per-card checks); no number was lowered to admit the aggregate. Each successor still requires its own clean-fingerprint admission.

## Canonical Specs

- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-positive-operation-boundary-public-integration/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify

- `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py tests/test_mcp_server.py`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests`
- `./bin/openspec validate --specs --strict --no-interactive`

## Runtime And Authority

The planned implementation verifies a Python-side contract offline (runtime_contours=0), with synthetic files and fake sockets/backends; it does not claim native correctness. Release qualification is separately owned by `openspec/board/1.backlog/oss-fix-11-verify-corrected-linux-runtime.md` and `openspec/board/1.backlog/oss-fix-12-verify-corrected-windows-runtime.md`. No live TestClient, Windows deployment or mutation is authorized here.

## Related

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `docs/development/local-changerail-delivery.md`
- `docs/development/legacy-board-transition.md`

## Superseded By

- `openspec/board/1.backlog/oss-fix-09a-admit-default-bdd-session-and-reads.md`
- `openspec/board/1.backlog/oss-fix-09b-admit-stateful-and-nested-bdd-steps.md`
- `openspec/board/1.backlog/oss-fix-09c-control-session-independent-bdd-steps.md`

## Decomposition Coverage

| Required boundary | Owning successor |
| --- | --- |
| Pre-session admission, read/assert control and common result projection | [FIX-09A](oss-fix-09a-admit-default-bdd-session-and-reads.md) |
| Stateful/navigation execution, nested dispatch and cache correctness | [FIX-09B](oss-fix-09b-admit-stateful-and-nested-bdd-steps.md) |
| Local bookkeeping and explicitly admitted optional provider reads | [FIX-09C](oss-fix-09c-control-session-independent-bdd-steps.md) |

The first successor provides useful guarded reads and explicitly blocks every not-yet-integrated composed family. FIX-09B and FIX-09C remove only their own blocks using that same dispatcher/result policy; neither may restore a raw helper fallback. Provider capability absence remains explicitly blocked, while injected read-only providers retain a supported route. All three successors are required; the new step-result and provider seams explain the refreshed estimates.

## Result

SPLIT_REQUIRED aggregate decomposed into FIX-09A, FIX-09B and FIX-09C; implementation not started and finding R3 remains open. This retained aggregate must not be sent to FF/delivery or used as a done prerequisite.

## Next

- Review/admit the three named successor drafts individually, with their exact dependencies; do not run or move this aggregate as delivery.
- Close no part of the finding merely from planning or a partial successor. FIX-11/FIX-12 depend on all required successors, not this aggregate.
- Existing exhausted in-progress history and separate migration-pilot approval remain unchanged.

## Change 1: `oss-fix-09-bind-default-bootstrap-and-reads`

### Why

run_scenario defaults to single_session and run_step forces it, but run_single_session invokes handles/resolvers directly. A deny-all executor is never called and raw UI is returned under sanitized policy. Unify operation control without breaking one-bootstrap cursor ordering or useful BDD actions.

### Goal

Plan admission before session creation and shared single-session read/assert adapters with real default entrypoint tests.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- Card-level dependencies above.

### Ordered Tasks

1. Plan admission before session creation and shared single-session read/assert adapters with real default entrypoint tests.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py tests/test_mcp_server.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Change 2: `oss-fix-09-bind-stateful-step-families`

### Why

The first checkpoint alone does not prove the full card invariant; verify its required consumer/policy controls.

### Goal

Plan action/navigation/nested resolver integration, common result policy and bounded attachment handling while preserving existing useful step support.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- `oss-fix-09-bind-default-bootstrap-and-reads`.

### Ordered Tasks

1. Plan action/navigation/nested resolver integration, common result policy and bounded attachment handling while preserving existing useful step support.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py tests/test_mcp_server.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-05T08:11:47Z SPLIT_REQUIRED: a coherent complete implementation is provisionally 50 minutes and about 500 production LOC. Refine into disjoint default-session admission/read/assert control and stateful action/navigation/nested-step control. Any intermediate successor must explicitly block its unintegrated bound step families and cannot close R3 or the release gate until both are verified.
- 2026-09-05T08:38:59Z Operator-authorized decomposition created FIX-09A/B/C and reconciled downstream prerequisites; aggregate retained as non-executable history, with original estimates and no status move.
