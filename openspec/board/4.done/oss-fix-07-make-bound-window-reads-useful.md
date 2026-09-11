# Make bound active-window reads useful without disclosing private UI

## Status
4.done

## Owner
qa-mcp

## Series
oss-fix-07

## Order Index
406.26

## Lifecycle
openspec-v1

## OpenSpec Stage
archived; independently verified under operator-authorized manual completion

## Priority
P2

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
Published-stage R6, reconfirmed on `79d0b92` using actual InitialUiContext and
ActiveWindowContext.to_result with the real default executor and ScenarioRunner:
success/value={} and both matching/mismatching expected windows fail. Baseline:
`.runtime/qa-roadmap/oss-00/fix-07-planning/reproduction.json` (optional local evidence).

## Summary
Expose useful bounded active-window observation, evaluate requested window
predicates before redaction and retain positive reconstruction/legacy behavior.

## Acceptance
- [C1] Actual ActiveWindowContext through real admitted local/Windows-host default factory paths exposes documented safe observed/missing/ambiguous state and exact marker_count, rather than unconditional success with empty value; malformed/unsuccessful native observations remain non-success.
- [C2] An explicitly requested actual observed-window predicate passes/mismatches against trusted internal refs/markers before public redaction; missing/ambiguous, metadata-only and public-envelope-only matches cannot pass. Real bound ScenarioRunner.run uses the admitted boolean with one native read and no fallback; operation and StepResult preview/error expose no raw UI/ref/expected-text/path/secret fragments, and request-local expectations do not leak.
- [C3] Production active-window schema remains finite and source-owned; malformed/oversized results preserve complete fixed type/size/provenance/receipt failures. Generic finite-class and forty public URL-cell protections remain covered separately from the product DTO, and deliberate unbound direct/multi-session compatibility stays useful.

## Scope
- `src/qa_mcp/core/boundary.py`, `src/qa_mcp/core/operations.py`, `src/qa_mcp/mcp_server.py`, `src/qa_mcp/scenario/runner.py`.
- `tests/test_bound_active_window_outcomes.py`; affected boundary/public-integration/scenario/shared-core tests and existing test-only helpers.
- `docs/qa-mcp-tool-reference.md`, `docs/shared-core-extension.md`; the three linked canonical deltas.

## Non-Goals
No native query/parser or wire/uniqueness qualification; no arbitrary UI strings,
form/element DTO redesign, generic artifact authority, new synthetic production
operation or dynamic schema injection. Default single-session BDD routing stays
in FIX-09A; live Linux/Windows in FIX-11/FIX-12. No ChangeRail work.

## Depends On
- `openspec/board/4.done/oss-fix-06-preserve-display-failure-verdicts.md`

## OpenSpec Changes
1. `oss-fix-07-make-bound-window-reads-useful`

## Design
The linked change defines concrete observation semantics and the private/public
predicate boundary. Every Cn uses the actual focused acceptance module. Real
InitialUiContext/ActiveWindowContext and default local/Windows-host executors are
mandatory product controls; a fake BaseContext with synthetic active fields is
not an oracle. Generic class tests use explicit separate fixtures/declared paths
without weakening actual production schema authority or prior negative controls.

## Delivery Budget
- primary_invariant: Bound active-window observations and assertions are useful while raw UI stays private and positive reconstruction remains intact.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 4
- estimated_production_loc: 280

## Budget Notes
Timing/size are advisory. One coherent native change/checkpoint covers the real
DTO, predicate and public reconstruction partition; two ordinary independent
reviews cover the run and continuations without reset.

## Canonical Specs
- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-positive-core-operation-boundary/spec.md`
- `openspec/specs/qa-mcp-positive-operation-boundary-public-integration/spec.md`

## Verify
- `uv run pytest -v tests/test_bound_active_window_outcomes.py --qa-lane offline --durations=10`
- `uv run pytest -v tests/test_positive_core_operation_boundary.py tests/test_positive_operation_boundary_integration.py tests/test_scenario_runner.py --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-plan`
- `uv run pytest -v --qa-changed --qa-lane offline --durations=10`
- `uv run pytest -v --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
Retain source/assertion fragments and verbose terminal nodes/JUnit after actual
UTC Result/Log and sync. Command receipts AND current registered typed C1-C3
records are required for handoff; archive refresh binds the new payload and
continues the same reviewer. Serialize evidence writes. No full suite implied.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Actual active-window observation",
      "precondition": "Actual InitialUiContext and ActiveWindowContext; real admitted factories/default local and Windows-host executors/current attachment; synthetic session",
      "action": "Invoke shared registered MCP operation and ScenarioRunner.run for observed/missing/ambiguous DTO combinations; assert actual call count and arguments",
      "expected": "Documented safe state and exact marker count replace success with empty value; malformed/unsuccessful data is non-success",
      "method": {
        "kind": "test",
        "target": "tests/test_bound_active_window_outcomes.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Predicate before public redaction",
      "precondition": "Actual private window reference/markers and explicit expected predicate; real default handler/ScenarioRunner.run",
      "action": "Exercise actual match, mismatch, missing/ambiguous and metadata/public-envelope-only matches; serialize operation and StepResult",
      "expected": "Only actual observed-window match passes, expected text and private UI/paths/secrets remain absent, no duplicate native read or fallback",
      "method": {
        "kind": "test",
        "target": "tests/test_bound_active_window_outcomes.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Positive reconstruction and compatibility",
      "precondition": "Production fixed schema plus retained finite-class/public error-details controls; real unbound compatibility and hostile bound outcomes",
      "action": "Run malformed types/subclasses/literals/counts, oversized result, provenance/receipt controls and generic class/public URL regression matrices",
      "expected": "Complete existing fixed failures/bounds retained, no partial or arbitrary fields, synthetic class fixtures separated, unbound legacy reads remain useful",
      "method": {
        "kind": "test",
        "target": "tests/test_bound_active_window_outcomes.py"
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
      "decision": "Expected/read data remain private and cannot alter schema/provenance; exact classes and fixed outcomes with malicious/oversized controls.",
      "conditions": [
        "C1",
        "C2",
        "C3"
      ]
    },
    {
      "kinds": [
        "concurrency"
      ],
      "applies": true,
      "decision": "Any private expectation carrier is request-local; independent expectations cannot leak and success/failure restores caller state. No shared cache introduced.",
      "conditions": [
        "C2"
      ]
    },
    {
      "kinds": [
        "restart"
      ],
      "applies": false,
      "decision": "No persisted state or resumable session changes; single-session routing remains FIX-09A.",
      "conditions": []
    },
    {
      "kinds": [
        "mutation",
        "external_effects"
      ],
      "applies": false,
      "decision": "Read-only pure Python correction with synthetic sessions/temporary fixtures; no live sockets, UI actions or cleanup effects.",
      "conditions": []
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "No release workflow change; ordinary runner-owned publication.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
Hermetic Python fixtures and substituted native session only; no real socket,
TestClient, UI effect or native certification. Existing OSS-00 mandate authorizes
implementation, review, commit and ordinary push. Qualification remains separate.

## Related
- `docs/development/oss-00-orchestration.md`
- `docs/development/test-policy.md`

## Result
2026-09-11T03:06:37.353677+00:00: FIX-07 implemented and independently accepted under the operator-authorized manual completion. Safe observed/missing/ambiguous window outcomes and private predicates work through real default local/Windows-host factories and shared MCP/ScenarioRunner; exact reconstruction/refusal, provenance/receipt and deliberate unbound behavior are retained. Prearchive checks: 637 focused, 1435 affected offline and one integration, compile/70 strict specs/diff passed. Independent review cycle 2 is GO; the interrupted unvalidated native review is counted as cycle 1. Stock archive preserves product/tests/docs/canonical bytes. Current final verification and ordinary publication use the separate `.runtime/qa-roadmap/oss-00/fix-07-manual-completion/` ledger; stopped native runs remain unchanged. No native success or live qualification is claimed.

## Next
FIX-07 is complete under the retained manual exception. Continue OSS-00 from clean published main with FIX-08; preserve all stopped native attempts and final manual evidence.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-11 Reconfirmed actual DTO success/value={} and matching window assertion false through the published default executor/ScenarioRunner. Refreshed two historical changes into one native observation/predicate/positive-boundary change with real fixtures, explicit compatibility and coherent typed selectors; no full-suite per-card requirement.
- 2026-09-11T01:24:31Z accepted native OpenSpec plan
- 2026-09-11T01:26:03Z started native OpenSpec delivery
- 2026-09-11T01:53:26Z completed implementation checkpoint 1: focused C1-C3, affected offline/integration, compile, strict specs and diff checks passed; registered shared MCP/default local+Windows-host proof, malformed/oversized and legacy redaction sensitivity controls retained.
- 2026-09-11T02:28:24Z manual completion repair: removed custom positive executor/default-handler and module-wide schema/projection bypasses; added real factory controls, unbound compatibility and retained old-projection negative control. Focused offline: 61 tests (C1-C3 + scenario), 408 core, 116 public integration; all passed. Integration lane: no selected tests (exit 5). Compile/spec/diff passed; logs/JUnit retained under `.runtime/qa-roadmap/oss-00/fix-07-manual-completion/repair/`.
- 2026-09-11T02:35:25Z final focused rerun after default-handler repair: C1-C3 22/22 and affected offline 563/563 passed; compile and diff-check passed. Strict specs remained 70/70. Integration lane retained 0 selected (exit 5).

- 2026-09-11T02:44:51.493258+00:00 Supervisor completed missing C1-C3 controls after the manual worker: restored exact public refusal oracles, covered both policies and actual factory paths, invalid expectations, failure/recovery, schema classes, current/foreign/stale receipts and unbound direct compatibility. Retained failing controls reproduced public-preview false positives and raw mapping size bypass; fixed both in accepted product seams. Earlier implementation/evidence completeness claims are superseded by current source-bound checks. One interrupted native review session is counted as used; one independent review remains, without reset.

- 2026-09-11T02:50:19.237448+00:00 Final C3 check reproduced a third projection gap: SUCCESS carrying error was rebuilt as success. Corrected malformed-result validation and exact invalid-executor-result/result-too-large taxonomy before normalization; native status/adapter failures retain executor-failure. Current targeted regressions: 189 passed (73 focused acceptance plus 116 public boundary cases). The earlier broad pre-review attempt was interrupted after 591 passes to apply this correction, not recorded as a completed verification. Current complete verification follows this final Result/Log edit.

- 2026-09-11T02:55:58.836788+00:00 Complete candidate checks passed (636 focused, 1434 affected offline, one integration, compile/70 strict specs/diff). A final malformed-key control then reproduced a callback regression at raw status lookup; added exact-string-key validation before any lookup. The before/after control is retained in supervisor-key-before.log/supervisor-key-after.log. Current complete checks are refreshed after this final in-scope correction; no additional independent review was created.

- 2026-09-11T03:06:37.354697+00:00 Independent manual review cycle 2 returned GO; cycle 1 remains the preserved interrupted native session, with no accepted native verdict. Stock archive moved the seven exact accepted artifacts to `openspec/changes/archive/2026-09-11-oss-fix-07-make-bound-window-reads-useful` with --skip-specs; product/test/docs/canonical bytes unchanged. Final current checks follow this Result/Log update.
