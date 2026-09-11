# Control session-independent and provider-data BDD steps explicitly

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-09c

## Order Index

406.283

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

_run_sessionless_step runs before the guarded handle branch and can lazily construct an env-based ODataClient. skip/connect/performance markers and assert_data/assert_data_count currently lack a common explicit policy classification and can serialize raw data/errors.

## Acceptance

### Requirement: Classify local-only markers honestly

#### Scenario: Skip, connect marker and performance checks

- WHEN skip_step, connect_client or assert_step_perf is dispatched at top level or via the common nested dispatcher,
- THEN local bookkeeping does not invoke TestClient or a provider; connect_client cannot establish or replace an attachment, skip stays an explicit skip, and performance evaluates recorded durations through the same bounded public-result policy.

### Requirement: Admit optional provider reads without native fallback

#### Scenario: Denied, absent and injected data executor

- WHEN assert_data or assert_data_count is dispatched with a deny-all/unsupported executor or an explicitly injected read-only provider handler,
- THEN denied/unsupported calls create no ODataClient and make no HTTP call; the admitted handler alone reads and evaluates the assertion, and composed calls never silently construct an env-based provider or require one for ordinary native BDD.

### Requirement: Keep provider verdicts private and dispatch modes equivalent

#### Scenario: Provider outcomes, exceptions and mixed scenarios

- WHEN fake provider reads return success, assertion mismatch, blocked/ambiguous/failure or an exception through single-session, multi-session or nested dispatch,
- THEN normalized verdict/provenance and bounded assertion outcomes are preserved; report/log/attachment fields expose neither raw values/queries/endpoints nor credentials; native UI state/cache is unchanged and legacy explicitly uncomposed injected-provider behavior stays supported.

## Scope

- `src/qa_mcp/scenario/runner.py`
- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/core/boundary.py`
- Focused tests: `tests/test_scenario_runner.py`, `tests/test_scenario_actions.py`, `tests/test_shared_core_extension.py`, `tests/test_reporting.py`.
- Canonical specs and consumer documentation may be updated directly during authorized implementation; no new legacy lifecycle artifacts.

## Affected Capabilities

Session-independent BDD steps cannot bypass application operation policy or disclose provider data through reports.

## Non-Goals

No new provider package/API, change to OData URL/credential configuration, metadata integration, provider mutations, guarantee of zero bootstrap for an entire provider-only scenario, change to UI algorithms or loss of existing uncomposed injected-provider tests.

## Depends On

- `openspec/board/1.backlog/oss-fix-09a-admit-default-bdd-session-and-reads.md`

## Change Set

- `oss-fix-09c-classify-local-and-provider-steps`
- `oss-fix-09c-verify-provider-verdict-and-isolation`

## Design

Complete the finite step-family classifier established by FIX-09A: local bookkeeping, native operations, optional provider reads, and unsupported steps. Use the existing READ operation contract with explicit assert_data/count handlers and injected fake providers in tests; unsupported bound provider capability is a documented blocked result, not an env fallback. Keep local marker results policy-safe without pretending they are native observations. Reuse FIX-09A's normalized projection and FIX-09B's recursive dispatcher when delivered. The three cards do not depend cyclically: FIX-09B routes all descendants through the same dispatcher even while this card's families remain blocked.

## Coverage And Boundary

Owns the session-independent/provider classification noted in parent FIX-09 Design and completes its no-bypass/result requirements. R3 requires FIX-09A/B/C plus final Linux/Windows qualification; local-provider support alone is not native proof.

Production paths may overlap adjacent cards, but acceptance ownership does not. Deliver sequentially and consume predecessor contracts; do not reimplement their mechanisms. Recheck the named seams after prerequisites change the audited baseline.

## Implementation Plan

1. Replace composed sessionless bypass with the existing common classifier, restore safe local bookkeeping, and introduce explicit optional provider operation handlers without lazy env-based construction.
2. Use fake providers to verify zero-call denial, allowed value/count assertions, four verdicts, exception redaction and mixed/nested dispatch; preserve uncomposed compatibility without broadening composed authority.
3. Update governing canonical requirements/consumer limitations directly, finalize Result/Log and retain focused evidence. The authorized outer runner owns review, the final floor, done, commit and push.

## Delivery Budget

- primary_invariant: Session-independent BDD steps cannot bypass application operation policy or disclose provider data through reports.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 190

## Budget Notes

Provisional whole-card estimate, including focused tests and delivery checks; not a READY verdict or elapsed-time promise. Tests/docs are excluded from product-file/LOC counts. Reuse named predecessor seams; if the complete invariant exceeds the configured caps, return SPLIT_REQUIRED with the uncovered boundary rather than weakening acceptance or hiding work.

## Canonical Specs

- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-positive-operation-boundary-public-integration/spec.md`

## Verify

- `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_shared_core_extension.py tests/test_reporting.py`
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

## Change 1: `oss-fix-09c-classify-local-and-provider-steps`

### Why

_run_sessionless_step runs before the guarded handle branch and can lazily construct an env-based ODataClient. skip/connect/performance markers and assert_data/assert_data_count currently lack a common explicit policy classification and can serialize raw data/errors.

### Goal

Only explicitly allowed local or provider work can be dispatched.

### Scope

- The named product seams and tests for this checkpoint; no sibling acceptance is transferred here.

### Acceptance

- Only explicitly allowed local or provider work can be dispatched. The applicable complete card-level scenarios have desired-behavior regressions.

### Depends On

- Card-level prerequisites above.

### Ordered Tasks

1. Replace composed sessionless bypass with the existing common classifier, restore safe local bookkeeping, and introduce explicit optional provider operation handlers without lazy env-based construction.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_shared_core_extension.py tests/test_reporting.py` for the affected behavior; retain concise secret-safe evidence and reuse unchanged successful checks.

## Change 2: `oss-fix-09c-verify-provider-verdict-and-isolation`

### Why

The first checkpoint needs its corresponding consumer, isolation and result controls to establish the complete card invariant.

### Goal

All dispatch modes retain private-safe provider outcomes.

### Scope

- The named product seams and tests for this checkpoint; no sibling acceptance is transferred here.

### Acceptance

- All dispatch modes retain private-safe provider outcomes. The applicable complete card-level scenarios have desired-behavior regressions.

### Depends On

- `oss-fix-09c-classify-local-and-provider-steps`.

### Ordered Tasks

1. Use fake providers to verify zero-call denial, allowed value/count assertions, four verdicts, exception redaction and mixed/nested dispatch; preserve uncomposed compatibility without broadening composed authority.
2. Run `uv run pytest -q tests/test_scenario_runner.py tests/test_scenario_actions.py tests/test_shared_core_extension.py tests/test_reporting.py` for the affected behavior; retain concise secret-safe evidence and reuse unchanged successful checks.

## Log

- 2026-09-05T08:38:59Z Created by operator-authorized board-only decomposition of FIX-09; no admission, implementation, runtime, status move or publication.
