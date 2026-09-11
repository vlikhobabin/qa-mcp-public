# Reject project attach without runtime target evidence

## Status
3.inprogress

## Lifecycle
openspec-v1

## Owner

qa-mcp

## Series

oss-fix-02

## Order Index

406.21

## OpenSpec Stage
native plan prepared; not admitted

## Priority

P1

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage code review, 2026-09-05, finding R8, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- The symptom and required regression are restated here; ignored local review files are optional context, not clean-clone prerequisites. Original reproduction tests asserted the bug and must be inverted into desired-behavior regressions.

## Summary

Linux attach currently promotes TCP reachability into a project-bound session; remote attach checks PID/port/listening but not observed infobase identity. Stop issuing trusted target provenance for an endpoint whose target/generation has not been proven.

## Acceptance

### Requirement: Fail closed on missing or mismatched observation

#### Scenario: Correction 02 control 1

- [C1] WHEN only TCP reachability or PID/port/listening is supplied, or observation does not bind the expected target and generation to the current process, THEN bound attach returns a fixed blocked result without admitting a session or sending protocol/UI commands.

### Requirement: Do not invent observation authority

#### Scenario: Correction 02 control 2

- [C2] WHEN admission considers provider data, THEN copying the declared profile, a caller-provided fingerprint or an old owned handle cannot become current observation; no new trusted-observer format or transport is invented in this slice.

### Requirement: Preserve supported owned and unbound paths

#### Scenario: Correction 02 control 3

- [C3] WHEN existing validated owned launch or explicit unbound attach is used, THEN its existing contract is preserved; documentation states that fresh non-owned bound attach remains unavailable until a separately reviewed observer can prove identity.

## Scope

- `src/qa_mcp/mcp_server.py`
- `src/qa_mcp/core/runtime_target.py`
- Focused regression tests: `tests/test_target_bound_lifecycle_admission.py`, `tests/test_mcp_server.py`.
- The linked delta owns canonical lifecycle changes; synchronize it using stock OpenSpec before independent review. Update consumer documentation only for the corrected contract.

## Affected Capabilities

- Endpoint reachability alone never authorizes a project-bound attachment.

## Non-Goals

- No new observer implementation, business reads, live attach, target discovery, fallback base selection or claim that general non-owned bound attach now works.
- No unrelated changes, automatic publication or authority to execute this card from a planning request.

## Depends On

- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`

## OpenSpec Changes

1. `oss-fix-02-native-bound-attach-containment`

## Design
Implementation design and ordered tasks belong to the linked native change.
- Input-safety risk (C1/C2): declared profile, caller identity and stale handles must never become current observed target provenance.
- Mutation/external-effects risk (C1): assert unchanged admission/session state and zero protocol/UI commands for refused attach.
- Compatibility (C3): preserve real entry-point behavior for validated owned launch and explicit standalone attach using positive offline controls.
- Restart/concurrency are inapplicable: this slice adds no persistence, locks or scheduling. Publication is runner-owned and outside the product implementation. No new protocol claim or live qualification is made.

## Delivery Budget

- primary_invariant: Endpoint reachability alone never authorizes a project-bound attachment.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 2
- estimated_production_loc: 180

## Budget Notes

Provisional estimate for one Python-side invariant with hermetic fixtures and its delivery checks, not a wall-clock promise or READY verdict. Product-file estimates exclude tests and docs; changes outside the named product seam require re-sizing, not a silent scope expansion.

## Canonical Specs

- `openspec/specs/qa-mcp-target-bound-testclient-lifecycle/spec.md`
- `openspec/specs/qa-mcp-runtime-target-contract/spec.md`

## Verify
- `uv run pytest -q tests/test_target_bound_lifecycle_admission.py tests/test_mcp_server.py`
```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "public bound attach admission",
      "precondition": "reachable endpoint without current matching target observation",
      "action": "call the registered local or remote bound attach tool",
      "expected": "typed blocked result, unchanged session and zero protocol/UI commands",
      "method": {
        "kind": "test",
        "target": "tests/test_target_bound_lifecycle_admission.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "trusted observation ownership",
      "precondition": "profile copy, caller fingerprint or stale owned handle offered as observation",
      "action": "trace the public admission path and provenance producer",
      "expected": "declaration never promoted to observation and no invented trusted producer",
      "method": {
        "kind": "inspection",
        "target": "src/qa_mcp/mcp_server.py"
      },
      "stage": "review"
    },
    {
      "condition": "C3",
      "seam": "supported owned and standalone lifecycle",
      "precondition": "validated owned launch or explicit unbound attach inputs",
      "action": "exercise their existing registered entry points",
      "expected": "positive ownership, target checks and standalone behavior preserved",
      "method": {
        "kind": "test",
        "target": "tests/test_mcp_server.py"
      },
      "stage": "final"
    }
  ],
  "risks": [
    {
      "kinds": [
        "input_safety"
      ],
      "applies": true,
      "decision": "Refuse declaration-only target proof at the public boundary.",
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
      "decision": "Refuse before session mutation and native commands; assert before/after state.",
      "conditions": [
        "C1"
      ]
    },
    {
      "kinds": [
        "restart",
        "concurrency",
        "publication"
      ],
      "applies": false,
      "decision": "No persistence or scheduling changes; publication remains runner-owned.",
      "conditions": []
    }
  ]
}
```
- The runner supplies independent review and the configured final non-live floor. Static plan validation is not observed proof.

## Runtime And Authority

The planned implementation verifies a Python-side contract offline (runtime_contours=0), with synthetic files and fake sockets/backends; it does not claim native correctness. Release qualification is separately owned by `openspec/board/1.backlog/oss-fix-11-verify-corrected-linux-runtime.md` and `openspec/board/1.backlog/oss-fix-12-verify-corrected-windows-runtime.md`. No live TestClient, Windows deployment or mutation is authorized here.

## Related

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `docs/development/local-changerail-delivery.md`
- `docs/development/legacy-board-transition.md`

## Result
checkpoints 1 and 2 complete; all six native OpenSpec tasks complete; the
bound-attach provenance requirement and its three scenarios are semantically
synced into the canonical lifecycle spec. Repair 01 strengthens C1 at the
factory-registered MCP boundary, covering reachable local/remote endpoints and
both empty and existing owned session state without new observer behavior. After
archive, refreshed offline C1/C3 evidence confirms the archived payload remains
stable with the supported owned and unbound paths intact.

## Next
- Start from clean published main after the FIX-01 one-off reconciliation in docs/development/native-transition.md; verify its done dependency before admission.
- Validate this native plan with `chrl native-accept --dry-run`, then admit and deliver only within the authorized clean-main scope. Do not run legacy FF for this card.

## Log
- 2026-09-09T06:07:02Z Replanned the existing containment scope as one native OpenSpec change with two task groups. Historical FIX-01 run and product bytes remain unchanged.
- 2026-09-09T08:20:55Z accepted native OpenSpec plan
- 2026-09-09T08:23:39Z started native OpenSpec delivery
- 2026-09-09T08:31:17Z Checkpoint 1 rejected bound local and remote attach before native or host-agent commands; current focused C1 evidence is `c1-bound-attach-refusal` (209 passed).
- 2026-09-09T08:37:23Z Checkpoint 2 retained validated owned-launch and explicit standalone-attach controls, documented the non-owned bound-attach limitation, and recorded focused C3 evidence `c3-supported-owned-and-unbound-paths` (210 passed).
- 2026-09-09T08:42:00Z Semantically synced the lifecycle delta into its canonical spec; retained `sync-report.md` and the native sync receipt. `./bin/openspec validate --specs --strict --no-interactive` passed (70 specs).
- 2026-09-09T09:16:59Z Repair 01 added registered-boundary C1 coverage for local/remote reachable endpoints and empty/owned state snapshots; refusal preserves target/generation/session/attachment identity and command inventories.
- 2026-09-09T09:27:07Z Archive-refresh reran the focused C1/C3 lifecycle and MCP proof (`archive-refresh-c1-c3`): 214 passed; the evidence recorder retained an unchanged archived-payload fingerprint.
