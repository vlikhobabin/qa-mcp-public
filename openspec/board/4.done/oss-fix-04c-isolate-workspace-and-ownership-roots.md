# Keep workspace output and process-ownership records inside their owning application

## Status
4.done

## Owner
qa-mcp

## Series
oss-fix-04c

## Order Index
406.233

## Lifecycle
openspec-v1

## OpenSpec Stage
archived; independently verified under operator-authorized manual completion

## Priority
P1

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
Published-stage R4 and operator decomposition of FIX-04. On `1046b9f`, actual
factory callbacks with A/B/explicit-empty Settings still resolve a third process
workspace and ownership root. Retained local diagnostic is optional context:
`.runtime/qa-roadmap/oss-00/fix-04c-planning/reproduction.json`.

## Summary
Composed applications must create, locate and clean their workspace outputs and
ownership markers according to their own configured roots. Correct the full
creation/discovery family using the existing Settings scope from FIX-04B.

## Acceptance
- [C1] Real factories with distinct home/ownership settings and a conflicting process root use their intended capture/template/default-output roots; no output appears under another application's root. Separately admitted binding.evidence_root and retention policy retain their authority and never fall back to workspace.
- [C2] Fake owned launches create real markers that subsequent stop/cleanup discovers in the same owning root after env drift. Explicit ownership-root precedence and workspace fallback both work; foreign markers/processes are preserved and PID/start/group, target/session and unowned-process refusal remain intact.
- [C3] Explicit roots, authoritative empty Settings, documented fallback and intentionally unbound direct env calls retain deterministic precedence. Nested inner failure restores the caller's exact paired application/root scope. Bound sanitized results expose no raw root paths and existing unbound output/retention behavior remains compatible with the separate FIX-05 scope.

## Scope
- `src/qa_mcp/mcp_server.py`, `src/qa_mcp/protocol/lifecycle.py`; consume the existing config accessor.
- `tests/test_shared_core_extension.py`, `tests/test_lifecycle.py`, `tests/test_target_bound_evidence_cleanup.py` and directly affected consumers/support needed for these criteria.
- `docs/shared-core-extension.md`, `docs/qa-mcp-tool-reference.md` for precedence/limitations; canonical requirements through the linked delta only.

## Non-Goals
No socket/display policy change, retention TTL/artifact receipt redesign, old
runtime-directory migration, real process/file cleanup, target reinterpretation,
new observer, live operation or ChangeRail development.

## Depends On
- `openspec/board/4.done/oss-fix-04b-isolate-testclient-transport-settings.md`

## OpenSpec Changes
1. `oss-fix-04c-isolate-workspace-and-ownership-roots`

## Design
Implementation design and ordered tasks belong to the linked change. Evidence
must trace marker production through later successful same-owner discovery and
cleanup; resolver-only checks cannot prove C2. Use complete application/root
pairs and before/after inventories. C1/C3 preserve separately admitted evidence
policy and explicit legacy behavior; no new protocol claim is made.

## Coverage And Boundary
Owns the filesystem portion of superseded FIX-04. FIX-04B supplies scope; current
FIX-03 admission is preserved. Production paths overlap later corrections, whose
separate acceptance (especially FIX-05 retention and FIX-08 artifacts) stays open.

## Delivery Budget
- primary_invariant: A composed application resolves, retains and cleans outputs and ownership records only in its own configured roots under existing bound policy.
- expected_wall_minutes: 45
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 2
- estimated_production_loc: 150

## Budget Notes
Estimates are advisory. One cohesive root-placement/lookup invariant is one native
change and checkpoint; the shared two-independent-review allowance remains.

## Canonical Specs
- `openspec/specs/qa-mcp-runtime-configuration/spec.md`

## Verify
- `uv run pytest -v tests/test_shared_core_extension.py tests/test_lifecycle.py tests/test_target_bound_evidence_cleanup.py --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-plan`
- `uv run pytest -v --qa-changed --qa-lane offline --durations=10`
- `uv run pytest -v --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
Retain current source-bound verbose node/JUnit evidence and typed C1-C3 proof
AFTER final Result/Log and semantic sync edits, and refresh after archive.
Missing/stale proof is authorized finalization work to complete before handoff.
No full suite or whole-project coverage floor is implied.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Factory workspace and admitted evidence consumers",
      "precondition": "Distinct A/B workspace roots, bound evidence authority and process root C",
      "action": "Invoke real capture/output consumers with temporary files and fake native/display boundaries",
      "expected": "Exact owning workspace/output paths and bound evidence authority; no foreign-root outputs",
      "method": {
        "kind": "test",
        "target": "tests/test_shared_core_extension.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Owned marker creation through cleanup discovery",
      "precondition": "Explicit ownership root or workspace fallback, env drift, foreign markers and fake PID/start/group controls",
      "action": "Create markers through fake owned launches then invoke real discovery and cleanup policy",
      "expected": "Same-owner marker found and cleaned; foreign markers/processes and invalid identity remain untouched",
      "method": {
        "kind": "test",
        "target": "tests/test_lifecycle.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Root precedence, privacy and context lifetime",
      "precondition": "Explicit/empty settings, intentionally unbound direct calls and nested inner failure",
      "action": "Resolve actual consumers before/during/after nested calls and inspect sanitized public results",
      "expected": "Deterministic precedence, paired owning roots/context restored, no raw roots in bound sanitized output, legacy paths remain useful",
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
      "decision": "Explicit scope and empty settings must not inherit ambient filesystem roots; keep bound evidence policy authoritative.",
      "conditions": [
        "C1",
        "C3"
      ]
    },
    {
      "kinds": [
        "mutation",
        "external_effects",
        "restart"
      ],
      "applies": true,
      "decision": "Real marker serialization/discovery across calls with fake processes/signals; preserve foreign resources and PID/start/group/ownership refusal.",
      "conditions": [
        "C2"
      ]
    },
    {
      "kinds": [
        "concurrency"
      ],
      "applies": true,
      "decision": "Nested exceptional exits preserve exact root/application pairs and restore caller scope; no process env mutation.",
      "conditions": [
        "C3"
      ]
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "No release workflow change; ordinary delivery remains runner-owned.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
Hermetic Python proof with temporary directories and fake native/process/display
boundaries. Signal/create/cleanup only fake or run-owned fixture resources; no
real TestClient, Windows deployment, business mutation or native correctness
claim. Final native qualification remains FIX-11/FIX-12. Operator OSS-00 mandate
authorizes implementation, independent review and ordinary commit/push.

## Related
- `openspec/board/1.backlog/oss-fix-04-isolate-application-runtime-configuration.md`
- `docs/development/oss-00-orchestration.md`
- `docs/development/test-policy.md`

## Result
C1–C3 and all six delta scenarios accepted by independent review: two native
NO-GOs are preserved, and one separately accounted manual exception review
(total cycle 3) is GO with no findings. Root isolation, both local factory
launch paths, capture/template/default-output consumers and same-task context
restoration are proven. Every individual cleanup now preserves complete foreign
marker/sentinel/process inventories; refusals preserve all bytes/resources and
signals. A current-tmp-path-only cross-owner mutation fails the new assertion.

Current prearchive proof passed 127 acceptance offline and two integration
cases, compile, 70 strict specs and diff checks. Stock OpenSpec archive preserves
the exact reviewed artifacts and canonical/product bytes. Final affected checks,
same-reviewer postarchive confirmation and ordinary publication are retained as
they complete under `.runtime/qa-roadmap/oss-00/fix-04c-manual-completion/`.
The operator-authorized manual exception preserves all 199 native run files and
both NO-GOs; no native resume success or budget reset is claimed. Native Linux
and Windows qualification remain separate FIX-11/FIX-12 obligations.

## Next
- FIX-04C is complete under the recorded manual exception; retain the original stopped run and both native NO-GOs. Final confirmation/publication use the separate manual ledger.
- Continue OSS-00 from clean published main under the operator's autonomous mandate, starting FIX-05 and subsequent actual corrective cards.

## Log

- 2026-09-05T08:38:59Z Created by operator-authorized board-only decomposition of FIX-04; no admission, implementation, runtime, status move or publication.
- 2026-09-10 Reconfirmed A/B/explicit-empty factory roots all using process env. Replaced the old two-change/full-suite draft with one native change, one cohesive checkpoint and verbose typed C1-C3 evidence. Preserved current FIX-03 admission and separate retention/artifact corrections.
- 2026-09-10T21:37:06Z accepted native OpenSpec plan
- 2026-09-10T21:38:55Z started native OpenSpec delivery
- 2026-09-10 change-1 completed: factory workspace resolution now honors active Settings (including explicit-empty fallback), composed lifecycle output/markers use the active ownership root, and direct calls retain env compatibility. Added hermetic A/B/C, marker cleanup-after-env-drift, foreign-marker, nested-failure and bound-evidence controls; documented precedence and runtime limits. Current source-bound receipt is retained under this run after final Result/Log edits.
- 2026-09-10T22:00:29Z finalization recovery recorded this run's semantic-sync mapping as a deliberate no-op: all three FIX-04C delta requirements and scenarios are already present in the canonical runtime-configuration spec. Result/Log refreshed before current C1-C3 proof collection.
- 2026-09-10T22:51:44Z repaired the retained R1-R3 evidence gaps without changing accepted scope: C1 now invokes the real scenario callback and records per-operation complete foreign inventories; C2 exercises unbound and target-bound local launch branches with explicit ownership and workspace fallback, then real discovery/cleanup after env drift; C3 invokes the actual registered callbacks in one caller task and records application-object/root restoration. Semantic sync remains a deliberate canonical no-op; current focused, changed-lane, compile, strict-spec and diff proof is being retained before runner-owned review.

- 2026-09-10T23:21:20.894933+00:00 Recorded bounded manual completion after native two-review exhaustion: preserved both NO-GOs and every run file; repaired only remaining C2 per-stop foreign-root/resource preservation assertions. Exact node and 30 lifecycle tests pass; a current-tmp-path-only foreign-marker mutation fails immediately. C1/C3 and production bytes are unchanged. One separately counted extra independent review is reserved; current verification precedes that review.

- 2026-09-10T23:28:01.472823+00:00 Additional independently counted manual review (total cycle 3, extra 1/1) accepted C1-C3 and all six scenarios with no findings; last native R1 closed. Stock archive moved exact reviewed artifacts with --skip-specs and preserved product/test/canonical bytes. Final affected verification and same-thread postarchive confirmation precede publication; original 199 native files and both NO-GOs remain unchanged.
