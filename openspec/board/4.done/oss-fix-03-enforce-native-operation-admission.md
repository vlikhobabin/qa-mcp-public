# Enforce target admission for every bound native operation

## Status
4.done

## Owner
qa-mcp

## Series
oss-fix-03

## Order Index
406.22

## Lifecycle
openspec-v1

## OpenSpec Stage
native artifacts prepared; awaiting admission

## Priority
P1

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
Published-stage finding R2 (2026-09-05), reconfirmed on `289f432`: real bound
FastMCP click_command reaches a substituted native handler with no session or
attachment. Source-bound reproduction under `.runtime/qa-roadmap/oss-00/fix-03-planning/`
is optional local context; this card restates the clean-clone problem.

## Summary
Enforce explicit current-target route admission for every bound native operation,
independently of positive-result schema membership and before any side effect.

## Acceptance
- [C1] Bound native tools and shared native operations with missing, stale, foreign or malformed target/session/attachment/generation return fixed runtime-target-route-blocked before native handlers, endpoint probes, hidden display callbacks or protocol sends, preserving exact state. Include registered click_command outside the positive schema catalog.
- [C2] Every tool in both public profiles is explicitly classified as native-session-bound, lifecycle, provider-data or pure/readiness; cover direct/decorated routes. Unknown bound routes fail closed, and no schema-missing operation inherits permissive native execution.
- [C3] Exact admitted bound read, write and display consumers execute once with their current route and isolated application state. Pure/provider tools, valid lifecycle and explicit unbound compatibility retain useful behavior and their existing output/safety contracts.

## Scope
- `src/qa_mcp/mcp_server.py`, `src/qa_mcp/core/operations.py`, `src/qa_mcp/core/application.py`.
- Focused regression tests in `tests/test_target_bound_evidence_cleanup.py`, `tests/test_positive_operation_boundary_integration.py`, `tests/test_mcp_server.py`, related affected consumers and test support only as needed for these criteria.
- `docs/shared-core-extension.md`, `docs/qa-mcp-tool-reference.md` for corrected consumer policy; canonical spec through linked delta only.

## Non-Goals
No wire change, new mutation authority, observer, BDD executor refactor, tool
removal, live runtime, ChangeRail development or unrelated cleanup.

## Depends On
- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`
- `openspec/board/4.done/oss-fix-02-reject-unproven-project-attach.md`

## OpenSpec Changes
1. `oss-fix-03-enforce-native-operation-admission`

## Design
Implementation decisions and ordered tasks belong to the linked change.
Input-safety and external-effect evidence must assert pre/post identity and zero
refused callbacks, not just wrapper call ordering. C2 maps the complete registry;
C3 uses exact-route positive controls and isolated application state. No protocol
claim; native qualification is separately owned by FIX-11/FIX-12.

## Delivery Budget
- primary_invariant: Every bound native side effect requires a current admitted target/session route independently of result schemas.
- expected_wall_minutes: 60
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 280

## Budget Notes
Time/size estimates are advisory. One policy invariant and two ordered groups;
the shared maximum of two independent review cycles remains mandatory.

## Canonical Specs
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify
Use focused acceptance files first, then actual affected-module selection:
- `uv run pytest tests/test_target_bound_evidence_cleanup.py tests/test_positive_operation_boundary_integration.py tests/test_mcp_server.py --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-plan`
- `uv run pytest --qa-changed --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
Retain current source-bound C1-C3 observations/JUnit after final Result/Log edits.
No full suite or whole-project coverage floor is implied.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Registered and shared native route admission",
      "precondition": "Missing, stale, foreign or malformed target/session/attachment/generation, including no-schema click_command",
      "action": "Invoke real registered tools and shared operation entrypoints with external spies",
      "expected": "Fixed runtime-target-route-blocked before hidden display callbacks, endpoint probes or native effects; exact state unchanged",
      "method": {
        "kind": "test",
        "target": "tests/test_target_bound_evidence_cleanup.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Complete explicit operation classification",
      "precondition": "Both public profiles, direct/decorated and unknown bound routes",
      "action": "Assert full registry coverage and schema-independent admission behavior",
      "expected": "Every route explicitly classified; unknown native operations cannot fall through",
      "method": {
        "kind": "test",
        "target": "tests/test_positive_operation_boundary_integration.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Exact admitted route and compatibility",
      "precondition": "Current owned route or separately valid lifecycle/provider/pure/unbound inputs",
      "action": "Invoke representative read/write/display and independent/legacy real factory paths",
      "expected": "One execution with exact route identity and isolated state; supported policies and output contracts preserved",
      "method": {
        "kind": "test",
        "target": "tests/test_target_bound_evidence_cleanup.py"
      },
      "stage": "implementation"
    }
  ],
  "risks": [
    {
      "kinds": [
        "input_safety"
      ],
      "applies": true,
      "decision": "Validate route identity and fail closed independently of schemas.",
      "conditions": [
        "C1",
        "C2"
      ]
    },
    {
      "kinds": [
        "mutation",
        "external_effects"
      ],
      "applies": true,
      "decision": "Refuse before native/probe/display effects; assert unchanged state and exact positive routing with external fakes.",
      "conditions": [
        "C1",
        "C3"
      ]
    },
    {
      "kinds": [
        "concurrency"
      ],
      "applies": true,
      "decision": "Preserve per-application identity under separate and nested/concurrent registered calls.",
      "conditions": [
        "C1",
        "C3"
      ]
    },
    {
      "kinds": [
        "restart",
        "publication"
      ],
      "applies": false,
      "decision": "No persistence/process lifecycle or release changes; preserve existing lifecycle guards and runner publication ownership.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
Offline Python policy proof with fake native/process/display boundaries. No live
1C, Windows deployment, business mutation or native correctness claim. Runtime
qualification belongs to FIX-11/FIX-12. Operator OSS-00 mandate authorizes native
implementation/review and ordinary commit/push without repeated confirmation.

## Related
- `docs/development/oss-00-orchestration.md`
- `docs/development/test-policy.md`

## Result
Repair complete: bound admission now rejects stale/future session sequences and
malformed boundaries before callbacks; unknown bound extensions fail closed,
while an explicit shared-operation extension remains limited to the shared
admission path. Registered write/read/display controls retain exact routes,
including overlapping two-application calls. Evidence is offline with fake
external boundaries only; no live 1C, Windows, protocol or mutation claim.

## Next
- continue with the next dependency-ready epic card

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-10 Reconfirmed the defect through the real registered factory without sockets, replaced the old two-change draft with one native change and focused C1-C3 evidence, and selected delivery after published FIX-02 completion.
- 2026-09-10T20:02:40Z accepted native OpenSpec plan
- 2026-09-10T20:04:14Z started native OpenSpec delivery
- 2026-09-10T20:26:51Z change-2: added real registered admitted-write isolation and gate-sensitivity controls; corrected shared-core and tool-reference admission policy. Focused C1-C3: 321 passed in 59.11s. Changed offline: 1303 passed in 139.49s; integration: 1 passed in 3.25s. Changed-file compile, strict OpenSpec (70 specs), and diff check passed. Mocked boundaries prove pre/post identity, zero refused effects and exact positive routing; live/native qualification remains out of scope.
- 2026-09-10T21:00:41Z repair-01: fixed review findings R1-R4. Focused repaired acceptance: 329 passed in 61.26s; changed offline: 1311 passed in 140.57s; changed integration: 1 passed in 3.45s. Changed-file compile, strict OpenSpec (70 specs), and diff check passed. Fresh C1-C3 proof retains stale/future and malformed refusal, bound-extension callback zero-effect, explicit shared-operation/unbound compatibility, and overlapping registered two-application routing with fake boundaries only.
- 2026-09-10T21:11:28Z archive-refresh: archive movement invalidated retained payload receipts; refreshed the complete C1-C3 offline control set against the archived payload (46 passed in 5.62s). Fresh typed proof and aggregate handoff follow this retained observation; no product, canonical-spec, or archived-artifact edits were made.

## Delivery Receipt

- Independent review: `GO` at `2026-09-10T21:17:14Z`.
- Final repository verification: `passed` at `2026-09-10T21:20:10Z`; 5/5 configured commands succeeded.
- Deterministic done transition recorded at `2026-09-10T21:20:18Z` for publish.
