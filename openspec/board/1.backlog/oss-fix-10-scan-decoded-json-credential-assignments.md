# Scan decoded JSON credential assignments without widening fixture allowances

## Status

1.backlog

## Owner

qa-mcp

## Series

oss-fix-10

## Order Index

406.29

## OpenSpec Stage

operator-refined backlog draft; not admitted

## Priority

P2

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage code review, 2026-09-05, finding R10, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- The symptom and required regression are restated here; ignored local review files are optional context, not clean-clone prerequisites. Original reproduction tests asserted the bug and must be inverted into desired-behavior regressions.

## Summary

The public scanner parses JSON for Base64 fields but does not inspect ordinary decoded keys/strings. A Unicode escape inside a password-suffixed key bypasses the raw assignment scanner. Close the semantic JSON/JSONL gap while preserving exact existing allowlist accounting and the frozen I2 oracle.

## Acceptance

### Requirement: Detect semantic JSON assignments

#### Scenario: Correction 10 control 1

- WHEN JSON or JSONL uses escaped characters in a supported credential key or value, including nested objects and arrays, THEN non-empty semantic assignments are detected with no minimum secret length and malformed independently parseable lines retain fail-closed behavior.

### Requirement: Preserve exact fixture accounting

#### Scenario: Correction 10 control 2

- WHEN raw and decoded views represent the same approved fixture, THEN allowances are not duplicated or widened; excess, missing, wrong-path and wrong-source occurrences still fail and any required migration is exact-tuple and reviewed.

### Requirement: Keep safe output and immutable gates

#### Scenario: Correction 10 control 3

- WHEN detection or decoding fails, THEN only safe category/path/source/count diagnostics are emitted; the published I2 bytes and all 23 hostile controls remain unchanged and audit/provenance/snapshot checks reject the new hostile fixture.

## Scope

- `tools/public_readiness.py`
- Focused regression tests: `tests/test_public_repository_readiness.py`.
- Direct updates to the governing canonical specs and consumer documentation only when the corrected contract changes. No new legacy lifecycle artifacts.

## Affected Capabilities

- Equivalent raw and JSON-escaped credential assignments receive the same safe fail-closed disclosure verdict.

## Non-Goals

- No search for actual credentials in ignored runtime, credential rotation, publication, history rewrite or general-purpose DLP platform.
- No unrelated changes, automatic publication or authority to execute this card from a planning request.

## Depends On

- none

## Change Set

- `oss-fix-10-cover-escaped-json-semantics`
- `oss-fix-10-integrate-safe-scan-accounting`

## Design

Inspect parsed key/value semantics in addition to raw bytes and decoded Base64. Define deterministic source identity and deduplication so equivalent views do not spend allowance capacity twice. Never print the synthetic secret in failure logs. Do not change the frozen I2 artifacts or add directory/whole-file exceptions.

## Implementation Plan

1. Create temporary synthetic escaped-key/value JSON/JSONL controls; assert blocked semantic findings rather than preserving the audit's bug-confirming assertion.
2. Implement semantic scanning and reviewed exact-view accounting; rerun audit/provenance/docs plus the isolated snapshot and immutable I2 mutations.
3. Complete focused evidence after final Result/Log edits; the authorized outer runner owns independent review, final verification, done, commit and push.

## Delivery Budget

- primary_invariant: Equivalent raw and JSON-escaped credential assignments receive the same safe fail-closed disclosure verdict.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 180

## Budget Notes

Provisional estimate for one Python-side invariant with hermetic fixtures and its delivery checks, not a wall-clock promise or READY verdict. Product-file estimates exclude tests and docs; changes outside the named product seam require re-sizing, not a silent scope expansion.

## Canonical Specs

- `openspec/specs/qa-mcp-public-provenance/spec.md`
- `openspec/specs/qa-mcp-publication-policy/spec.md`

## Verify

- `uv run pytest -q tests/test_public_repository_readiness.py`
- `git diff --check`
- `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`
- `uv run python -m compileall -q src tests`
- `./bin/openspec validate --specs --strict --no-interactive`
- `python3 tools/public_readiness.py audit --history --json`
- `python3 tools/public_readiness.py provenance --check --json`
- `python3 tools/protocol-research/oss07_i2/verify_matrix.py --run-mutations`

## Runtime And Authority

The planned implementation verifies a Python-side contract offline (runtime_contours=0), with synthetic files and fake sockets/backends; it does not claim native correctness. Release qualification is separately owned by `openspec/board/1.backlog/oss-fix-11-verify-corrected-linux-runtime.md` and `openspec/board/1.backlog/oss-fix-12-verify-corrected-windows-runtime.md`. No live TestClient, Windows deployment or mutation is authorized here.

## Related

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`
- `docs/development/local-changerail-delivery.md`
- `docs/development/legacy-board-transition.md`

## Result

not started; planning only. No finding is closed by this card's creation.

## Next

- Review the draft at a clean tracked fingerprint, then perform local FF/admission before any todo transition. Numeric size checks alone do not authorize execution.
- Existing historical in-progress cards and the separately unapproved migration pilot remain unchanged. Resolve delivery readiness by the local workflow; never clean or publish unrelated work to satisfy a gate.

## Change 1: `oss-fix-10-cover-escaped-json-semantics`

### Why

The public scanner parses JSON for Base64 fields but does not inspect ordinary decoded keys/strings. A Unicode escape inside a password-suffixed key bypasses the raw assignment scanner. Close the semantic JSON/JSONL gap while preserving exact existing allowlist accounting and the frozen I2 oracle.

### Goal

Create temporary synthetic escaped-key/value JSON/JSONL controls; assert blocked semantic findings rather than preserving the audit's bug-confirming assertion.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- Card-level dependencies above.

### Ordered Tasks

1. Create temporary synthetic escaped-key/value JSON/JSONL controls; assert blocked semantic findings rather than preserving the audit's bug-confirming assertion.
2. Run `uv run pytest -q tests/test_public_repository_readiness.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Change 2: `oss-fix-10-integrate-safe-scan-accounting`

### Why

The first checkpoint alone does not prove the full card invariant; verify its required consumer/policy controls.

### Goal

Implement semantic scanning and reviewed exact-view accounting; rerun audit/provenance/docs plus the isolated snapshot and immutable I2 mutations.

### Scope

- The card's named product/test/spec seams only; no independent feature or runtime contour.

### Acceptance

- The relevant card-level scenarios pass with desired-behavior assertions, not the original bug-confirming assertions.

### Depends On

- `oss-fix-10-cover-escaped-json-semantics`.

### Ordered Tasks

1. Implement semantic scanning and reviewed exact-view accounting; rerun audit/provenance/docs plus the isolated snapshot and immutable I2 mutations.
2. Run `uv run pytest -q tests/test_public_repository_readiness.py` for the changed behavior and retain concise, secret-safe evidence; reuse unchanged successful checks.

## Log

- 2026-09-05T08:11:47Z Created from the published-stage review at operator request; board-only draft, no implementation, runtime, admission or publication.
