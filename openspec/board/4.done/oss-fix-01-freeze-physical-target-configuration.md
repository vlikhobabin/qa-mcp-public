# Freeze one physical target configuration for the application lifetime

## Status
4.done

## Owner

qa-mcp

## Series

oss-fix-01

## Order Index

406.20

## OpenSpec Stage

completed by the operator-authorized one-off reconciliation; original pilot history retained

## Priority

P1

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage code review, 2026-09-05, finding R9, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- The symptom and required regression are restated here; ignored local review files are optional context, not clean-clone prerequisites. Original reproduction tests asserted the bug and must be inverted into desired-behavior regressions.

## Summary

A validated runtime resolution freezes the env filename but launch/attach reread its mutable contents. Changing the fixture infobase after composition currently changes the physical target without changing logical fingerprint or generation. Make every provider-owned consumer use the same immutable physical resolution.

## Acceptance

### Requirement: Freeze physical configuration once

#### Scenario: Correction 01 control 1

- WHEN the env fixture changes, disappears or becomes a symlink after composition, THEN existing consumers cannot silently select its new infobase, principal, platform or source root; they keep the admitted immutable configuration or return a fixed drift error before side effects.

### Requirement: Keep consumers and rebind coherent

#### Scenario: Correction 01 control 2

- WHEN lifecycle and hidden tool arguments consume one resolution, THEN they use the same snapshot; constructing a newly validated resolution is the only rebind path and stale sessions cannot carry into it.

### Requirement: Preserve confidentiality and unbound compatibility

#### Scenario: Correction 01 control 3

- WHEN readiness, errors and public identity are serialized, THEN physical values and credentials remain absent; explicit unbound configuration retains its documented behavior.

## Scope

- `src/qa_mcp/core/runtime_target.py`
- `src/qa_mcp/core/application.py`
- `src/qa_mcp/mcp_server.py`
- Focused regression tests: `tests/test_runtime_target_contract.py`, `tests/test_target_bound_lifecycle_admission.py`, `tests/test_target_bound_evidence_cleanup.py`.
- Direct updates to the governing canonical specs and consumer documentation only when the corrected contract changes. No new legacy lifecycle artifacts.

## Affected Capabilities

- One logical binding generation resolves to exactly one immutable physical configuration.

## Non-Goals

- No live target observation, protocol changes, source import, provider provisioning or automatic reconnect.
- No unrelated changes, automatic publication or authority to execute this card from a planning request.

## Depends On

- none

## Change Set
- `oss-fix-01-freeze-provider-config`
- `oss-fix-01-bind-all-physical-consumers`

## Design

Prefer a private immutable provider-config snapshot made during resolution; do not hash or expose credentials as public provenance. If retaining a path, verify frozen content identity before every use with no check/read race. Hidden arguments and lifecycle must consume the same source. Reject env fallback and ad-hoc global caching.

## Implementation Plan

1. Add a regression that composes an application, changes only its temporary env fixture, and observes lifecycle plus hidden-argument consumers. Implement frozen resolution without starting a client.
2. Route lifecycle and composition consumers through that resolution; verify no secret fragments and explicit new-resolution rebind. Update the governing canonical requirements directly.
3. Complete focused evidence after final Result/Log edits; the authorized outer runner owns independent review, final verification, done, commit and push.

## Delivery Budget

- primary_invariant: One logical binding generation resolves to exactly one immutable physical configuration.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 180

## Budget Notes

Provisional estimate for one Python-side invariant with hermetic fixtures and its delivery checks, not a wall-clock promise or READY verdict. Product-file estimates exclude tests and docs; changes outside the named product seam require re-sizing, not a silent scope expansion.

## Canonical Specs

- `openspec/specs/qa-mcp-runtime-target-contract/spec.md`
- `openspec/specs/qa-mcp-target-bound-testclient-lifecycle/spec.md`
- `openspec/specs/qa-mcp-target-bound-evidence-cleanup/spec.md`

## Verify

- `uv run pytest -q tests/test_runtime_target_contract.py tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py`
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

## Result
Implemented a private typed physical-config snapshot during runtime resolution.
Lifecycle construction and hidden tool arguments use that snapshot instead of
rereading the profile env fixture; composition rejects a session whose target
object or binding generation does not match the active resolution. Bound
`infobase_info` and `get_state` now serialize logical target provenance only,
while unbound diagnostic output remains explicit. Governing runtime-target,
lifecycle and evidence-cleanup specifications describe the freeze, rebind and
confidentiality boundaries. Offline regressions invoke lifecycle after fixture
rewrite, absence and symlink replacement; exercise a registered hidden-value
consumer; and prove old and newly resolved applications launch their respective
snapshots.

The measured pilot stopped without publication after its final-verification
repair allowance was exhausted. The separately authorized offline correction
aligns positive-operation integration fixtures with the admitted binding
generation and reconciles exact publication-scanner allowances for the reviewed
Python expressions and synthetic test sentinels. Negative session mutations
retain the admitted sequence so they isolate their named identity violation.
No product behavior or scanner rules were weakened. The prior runner GO and
manifest describe the pre-correction payload, not this amended working tree;
that amendment remained in progress until the one-off reconciliation below.

The operator explicitly authorized finalization, commit and push of all current
repository changes on 2026-09-09. This card closes through that one-off
reconciliation, separately from the stopped pilot. The product/ordinary-harness run passed 2280 non-live tests with 74.69% product coverage. Publication additionally requires all 638 historical-finalizer cases, native integration and finding-specific repairs, strict specs, compilation, wiring and the public-source audit; their terminal results are retained with this reconciliation.
Fresh independent review of the combined candidate and its repairs is retained
under `.runtime/changerail/publication-20260909/`; publication requires its GO
and an index tree matching the reviewed candidate. The commit containing this
entry binds the final source. No old GO, manifest, lifecycle marker or runtime
qualification has been renewed. The four frozen historical board records remain
byte-identical and the general offline finalizer remains disabled.

## Next
- Continue with native OSS-FIX-02 under its own delivery authority; no remaining FIX-01 implementation work.

## Change 1: `oss-fix-01-freeze-provider-config`

### Why

A validated runtime resolution freezes the env filename but launch/attach reread its mutable contents. Changing the fixture infobase after composition currently changes the physical target without changing logical fingerprint or generation. Make every provider-owned consumer use the same immutable physical resolution.

### Goal

Add a regression that composes an application, changes only its temporary env fixture, and observes lifecycle plus hidden-argument consumers. Implement frozen resolution without starting a client.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- Card-level dependencies above.

### Ordered Tasks

1. Add a regression that composes an application, changes only its temporary env fixture, and observes lifecycle plus hidden-argument consumers. Implement frozen resolution without starting a client.
2. Run `uv run pytest -q tests/test_runtime_target_contract.py tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Change 2: `oss-fix-01-bind-all-physical-consumers`

### Why

The first checkpoint alone does not prove the full card invariant; verify its required consumer/policy controls.

### Goal

Route lifecycle and composition consumers through that resolution; verify no secret fragments and explicit new-resolution rebind. Update the governing canonical requirements directly.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- `oss-fix-01-freeze-provider-config`.

### Ordered Tasks

1. Route lifecycle and composition consumers through that resolution; verify no secret fragments and explicit new-resolution rebind. Update the governing canonical requirements directly.
2. Run `uv run pytest -q tests/test_runtime_target_contract.py tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Log
- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
- 2026-09-05T16:12:28Z accepted by deterministic chrl-ff admission
- 2026-09-05T17:09:17Z started direct implementation in the primary main checkout by board-do
- 2026-09-05T17:14:48Z completed both Change checkpoints: froze allowlisted physical configuration at resolution, routed lifecycle and hidden consumers through it, rejected stale session composition, updated canonical specs, and passed the focused 62-test regression suite.
- 2026-09-05T17:23:27Z repaired semantic-review findings: made bound diagnostics logical-only, added registered file/client-server serialization checks, deletion/symlink fixture drift coverage, and distinct-resolution rebind/session coverage; focused suite passed 65 tests.
- 2026-09-05T17:34:36Z repaired final-verification coverage finding: invoked lifecycle during rewrite, absent-fixture and symlink states; captured registered hidden values through an offline catalog backend; and observed old/new resolution lifecycle targets. Focused suite passed 66 tests.
- 2026-09-05T18:09:14Z applied the separately authorized offline correction for the failed pilot floor: aligned integration session generations and reconciled exact public-scanner fixtures, removing obsolete allowances. Integration regressions passed 116 tests; scanner, public audit and provenance checks passed 19 tests. Preserved the stopped runner's evidence and budgets; no handoff, live execution, done transition, commit or push.
- 2026-09-09 Operator-authorized one-off reconciliation closes FIX-01 with current offline checks and fresh combined-candidate review; old pilot receipts and attempts remain unchanged. Native FIX-02 is the next product plan, not an automatically launched delivery.
