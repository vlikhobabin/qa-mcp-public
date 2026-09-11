# Preserve display failure verdicts through the operation boundary

## Status
4.done

## Owner
qa-mcp

## Series
oss-fix-06

## Order Index
406.25

## Lifecycle
openspec-v1

## OpenSpec Stage
native artifacts prepared; awaiting admission

## Priority
P2

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
Published-stage R5, reconfirmed through the real bound factory on `2405247`:
typed display exception becomes success/value={}, while ordinary failure and
empty/nonempty counts remain distinct. Optional local reproduction:
`.runtime/qa-roadmap/oss-00/fix-06-planning/reproduction.json`.

## Summary
Translate trusted window-list primitive failures before the operation boundary,
retaining successful data, privacy and deliberate direct legacy compatibility.

## Acceptance
- [C1] Real registered bound and unbound composed window-list calls through default local/Windows-host adapters preserve typed and ordinary backend failures as failure with existing fixed error vocabulary; no typed backend failure becomes success with empty value. Tests assert actual exception types and backend invocation.
- [C2] Real empty/nonempty inventories succeed with exact counts; arbitrary successful error-like dictionaries remain unchanged SUCCESS in generic HandlerQAExecutor, and explicit typed results retain their verdicts. No global dictionary heuristic is introduced.
- [C3] Serialized bound local/Windows-host failures omit hostile backend prose, secret fields, captions and paths while preserving fixed safe diagnostics; deliberate direct default-context calls retain typed legacy error dictionaries and valid inventory shape/count.

## Scope
- `src/qa_mcp/mcp_server.py`: trusted window-list handler and its default registration.
- `src/qa_mcp/core/executors.py`: existing generic compatibility seam only if necessary; no heuristic verdict inference.
- `tests/test_display_failure_verdicts.py`; directly affected display/shared-core/target-bound consumers when needed.
- `docs/qa-mcp-tool-reference.md`, `docs/shared-core-extension.md`; linked shared-core canonical delta.

## Non-Goals
No new error taxonomy, live display/1C/Windows invocation, transport change,
active-window DTO/assertion redesign, artifact trust redesign, general legacy
result refactor or ChangeRail development. FIX-07/FIX-08 retain their scope.

## Depends On
- none

## OpenSpec Changes
1. `oss-fix-06-preserve-display-failure-verdicts`

## Design
Implementation design lives in the linked change. Every typed C1-C3 selector
points to the actual focused module. Use real registered factories/default
executors and admitted bound target/session/attachment; replace only external
backend boundaries. Generic-dispatch controls are intentionally independent of
the trusted window-list producer. Record exact public outcomes and meaningful
source/assertion proof. A fixture TypeError is not the intended typed exception.

## Delivery Budget
- primary_invariant: A failed window-list primitive cannot become a successful operation while successful data and direct compatibility remain intact.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 2
- estimated_production_loc: 100

## Budget Notes
Estimates are advisory. One complete verdict partition is one native checkpoint;
ordinary shared allowance is two independent reviews across all continuations.

## Canonical Specs
- `openspec/specs/qa-mcp-shared-core-extension/spec.md`

## Verify
- `uv run pytest -v tests/test_display_failure_verdicts.py --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-plan`
- `uv run pytest -v --qa-changed --qa-lane offline --durations=10`
- `uv run pytest -v --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
Retain current typed C1-C3 source/terminal-node proof after final Result/Log and
semantic sync, refreshing again after archive. Serialize evidence writes. Finish
all condition proof and handoff; no full suite or native qualification implied.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Trusted window-list failure translation",
      "precondition": "Actual registered bound/unbound factories with default local and Windows-host executors; valid attachment for bound calls; fake display backend",
      "action": "Raise actual typed DisplayBackendError and ordinary RuntimeError; assert backend calls and composed outcomes",
      "expected": "Every backend failure remains failure with fixed existing code; typed exception never becomes success with empty value",
      "method": {
        "kind": "test",
        "target": "tests/test_display_failure_verdicts.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Successful inventory and generic-data partition",
      "precondition": "Real window-list producer plus independent real generic HandlerQAExecutor dispatch",
      "action": "Return zero and multiple windows; return arbitrary successful error-like dictionaries and explicit typed results from generic handlers",
      "expected": "Exact successful counts, generic SUCCESS value equality and typed verdict pass-through; old-adapter sensitivity fails",
      "method": {
        "kind": "test",
        "target": "tests/test_display_failure_verdicts.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Bound error privacy and deliberate legacy compatibility",
      "precondition": "Real admitted local/Windows-host contexts and distinct direct default-context legacy calls; hostile synthetic diagnostic fragments",
      "action": "Serialize typed/ordinary errors and successful inventories; inspect exact safe fields and direct legacy DTOs",
      "expected": "Bound diagnostics reveal no raw prose/secrets/captions/paths; direct typed error dict and success inventory/count remain compatible",
      "method": {
        "kind": "test",
        "target": "tests/test_display_failure_verdicts.py"
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
      "decision": "Hostile display diagnostic content must not cross the bound positive boundary; fixed code/message and raw-fragment absence.",
      "conditions": [
        "C1",
        "C3"
      ]
    },
    {
      "kinds": [
        "mutation",
        "external_effects"
      ],
      "applies": false,
      "decision": "Read-only synthetic window inventories; all external backend boundaries replaced, no live resources or file deletion.",
      "conditions": []
    },
    {
      "kinds": [
        "concurrency",
        "restart"
      ],
      "applies": false,
      "decision": "No new shared state/context lifecycle; use existing application-owned default adapters and current session admission.",
      "conditions": []
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "No release workflow change; ordinary authorized runner delivery.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
Hermetic fake backends/current target fixtures only, without live calls, business
effects or real display manipulation. FIX-11/FIX-12 retain native qualification.
The standing OSS-00 mandate authorizes implementation, review and ordinary push.

## Related
- `docs/development/oss-00-orchestration.md`
- `docs/development/test-policy.md`

## Result
Implemented trusted window-list failure translation and C1-C3 coverage. Focused
offline evidence, changed-module offline/integration checks, compile, strict
spec validation and diff checks pass. Delta requirements were semantically
synced into the canonical shared-core specification with a run-local mapping
report. Archive-refresh re-ran the C1-C3 selectors against the archived payload;
all three refreshed receipts pass.

## Next
- continue with the next dependency-ready epic card

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-11 Reconfirmed R5 through actual bound registered factory/default executor with typed/ordinary/empty/nonempty controls. Refreshed the old two-change/full-suite draft into one native change and coherent C1-C3 selectors; retained trusted producer translation and direct/generic compatibility scope.
- 2026-09-11T00:30:09Z accepted native OpenSpec plan
- 2026-09-11T00:31:34Z started native OpenSpec delivery
- 2026-09-11T00:40:08Z implemented producer-scoped OperationResult failure adapter; retained direct legacy helper behavior; added C1-C3 tests and consumer documentation.
- 2026-09-11T00:40:08Z focused evidence: c1 (5 passed), c2 (2 passed), c3 (1 passed); changed offline 950 passed, integration 1 passed, compile/spec/diff checks passed.
- 2026-09-11T00:46:53Z finalized semantic sync; added the three window-list verdict/privacy/compatibility requirements to `openspec/specs/qa-mcp-shared-core-extension/spec.md`; mapping retained in `.runtime/changerail/runs/20260911T003123Z-oss-fix-06-preserve-display-failure-verdicts/sync-report.md`.
- 2026-09-11T01:05:32Z archive-refresh re-ran C1 (5 passed), C2 (2 passed) and C3 (1 passed) with current archived payload fingerprint `sha256:9939a9509aa2e8c354446bb61dfae2a8e6a81e998a399eb850c8998ac2752e2e`.

## Delivery Receipt

- Independent review: `GO` at `2026-09-11T01:14:07.159454Z`.
- Final repository verification: `passed` at `2026-09-11T01:17:17Z`; 5/5 configured commands succeeded.
- Deterministic done transition recorded at `2026-09-11T01:17:25Z` for publish.
