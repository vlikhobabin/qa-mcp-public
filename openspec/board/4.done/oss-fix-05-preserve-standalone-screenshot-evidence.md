# Preserve screenshot evidence returned by the standalone factory

## Status
4.done

## Owner
qa-mcp

## Series
oss-fix-05

## Order Index
406.24

## Lifecycle
openspec-v1

## OpenSpec Stage
native artifacts prepared; awaiting admission

## Priority
P1

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
Published-stage R1, reconfirmed on `2a4c159`: real unbound factory default and
explicit captures return paths that were already deleted. Optional local
baseline: `.runtime/qa-roadmap/oss-00/fix-05-planning/reproduction.json`.

## Summary
Preserve the existing useful unbound screenshot result while keeping actual
admitted bound sanitized/full_local policy and capture/cleanup failures truthful.

## Acceptance
- [C1] Real unbound standalone factory/default-executor screenshot calls with default, explicit relative and absolute output return readable paths containing the exact captured bytes after the call; intentional direct compatibility stays useful.
- [C2] Real admitted bound sanitized and approved full_local calls preserve their evidence-root authority, exact artifact digest and public privacy: successful sanitized capture removes raw image/path; full_local retains only its authorized image. Standalone retention grants no project approval.
- [C3] Capture failure, missing readable evidence and required-cleanup failure report failure without a successful readable artifact; bound results expose no raw path/backend-secret prose. Immediate before/after inventories prove unrelated files remain byte-identical for every failure.

## Scope
- `src/qa_mcp/mcp_server.py`: existing screenshot handler/policy boundary only.
- `tests/test_screenshot_retention.py`; directly related existing screenshot/target fixture helpers and affected consumers if needed.
- `docs/qa-mcp-tool-reference.md`, `docs/shared-core-extension.md`; linked canonical delta only.

## Non-Goals
No live display, Windows deployment, protocol/format/routing change, new ledger
policy, generic artifact trust redesign, retention TTL or root correction.
FIX-06 and FIX-08 retain their separate verdict/artifact scope. No ChangeRail work.

## Depends On
- `openspec/board/4.done/oss-fix-04c-isolate-workspace-and-ownership-roots.md`

## OpenSpec Changes
1. `oss-fix-05-preserve-standalone-screenshot-evidence`

## Design
Implementation decisions and tasks belong to the linked change. Every condition
uses the actual registered factory/default handler with a fake backend. Real
bound resolution/session/attachment proves the policy partition; a context merely
named bound does not. Compare sentinels immediately after each failure. All typed
selectors point to the focused module containing the actual acceptance nodes.

## Delivery Budget
- primary_invariant: Successful standalone screenshot evidence remains readable while admitted bound retention and truthful failure remain intact.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 90

## Budget Notes
Estimates are advisory. One complete screenshot policy partition is one native
change/checkpoint; the ordinary shared two-independent-review allowance remains.

## Canonical Specs
- `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify
- `uv run pytest -v tests/test_screenshot_retention.py tests/test_target_bound_evidence_cleanup.py --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-plan`
- `uv run pytest -v --qa-changed --qa-lane offline --durations=10`
- `uv run pytest -v --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
Retain verbose nodes/JUnit and meaningful typed C1-C3 proof AFTER final Result/Log
and semantic sync, refreshing after archive. Complete all proof before handoff;
missing/stale receipts are authorized finalization work. No full suite implied.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Unbound registered screenshot retention",
      "precondition": "Real standalone factory/default executor and synthetic image backend",
      "action": "Capture default, explicit relative/absolute outputs and direct compatibility; read returned files after each call",
      "expected": "Exact owning output paths remain readable with captured bytes; deletion sensitivity fails",
      "method": {
        "kind": "test",
        "target": "tests/test_screenshot_retention.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Admitted bound screenshot privacy and retention",
      "precondition": "Valid exact target/session/attachment, sanitized or approved full_local profile",
      "action": "Invoke real registered screenshot, record destination/content/hash and public DTO",
      "expected": "Sanitized removes raw image and path; full_local retains only authorized evidence with exact digest",
      "method": {
        "kind": "test",
        "target": "tests/test_screenshot_retention.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Capture and required-cleanup failures",
      "precondition": "Backend failure/missing image or injected unlink rejection, unrelated sentinel byte inventories",
      "action": "Run each failure independently and compare immediate outputs/files with before snapshot",
      "expected": "Failure never claims successful readable artifact; bound diagnostics safe and unrelated bytes unchanged",
      "method": {
        "kind": "test",
        "target": "tests/test_screenshot_retention.py"
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
      "decision": "Standalone retention must not grant bound raw-image approval; real admitted sanitized/full_local controls.",
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
      "decision": "Temporary screenshot writes/deletion only; exact before/after sentinel bytes and truthful capture/cleanup failure.",
      "conditions": [
        "C2",
        "C3"
      ]
    },
    {
      "kinds": [
        "concurrency",
        "restart"
      ],
      "applies": false,
      "decision": "No new shared state, context lifecycle or persistent policy; existing isolation remains in force.",
      "conditions": []
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "No release workflow change; ordinary authorized delivery remains runner-owned.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
Hermetic temporary images/files and synthetic backend/process boundaries only.
No live TestClient/screenshot, deployment, business effect or native qualification.
Final Linux/Windows qualification stays in FIX-11/FIX-12. The standing OSS-00
mandate authorizes implementation, review and ordinary commit/push.

## Related
- `docs/development/oss-00-orchestration.md`
- `docs/development/test-policy.md`

## Result
Implemented the standalone/bound screenshot retention partition in
`src/qa_mcp/mcp_server.py`: sanitized deletion now requires an admitted runtime
target, while unbound default/relative/absolute captures retain readable bytes.
Added real registered-factory C1-C3 controls in
`tests/test_screenshot_retention.py`, including bound sanitized/full_local
digest/privacy checks, backend/missing-evidence failures, cleanup rejection and
immediate unrelated-file byte inventories. Updated the shared-core and tool
reference consumer policy text. Focused proof is retained with verbose node
output; typed C1-C3 evidence is recorded from the source-bound selectors after
this Result/Log update.

Checks: focused 50 passed; changed offline 942 passed; changed integration 1
passed; `qa_compile_changed` compiled 2 files; strict OpenSpec validation passed;
`git diff --check` passed. Archive-finalization refresh reran the source-bound
C1-C3 selectors (3, 2 and 3 passed); current typed proof is refreshed for the
archived payload before handoff.

## Next
- continue with the next dependency-ready epic card

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-10 Reconfirmed default/explicit screenshot deletion through the actual standalone factory after FIX-04C publication. Replaced the old two-change/full-suite draft with one native checkpoint and C1-C3 actual factory/policy/failure proof; aligned all typed selectors to the new focused screenshot module.
- 2026-09-10T23:40:13Z accepted native OpenSpec plan
- 2026-09-10T23:41:26Z started native OpenSpec delivery
- 2026-09-10T23:53:00Z implemented screenshot retention policy partition; focused and affected offline/integration checks, compile, strict spec validation and diff checks passed; source-bound C1-C3 evidence refresh follows this Result/Log update.
- 2026-09-11T00:00:58Z semantic sync merged the shared-core screenshot requirements; target-bound canonical surface was a deliberate no-op because no delta was supplied. Refreshed current source-bound typed proof: `c1-final` (3 passed), `c2-final` (2 passed), and `c3-final` (3 passed), all via `tests/test_screenshot_retention.py` on the offline lane.
- 2026-09-11T00:13:37Z archive-refresh reran C1 (3), C2 (2), and C3 (3) source-bound selectors with verbose output after stock archive; Result/Log is now frozen for current typed evidence refresh.

## Delivery Receipt

- Independent review: `GO` at `2026-09-11T00:18:16Z`.
- Final repository verification: `passed` at `2026-09-11T00:21:17Z`; 5/5 configured commands succeeded.
- Deterministic done transition recorded at `2026-09-11T00:21:25Z` for publish.
