# Admit stateful and nested BDD steps on the existing session

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-09b

## Order Index

406.282

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

_run_step_on_handle invokes navigate_resolver and action_resolver/handle.run_action directly; _run_subscenario dispatches children through raw handle/sessionless helpers. A policy-controlled read path alone therefore leaves stateful and nested bypasses.

## Acceptance

### Requirement: Control every stateful resolver before invocation

#### Scenario: Denied navigation or replay action

- WHEN a bound scenario requests navigation/open, capture-backed action or close/select/input behavior and the selected executor denies or lacks that operation,
- THEN neither resolver, run_action nor fallback executes; admitted existing operations execute once on the same handle, and mutations still require their existing authority rather than being reclassified as reads.

### Requirement: Keep nested dispatch inside the same operation policy

#### Scenario: Nested actions, cycles and unsupported descendants

- WHEN nested scenarios contain allowed or denied children, unknown names or cycles,
- THEN each child passes the same dispatcher as top-level steps, denied children perform no side effect, cycle/unknown cases return bounded errors, and descendants cannot call raw sessionless helpers; root bootstrap remains single and operation verdicts are retained in a bounded policy-safe aggregate.

### Requirement: Preserve stateful behavior, cursor and evidence correctness

#### Scenario: Read-action-read and navigation failure controls

- WHEN admitted actions/navigation change UI state or are rejected, followed by read/assert work or another nested call,
- THEN cache state is invalidated or renewed only according to supported cursor semantics; stale data cannot make an assertion pass, required unsupported re-reads are explicit failures, and FIX-09A result policy preserves four verdicts/provenance and only FIX-08-admitted artifacts.

## Scope

- `src/qa_mcp/scenario/runner.py`
- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/core/boundary.py`
- Focused tests: `tests/test_scenario_runner.py`, `tests/test_scenario_actions.py`, `tests/test_positive_operation_boundary_integration.py`, `tests/test_shared_core_extension.py`.
- Canonical specs and consumer documentation may be updated directly during authorized implementation; no new legacy lifecycle artifacts.

## Affected Capabilities

Every stateful step, including one reached through a nested scenario, executes only through the selected executor on the already admitted BDD handle.

## Non-Goals

No new mutation authority, action corpus/replay algorithm changes, full support for previously unsupported actions, provider-data implementation (FIX-09C), new report renderer or native qualification.

## Depends On

- `openspec/board/1.backlog/oss-fix-09a-admit-default-bdd-session-and-reads.md`
- `openspec/board/4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md`

## Change Set

- `oss-fix-09b-admit-stateful-adapters`
- `oss-fix-09b-gate-nested-dispatch-and-cache`

## Design

Extend FIX-09A's dispatcher and its existing default-executor registrations with explicit stateful operation adapters. Keep replay and navigation algorithms in their existing resolvers, invoked only by the selected adapter. Route every nested child back through the same dispatcher and common normalized result projection; do not mint a new target/session or flatten blocked/ambiguous into success. Invalidate only affected cache entries and respect existing linear-cursor limits. Session-independent/provider descendants use FIX-09C when available, otherwise the FIX-09A block remains. No new nested execution engine or protocol schema catch-all.

## Coverage And Boundary

Owns stateful/navigation/nested portions of parent FIX-09 requirements 2/3. FIX-09C is still required for session-independent/provider dispatch; neither completed nested read nor action support alone closes R3.

Production paths may overlap adjacent cards, but acceptance ownership does not. Deliver sequentially and consume predecessor contracts; do not reimplement their mechanisms. Recheck the named seams after prerequisites change the audited baseline.

## Implementation Plan

1. Add selected-executor deny/allow tests through real default scenario calls, then register narrow navigation/replay adapters that reuse the admitted handle and normalized result path.
2. Route descendants through the common classifier, cover cycle/unknown/blocked children and read-action-read cache behavior, and retain bounded four-verdict aggregates without raw UI or path leakage.
3. Update governing canonical requirements/consumer limitations directly, finalize Result/Log and retain focused evidence. The authorized outer runner owns review, the final floor, done, commit and push.

## Delivery Budget

- primary_invariant: Every stateful step, including one reached through a nested scenario, executes only through the selected executor on the already admitted BDD handle.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 260

## Budget Notes

Provisional whole-card estimate, including focused tests and delivery checks; not a READY verdict or elapsed-time promise. Tests/docs are excluded from product-file/LOC counts. Reuse named predecessor seams; if the complete invariant exceeds the configured caps, return SPLIT_REQUIRED with the uncovered boundary rather than weakening acceptance or hiding work.

## Canonical Specs

- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-positive-operation-boundary-public-integration/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify

- `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py`
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

## Change 1: `oss-fix-09b-admit-stateful-adapters`

### Why

_run_step_on_handle invokes navigate_resolver and action_resolver/handle.run_action directly; _run_subscenario dispatches children through raw handle/sessionless helpers. A policy-controlled read path alone therefore leaves stateful and nested bypasses.

### Goal

Allowed stateful calls run once and denied calls reach no resolver.

### Scope

- The named product seams and tests for this checkpoint; no sibling acceptance is transferred here.

### Acceptance

- Allowed stateful calls run once and denied calls reach no resolver. The applicable complete card-level scenarios have desired-behavior regressions.

### Depends On

- Card-level prerequisites above.

### Ordered Tasks

1. Add selected-executor deny/allow tests through real default scenario calls, then register narrow navigation/replay adapters that reuse the admitted handle and normalized result path.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py` for the affected behavior; retain concise secret-safe evidence and reuse unchanged successful checks.

## Change 2: `oss-fix-09b-gate-nested-dispatch-and-cache`

### Why

The first checkpoint needs its corresponding consumer, isolation and result controls to establish the complete card invariant.

### Goal

Nested calls cannot bypass the dispatcher or assert against stale state.

### Scope

- The named product seams and tests for this checkpoint; no sibling acceptance is transferred here.

### Acceptance

- Nested calls cannot bypass the dispatcher or assert against stale state. The applicable complete card-level scenarios have desired-behavior regressions.

### Depends On

- `oss-fix-09b-admit-stateful-adapters`.

### Ordered Tasks

1. Route descendants through the common classifier, cover cycle/unknown/blocked children and read-action-read cache behavior, and retain bounded four-verdict aggregates without raw UI or path leakage.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_positive_operation_boundary_integration.py tests/test_shared_core_extension.py` for the affected behavior; retain concise secret-safe evidence and reuse unchanged successful checks.

## Log

- 2026-09-05T08:38:59Z Created by operator-authorized board-only decomposition of FIX-09; no admission, implementation, runtime, status move or publication.
