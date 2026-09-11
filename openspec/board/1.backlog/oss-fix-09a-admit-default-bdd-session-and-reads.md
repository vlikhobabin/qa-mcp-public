# Admit default BDD sessions and read/assert operations through the shared boundary

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-09a

## Order Index

406.281

## OpenSpec Stage

operator-refined successor draft; not admitted

## Priority

P1

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage review on 2026-09-05, finding R3, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- Operator-authorized decomposition of `openspec/board/1.backlog/oss-fix-09-unify-default-bdd-operation-boundary.md`. The symptom below is self-contained; ignored local audit reproductions are optional and their bug-confirming assertions must be inverted.

## Summary

run_scenario defaults to single_session and run_step forces it; run_single_session opens/bootstrap a socket and calls cached handle reads directly. A deny-all executor is skipped, while StepResult preview/error serialization can expose raw UI and collapses operation verdicts.

## Acceptance

### Requirement: Admit before native session acquisition

#### Scenario: Real default MCP calls with invalid state or denied bootstrap

- WHEN real factory run_scenario omits single_session, run_step is called, or ScenarioRunner is composed with missing/stale/foreign bound state or executor-denied session acquisition,
- THEN shared admission occurs before endpoint probing, sockets and bootstrap; denied acquisition makes zero native calls, and a denied read/assert never falls back to its handle or resolver.

### Requirement: Keep useful read/assert behavior on one trusted handle

#### Scenario: Cached presence, table and value assertions

- WHEN an admitted scenario runs supported active-window/form/value reads and presence/table/contains/equality assertions,
- THEN the selected executor controls each applicable operation, bootstrap occurs once, trusted cached reads do not advance the cursor twice, and assertions use FIX-07's internal data rather than sanitized preview; unsupported read_element/frame combinations are explicitly blocked, not advertised as newly supported.

### Requirement: Preserve policy in every BDD result channel and intermediate state

#### Scenario: Four verdicts and blocked not-yet-integrated families

- WHEN read outcomes cover success/blocked/ambiguous/failure or throw, and action/navigation/nested/provider/local-only families not yet integrated by FIX-09B/C are requested,
- THEN the same normalized operation verdict/provenance survives default and equivalent multi-session reports, logs and reporting inputs without raw UI, paths or exception fragments; unintegrated composed families are explicitly blocked before their helper runs; existing step status consumers retain compatibility.

## Scope

- `src/qa_mcp/scenario/runner.py`
- `src/qa_mcp/scenario/model.py`
- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/core/operations.py`
- `src/qa_mcp/core/boundary.py`
- Focused tests: `tests/test_scenario_runner.py`, `tests/test_positive_operation_boundary_integration.py`, `tests/test_shared_core_extension.py`, `tests/test_mcp_server.py`, `tests/test_reporting.py`.
- Canonical specs and consumer documentation may be updated directly during authorized implementation; no new legacy lifecycle artifacts.

## Affected Capabilities

Default BDD session acquisition and supported read/assert steps use shared admission, the selected executor and trusted result policy before native side effects.

## Non-Goals

No action/navigation/nested implementation (FIX-09B), local/provider-step implementation (FIX-09C), new read_element protocol support, OData configuration redesign, live UI activity or blanket disabling of useful BDD reads to claim R3 closed.

## Depends On

- `openspec/board/4.done/oss-fix-03-enforce-native-operation-admission.md`
- `openspec/board/4.done/oss-fix-04b-isolate-testclient-transport-settings.md`
- `openspec/board/4.done/oss-fix-04c-isolate-workspace-and-ownership-roots.md`
- `openspec/board/2.todo/oss-fix-07-make-bound-window-reads-useful.md`
- `openspec/board/2.todo/oss-fix-08-bind-artifacts-at-trusted-production.md`

## Change Set

- `oss-fix-09a-admit-session-and-read-handles`
- `oss-fix-09a-project-trusted-bdd-results`

## Design

Reuse FIX-03 admission and FIX-07/08 trusted read/evidence contracts. Move session acquisition into admitted execution and adapt local read handlers to the one current handle instead of rebuilding sessions. Keep a small internal handle/cache carrier, never a public arbitrary callback supplied by an executor. Add an optional normalized operation-result projection to StepResult if needed to preserve the four verdicts while retaining existing status/summary fields. Evaluate assertions against trusted internal data and normalize before _record_result/report serialization. Centralize the unintegrated-family block so nested or sessionless dispatch cannot bypass it. No generalized execution graph, raw-UI schema expansion or change to protocol algorithms.

## Coverage And Boundary

Owns parent FIX-09 requirement 1 and read/assert plus common result portions of requirements 2/3. It is a useful safe read-only intermediate, not R3 closure: FIX-09B and FIX-09C must remove only their own temporary blocks.

Production paths may overlap adjacent cards, but acceptance ownership does not. Deliver sequentially and consume predecessor contracts; do not reimplement their mechanisms. Recheck the named seams after prerequisites change the audited baseline.

## Implementation Plan

1. Write real default run_scenario/run_step negative controls and positive one-bootstrap read/assert cases; route acquisition and handle-backed reads through existing shared operations, with blocked unsupported families.
2. Reuse trusted assertions and artifact receipts, add the narrow StepResult projection, and test four verdicts, cache ordering, sanitized report/log/attachment channels and equivalent multi-session reads.
3. Update governing canonical requirements/consumer limitations directly, finalize Result/Log and retain focused evidence. The authorized outer runner owns review, the final floor, done, commit and push.

## Delivery Budget

- primary_invariant: Default BDD session acquisition and supported read/assert steps use shared admission, the selected executor and trusted result policy before native side effects.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 5
- estimated_production_loc: 290

## Budget Notes

Provisional whole-card estimate, including focused tests and delivery checks; not a READY verdict or elapsed-time promise. Tests/docs are excluded from product-file/LOC counts. Reuse named predecessor seams; if the complete invariant exceeds the configured caps, return SPLIT_REQUIRED with the uncovered boundary rather than weakening acceptance or hiding work.

## Canonical Specs

- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-positive-operation-boundary-public-integration/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify

- `uv run pytest -q tests/test_scenario_runner.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py tests/test_mcp_server.py tests/test_reporting.py`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests`
- `./bin/openspec validate --specs --strict --no-interactive`

## Runtime And Authority

This is a hermetic Python-side correction (runtime_contours=0), not native certification. Use fake sockets/HTTP/handles/providers and temporary files, with process signalling mocked. FIX-11 and FIX-12 own separately authorized final-source Linux/Windows qualification. Planning authorizes no implementation, live runtime, business mutation, commit or push; the migration pilot remains separately unapproved.

## Related

- `openspec/board/1.backlog/oss-fix-09-unify-default-bdd-operation-boundary.md`
- `docs/development/local-changerail-delivery.md`
- `docs/development/legacy-board-transition.md`

## Result

not started; decomposed backlog plan only. No review finding is closed.

## Next

- Review/admit this successor at a clean tracked fingerprint after its dependencies. It is not READY/todo merely because its estimates fit.
- Keep aggregate history and existing exhausted in-progress records intact; never clean unrelated work or infer pilot/publication authority.

## Change 1: `oss-fix-09a-admit-session-and-read-handles`

### Why

run_scenario defaults to single_session and run_step forces it; run_single_session opens/bootstrap a socket and calls cached handle reads directly. A deny-all executor is skipped, while StepResult preview/error serialization can expose raw UI and collapses operation verdicts.

### Goal

Admission/executor control precedes native session and read effects.

### Scope

- The named product seams and tests for this checkpoint; no sibling acceptance is transferred here.

### Acceptance

- Admission/executor control precedes native session and read effects. The applicable complete card-level scenarios have desired-behavior regressions.

### Depends On

- Card-level prerequisites above.

### Ordered Tasks

1. Write real default run_scenario/run_step negative controls and positive one-bootstrap read/assert cases; route acquisition and handle-backed reads through existing shared operations, with blocked unsupported families.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py tests/test_mcp_server.py tests/test_reporting.py` for the affected behavior; retain concise secret-safe evidence and reuse unchanged successful checks.

## Change 2: `oss-fix-09a-project-trusted-bdd-results`

### Why

The first checkpoint needs its corresponding consumer, isolation and result controls to establish the complete card invariant.

### Goal

Assertions stay useful and all outward channels preserve verdict/privacy.

### Scope

- The named product seams and tests for this checkpoint; no sibling acceptance is transferred here.

### Acceptance

- Assertions stay useful and all outward channels preserve verdict/privacy. The applicable complete card-level scenarios have desired-behavior regressions.

### Depends On

- `oss-fix-09a-admit-session-and-read-handles`.

### Ordered Tasks

1. Reuse trusted assertions and artifact receipts, add the narrow StepResult projection, and test four verdicts, cache ordering, sanitized report/log/attachment channels and equivalent multi-session reads.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py tests/test_mcp_server.py tests/test_reporting.py` for the affected behavior; retain concise secret-safe evidence and reuse unchanged successful checks.

## Log

- 2026-09-05T08:38:59Z Created by operator-authorized board-only decomposition of FIX-09; no admission, implementation, runtime, status move or publication.
