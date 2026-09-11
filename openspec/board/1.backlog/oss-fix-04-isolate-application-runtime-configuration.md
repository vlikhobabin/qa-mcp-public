# Isolate runtime configuration for separately composed applications

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-04

## Order Index

406.23

## OpenSpec Stage

superseded SPLIT_REQUIRED aggregate; planning history only; not a runner input

## Priority

P1

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage code review, 2026-09-05, finding R4, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- The symptom and required regression are restated here; ignored local review files are optional context, not clean-clone prerequisites. Original reproduction tests asserted the bug and must be inverted into desired-behavior regressions.

## Summary

Factory Settings select an executor name, while display/relay and workspace helpers still consult process environment. A remote-configured application can select local-xtest, and multiple applications can share the wrong transport/evidence configuration. Resolve this as an application-isolation invariant, not just a backend-name patch.

This aggregate was decomposed at operator request. Its original Scope, Implementation Plan and Change checkpoints are retained as design history, not an execution plan. Use all named successors below; aggregate creation/decomposition closes no finding.

## Acceptance

### Requirement: Honor explicit display settings

#### Scenario: Correction 04 control 1

- WHEN two applications have different local/remote mode and host-agent settings while process environment disagrees, THEN each display/lifecycle client uses only its own address, credentials, port and compatibility policy without contacting any real host in offline tests.

### Requirement: Isolate protocol and retention settings

#### Scenario: Correction 04 control 2

- WHEN applications use different relay configurations and workspace/ownership roots, THEN protocol prefaces, route probes and output/cleanup paths remain application-specific; concurrent calls and env changes cannot cross-contaminate them.

### Requirement: Preserve legacy and target contracts

#### Scenario: Correction 04 control 3

- WHEN a legacy direct entrypoint is intentionally used, THEN its documented env behavior remains explicit; composed calls retain target admission and do not expose secret configuration.

## Scope

- `src/qa_mcp/core/application.py`
- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/protocol/display_backend.py`
- `src/qa_mcp/protocol/transport.py`
- `src/qa_mcp/protocol/session.py`
- `src/qa_mcp/protocol/lifecycle.py`
- Focused regression tests: `tests/test_shared_core_extension.py`, `tests/test_display_backend.py`, `tests/test_protocol_session.py`, `tests/test_lifecycle.py`.
- Direct updates to the governing canonical specs and consumer documentation only when the corrected contract changes. No new legacy lifecycle artifacts.

## Affected Capabilities

- A composed application's display, protocol route and evidence ownership configuration never comes from another application or later process-env drift.

## Non-Goals

- No private Runtime Proxy implementation, wire protocol changes, Windows bridge rewrite or general cleanup of unrelated global constants.
- No unrelated changes, automatic publication or authority to execute this card from a planning request.

## Depends On

- none

## Change Set

- `oss-fix-04-isolate-display-dependencies`
- `oss-fix-04-isolate-protocol-and-retention`

## Design

Prefer explicit provider-neutral dependencies composed once from existing Settings. Examine all active callers, including TestClientSession and native write transports, before choosing an injected connector or scoped immutable transport configuration. Do not mutate os.environ or add product-specific globals. The estimate exceeds admission: it must not become one executable card by lowering the numbers.

## Implementation Plan

1. Plan and test two real factory instances with conflicting process env; select a per-application display/lifecycle client dependency.
2. Inventory connector and ownership/evidence consumers; propagate the same application-specific settings through real protocol entrypoints and cleanup, with concurrency controls.
3. Complete focused evidence after final Result/Log edits; the authorized outer runner owns independent review, final verification, done, commit and push.

## Delivery Budget

- primary_invariant: A composed application's display, protocol route and evidence ownership configuration never comes from another application or later process-env drift.
- expected_wall_minutes: 40
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 6
- estimated_production_loc: 400

## Budget Notes

SPLIT_REQUIRED remains the historical aggregate disposition. The original 40-minute/six-path/400-LOC estimate above is not a current executable budget. The three named successors have separate complete delivery estimates (75 expected minutes in total, including per-card checks); no number was lowered to admit the aggregate. Each successor still requires its own clean-fingerprint admission.

## Canonical Specs

- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-runtime-configuration/spec.md`
- `openspec/specs/qa-mcp-standalone-host-bridge/spec.md`

## Verify

- `uv run pytest -q tests/test_shared_core_extension.py tests/test_display_backend.py tests/test_protocol_session.py tests/test_lifecycle.py`
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

- `openspec/board/4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md`
- `openspec/board/4.done/oss-fix-04b-isolate-testclient-transport-settings.md`
- `openspec/board/4.done/oss-fix-04c-isolate-workspace-and-ownership-roots.md`

## Decomposition Coverage

| Required boundary | Owning successor |
| --- | --- |
| Display/lifecycle settings and client targeting | [FIX-04A](oss-fix-04a-isolate-display-and-host-agent-settings.md) |
| Native socket/relay settings and non-consuming probes | [FIX-04B](oss-fix-04b-isolate-testclient-transport-settings.md) |
| Workspace/output roots and owned marker creation/cleanup | [FIX-04C](oss-fix-04c-isolate-workspace-and-ownership-roots.md) |

Retention is independent from transport: a correct relay route does not prove that marker lookup or cleanup uses the owning root. FIX-04B owns the minimal application Settings scope; FIX-04C reuses it. Common compatibility/confidentiality controls stay with each affected consumer.

## Result

SPLIT_REQUIRED aggregate decomposed into FIX-04A, FIX-04B and FIX-04C; implementation not started and finding R4 remains open. This retained aggregate must not be sent to FF/delivery or used as a done prerequisite.

## Next

- Review/admit the three named successor drafts individually, with their exact dependencies; do not run or move this aggregate as delivery.
- Close no part of the finding merely from planning or a partial successor. FIX-11/FIX-12 depend on all required successors, not this aggregate.
- Existing exhausted in-progress history and separate migration-pilot approval remain unchanged.

## Change 1: `oss-fix-04-isolate-display-dependencies`

### Why

Factory Settings select an executor name, while display/relay and workspace helpers still consult process environment. A remote-configured application can select local-xtest, and multiple applications can share the wrong transport/evidence configuration. Resolve this as an application-isolation invariant, not just a backend-name patch.

### Goal

Plan and test two real factory instances with conflicting process env; select a per-application display/lifecycle client dependency.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- Card-level dependencies above.

### Ordered Tasks

1. Plan and test two real factory instances with conflicting process env; select a per-application display/lifecycle client dependency.
2. Run `uv run pytest -q tests/test_shared_core_extension.py tests/test_display_backend.py tests/test_protocol_session.py tests/test_lifecycle.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Change 2: `oss-fix-04-isolate-protocol-and-retention`

### Why

The first checkpoint alone does not prove the full card invariant; verify its required consumer/policy controls.

### Goal

Inventory connector and ownership/evidence consumers; propagate the same application-specific settings through real protocol entrypoints and cleanup, with concurrency controls.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- `oss-fix-04-isolate-display-dependencies`.

### Ordered Tasks

1. Inventory connector and ownership/evidence consumers; propagate the same application-specific settings through real protocol entrypoints and cleanup, with concurrency controls.
2. Run `uv run pytest -q tests/test_shared_core_extension.py tests/test_display_backend.py tests/test_protocol_session.py tests/test_lifecycle.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-05T08:11:47Z SPLIT_REQUIRED: the provisional aggregate is 40 minutes, six product paths and about 400 production LOC. Refine into independently useful application-owned display/lifecycle routing and application-owned protocol/retention routing; confirm whether retention needs its own invariant before creating successors. Do not treat the two provisional checkpoints as an accepted delivery.
- 2026-09-05T08:38:59Z Operator-authorized decomposition created FIX-04A/B/C and reconciled downstream prerequisites; aggregate retained as non-executable history, with original estimates and no status move.
