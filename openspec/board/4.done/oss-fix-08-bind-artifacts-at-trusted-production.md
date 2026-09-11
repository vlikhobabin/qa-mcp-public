# Bind evidence receipts at trusted artifact production

## Status
4.done

## Owner
qa-mcp

## Series
oss-fix-08

## Order Index
406.27

## Lifecycle
openspec-v1

## OpenSpec Stage
archived; independently verified under operator-authorized manual completion

## Priority
P2

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
Published-stage R7, reconfirmed on `15ab9a7`: registered bound full_local capture
promotes a pre-existing in-root unrelated file with a false all-zero digest.
Optional local baseline: `.runtime/qa-roadmap/oss-00/fix-08-planning/reproduction.json`
and `current-applicability.json`; current published source hashes match the probe.
The problem and desired regression are fully specified here for a clean clone.

## Summary
Bind current artifact authority at actual trusted production, verify path/content,
and preserve independent operation cleanup, public privacy and unbound capture.

## Acceptance
- [C1] Shared execution never mints authority from raw executor paths: old in-root files, false well-formed hashes, absent production and stale/foreign/lookalike claims fail without current path disclosure or borrowed-file changes. Real shared MCP/scenario refusals retain exact fixed artifact/type/size/provenance/receipt priority.
- [C2] Actual default local/Windows-host screenshot factories bind trusted current production to application/operation/scope/path/content, using only substituted external backends in tests. Both policies work; mismatched returned paths, symlinks, false hashes and postproduction changes fail before success. Sanitized deletes only its owned raw file and retains verifiable safe metadata; full_local returns exact readable bytes/path. Unbound standalone/direct behavior stays useful.
- [C3] Overlapping same-ledger scopes with identical bytes/IDs and different paths, plus distinct applications under both opposite policy combinations, have exact own result/destination/call mapping. Success/failure closes only own records/files; foreign snapshots remain unchanged immediately while the sibling is still paused after production. Scope carrier restores in the original callback context; no cross-request authority or raw sanitized output.

## Scope
- `src/qa_mcp/core/boundary.py`, `src/qa_mcp/core/operations.py`, `src/qa_mcp/mcp_server.py`; `src/qa_mcp/core/contracts.py` only if needed.
- `tests/test_trusted_artifact_production.py`; affected positive-core/public-integration, screenshot-retention, target-bound-evidence-cleanup and shared scenario tests; directly affected test-only helpers.
- `docs/qa-mcp-tool-reference.md`, `docs/shared-core-extension.md`; three linked canonical deltas.

## Non-Goals
No artifact store/signing/storage migration, configurable producer/schema registry,
hostile arbitrary Python sandbox, live screenshot/native qualification, unrelated
BDD routing changes, ChangeRail development or tests. Protect untrusted result data.

## Depends On
- `openspec/board/4.done/oss-fix-05-preserve-standalone-screenshot-evidence.md`
- `openspec/board/4.done/oss-fix-06-preserve-display-failure-verdicts.md`
- `openspec/board/4.done/oss-fix-07-make-bound-window-reads-useful.md`

## OpenSpec Changes
1. `oss-fix-08-bind-artifacts-at-trusted-production`

## Design
Every Cn uses the actual focused acceptance module. Positive factory controls
must invoke real registered/default producers, replacing only external boundaries.
Custom executor claims serve negatives. Preserve existing exact assertions and
production schema authority. Concurrency uses immediate foreign snapshots before
sibling release; same-context callback checks expose missing carrier reset.

## Delivery Budget
- primary_invariant: Only current trusted production can authorize an artifact receipt and its path/content identity.
- expected_wall_minutes: 40
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 4
- estimated_production_loc: 320

## Budget Notes
One coherent native checkpoint; time/size advisory. Two ordinary independent
review sessions across run/continuations, retaining interrupted sessions too.

## Canonical Specs
- `openspec/specs/qa-mcp-positive-core-operation-boundary/spec.md`
- `openspec/specs/qa-mcp-positive-operation-boundary-public-integration/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify
- `uv run pytest -v tests/test_trusted_artifact_production.py --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-plan`
- `uv run pytest -v --qa-changed --qa-lane offline --durations=10`
- `uv run pytest -v --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
Retain actual setup/action/assertion source spans, verbose terminal nodes/JUnit,
UTC timing and exact selected checks after final Result/Log and semantic sync.
Command receipts AND registered current typed C1-C3 proofs precede handoff;
complete finalization, archive refresh and same-thread confirmation. Serialize
evidence writes. No full-suite requirement or header-fragment proof.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Untrusted result cannot authorize evidence",
      "precondition": "Admitted actual shared MCP/scenario boundary; controlled untrusted executor data and old in-root files",
      "action": "Exercise old path/false hash/no production, stale/foreign/lookalike claims and malformed artifacts",
      "expected": "Exact artifact/receipt refusal before disclosure; no authority minted and borrowed files unchanged",
      "method": {
        "kind": "test",
        "target": "tests/test_trusted_artifact_production.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Trusted actual default screenshot production",
      "precondition": "Real default local/Windows-host factories and registered captures; external backend only substituted; both policies",
      "action": "Capture current bytes; inject wrong returned path, symlink, false hash and postproduction modification; check deliberate unbound behavior",
      "expected": "Exact own readable full_local evidence and safe sanitized metadata; invalid production fails; borrowed files preserved",
      "method": {
        "kind": "test",
        "target": "tests/test_trusted_artifact_production.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Concurrent authority and owned cleanup",
      "precondition": "Overlapping same-ledger identical-byte/ID scopes at distinct paths; separate apps and both opposite policies",
      "action": "Pause sibling after production/registration, snapshot files/records, complete current success/failure, compare before sibling release; inspect same-context reset",
      "expected": "Exact own path/result/call mapping; foreign snapshots unchanged; only own records/files closed; current carrier restored",
      "method": {
        "kind": "test",
        "target": "tests/test_trusted_artifact_production.py"
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
      "decision": "Untrusted result paths/hash/classes cannot mint authority; exact current production and fixed validation priority.",
      "conditions": [
        "C1",
        "C2"
      ]
    },
    {
      "kinds": [
        "concurrency"
      ],
      "applies": true,
      "decision": "Request-local producer scope; identical IDs and paused-sibling immediate record/file inventories on both policies, success/failure reset.",
      "conditions": [
        "C3"
      ]
    },
    {
      "kinds": [
        "restart"
      ],
      "applies": false,
      "decision": "No persisted ledger or resumable state; stale scopes remain invalid.",
      "conditions": []
    },
    {
      "kinds": [
        "mutation",
        "external_effects"
      ],
      "applies": true,
      "decision": "Only temporary synthetic backend files; cleanup of own production, preserve borrowed paths and foreign sibling/sentinel bytes.",
      "conditions": [
        "C2",
        "C3"
      ]
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "Ordinary authorized runner publication only; no release workflow changes.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
Hermetic Python fixtures, temporary synthetic files and substituted external
boundaries; runtime_contours=0. No live TestClient/display/socket, Windows-native
qualification or release. OSS-00 mandate authorizes implementation, review,
commit and ordinary push. FIX-11/FIX-12 own native qualification.

## Related
- `docs/development/oss-00-orchestration.md`
- `docs/development/test-policy.md`

## Result
2026-09-11T04:25:23.248751+00:00: FIX-08 implemented and independently accepted under operator-authorized manual completion. Actual default local/Windows-host screenshot production binds an exclusive owned destination and current content hash/file identity; raw claims, absent evidence, invalid metadata and stale/foreign/lookalike receipts fail with exact taxonomy. Same-ledger identical-ID overlap, both opposite-policy application pairs, immediate paused-sibling inventories, cleanup failures and same-context restoration are covered; unbound capture remains readable. Prearchive focused/affected offline/integration, compile, 70 strict specs and diff passed; exact counts and durations are retained in the manual ledger. Independent review cycle 1 is GO. All eleven stopped native-run files remain unchanged; no native success or live qualification claimed. Final verification follows this Result/Log and stock archive.

## Next
FIX-08 is complete under the retained manual exception. Continue OSS-00 from clean published main with FIX-09A; preserve all stopped native attempts and final manual evidence.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-11 Refreshed historical two-change draft into one native producer-authority change after FIX-07 publication. Explicit actual-factory/hash/ownership/concurrency acceptance replaces obsolete full-suite and FF instructions.
- 2026-09-11T03:22:28Z accepted native OpenSpec plan
- 2026-09-11T03:24:04Z started native OpenSpec delivery

- 2026-09-11T04:09:55.291300+00:00: Supervisor stopped the partial native implementation before review after reproducing false-digest success under both policies. Completed accepted C1-C3, including same-ledger identical-ID overlap, opposite-policy applications, immediate paused-sibling inventories, wrong-path-before-read protection and cleanup failure restoration. Two ordinary independent review sessions remain; native history is retained separately. Current verification pending.

- 2026-09-11T04:15:11.407030+00:00: Completed first verification (681 focused, 1542 offline, one integration, 70 specs/compile/diff). A further malformed receipt.path equality probe exposed an exact-class gap; fixed before review, with failing-before/passing-after evidence and callback-free regression. Fresh current proof follows this final Log update.

- 2026-09-11T04:25:23.249363+00:00 Independent manual review cycle 1 returned GO. Stock archive moved the seven exact accepted artifacts to `openspec/changes/archive/2026-09-11-oss-fix-08-bind-artifacts-at-trusted-production` with --skip-specs; product/test/docs/canonical bytes unchanged. Final current checks follow this Result/Log update.
