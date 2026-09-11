# Implement Positive Core Operation Boundary

## Status
4.done

## Owner
unassigned

## Series
oss-04d-r7

## Order Index
4034.867

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Source Lineage
- Build from published `main` after R5-R2/A4. Failed stashes are evidence only
  and MUST NOT be restored wholesale.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `yes`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/oss-04d-a4-authorize-positive-core-operation-boundary.md","authorization_id":"oss-04d-a4-authorize-positive-core-operation-boundary"}`

## Goal
Implement the immutable positive public-result schema, context-local evidence
ledger and total bounded core normalizer from clean published `main`.

## Acceptance
- Application-composed exact operation schemas are immutable, callback-free and
  cannot be supplied or replaced by dynamic data.
- Undeclared keys are omitted without value inspection; at a declared path,
  every wrong class, non-exact type,
  subclass, non-member literal or invalid value returns complete fixed
  `invalid-executor-result` with no partial result or input fragment.
- `value.referenceLabel` and `error.details.referenceLabel` use exact frozen
  operation/path-local `literal_text(("Reference label 7",))`; only that exact
  built-in public literal preserves.
- The finite class catalog is exact: built-in boolean; signed-64 `int64`;
  signed-64 integer or finite built-in float `finite_number`; built-in
  `reference_count` 0–2,147,483,647; operation/path literal text; and exact
  `documentation_url`, which accepts only exact built-in `str` values admitted
  by the published public HTTP(S) fixed-point canonicalizer and emits its
  canonical URL. Exact-depth 1–4 benign encoded-path controls are admitted and
  canonicalized; depth-5 non-fixed, private/local/userinfo/query/fragment/
  invalid-authority values, wrong types and string subclasses return the
  complete fixed `invalid-executor-result` with the URL absent and no fragment.
- Full-local paths require a current exact-scope receipt below a frozen root and
  enforce 2,047/2,048/2,049 canonical-scalar controls.
- Artifact id (`127/128/129`), media (`126/127/128`), SHA
  (`empty/71` and malformed `70/72`), sensitivity, validation order and node
  accounting use the exact published outcomes.
- Shared-node `511/512/513` and canonical-byte `65,535/65,536/65,537` controls
  yield preserve/preserve/fixed failure.
- Path, connection/alias and local IPv4/IPv6 hostiles fail at the same exact
  value/error paths and artifact fields while safe controls preserve.
- Added production lines are at most 300; no public routing/lifecycle/new
  authority or wire protocol.

## Scope
- Core schema, ledger, provenance, URL admission and reconstruction.
- Direct test-first Linux matrix and exact-source Windows offline proof.
- No MCP/ScenarioRunner routing, lifecycle, live 1C or failed-stash restoration.

## Change Set
1. `implement-qa-mcp-positive-core-operation-boundary` -
   `openspec/changes/archive/2026-08-26-implement-qa-mcp-positive-core-operation-boundary/`

## Depends On
- `oss-04d-r5-r2-resolve-positive-result-mismatch-outcome`
- `oss-04d-a4-authorize-positive-core-operation-boundary`

## Blocks
- `oss-04d-a5-authorize-positive-operation-boundary-integration`

## Verify
- Exact intended-oracle RED retained; direct positive-schema/authority/bounds
  matrix passed after rescue 2: `408 passed`.
- Same-path exact-valid, alternate-value, wrong-class, subclass and undeclared
  cells assert the complete public outcome, not only an admission boolean.
- Per-class tests pair valid, wrong-type, subclass and invalid-domain cells:
  int64 min/max/outside, finite float/NaN/infinities, reference count
  0/max/outside, literal member/non-member and canonical/private/userinfo/
  query/fragment/non-fixed `documentation_url` values. URL tests use exact
  built-in `str`, canonical public controls and admitted encoded-path controls
  at depths 1–4, asserting the emitted canonical URL; all invalid cells assert
  complete fixed `invalid-executor-result`, absent URL and no original/decoded
  fragment. Boolean records its impossible subclass/domain cells as explicit
  N/A.
- Every artifact field uses exact grammar/local boundary/order/outcome; shared
  node and final-byte aggregates are paired below/at/above.
- Focused shared-core/runtime-target/MCP surface passed: `644 passed`.
- Exact full non-live CI command passed: `1414 passed`, coverage `74.09%`.
- Python compilation, strict OpenSpec `36/36`, evidence index, manifest
  working-tree scope and full-tree whitespace checks passed.
- ChangeRail complexity guard reports `297` added production lines against the
  authorized ceiling `301` and the card's stricter cap `300`; no routing,
  lifecycle, authority or wire files changed.
- Exact clean-tree wheel Windows offline proof passed on
  `HISTORICAL-LAB-HOST\\User`, Python `3.13.1`: wheel SHA-256
  `5beb88a1ad77e484c15e12d90fc1f9a5a3d8f77eb5e4bd81961f5309997ba7ec`;
  installed changed-core hashes exactly matched Linux source. Pre/post
  inventory remained zero tracked processes and the same `39` listeners;
  decoded-authority structure, artifact-before-receipt precedence and malformed
  receipt totality passed; only the owned stage was removed and no resources
  remained.
- Evidence index:
  `.runtime/changerail/evidence/oss-04d-r7-implement-positive-core-operation-boundary/index.json`.
- Live 1C, MCP/ScenarioRunner integration, protocol, Docker, host-agent and
  external-action proof are explicitly not applicable to this core-only card.
- Fresh independent review; no failed verdict authorizes publish.

## Result
The positive core operation boundary is implemented from clean published
`main`: immutable application-composed tuple schemas, sealed logical
provenance, context-local exact-scope evidence receipts, closed six-class
reconstruction, fixed-point public documentation URLs, exact artifact
contracts and deterministic structural/final-byte fallbacks. The new
capability is synced and its change archived. Existing MCP, ScenarioRunner,
lifecycle and executor routing remains unchanged for A5/R8.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `implement-qa-mcp-positive-core-operation-boundary`

### Why
The published design and authorization have no runtime implementation on clean
`main`; shared-core executor DTOs still bypass a positive schema and receipt
authority.

### Goal
Implement the immutable positive schema, context-local evidence ledger and
total bounded core normalizer within R7's 300-line production cap.

### Scope
- `qa_mcp.core` schema/provenance/ledger/normalizer primitives, direct tests
  and shared-core extension documentation.
- Test-first Linux matrix and exact-source Windows offline proof.
- No MCP/ScenarioRunner routing, lifecycle, live 1C, protocol or external
  action.

### Acceptance
- All card acceptance and exact R5-R2 matrix cells pass through the direct core
  API with fixed complete outcomes.
- Added production LOC is at most 300 and A4's exact bounded authorization is
  accepted by preflight.
- Specs are synced, the change is archived and a fresh independent review is
  required before publish.

### Depends On
- Published R5-R2 and A4.

### Related
- `openspec/changes/implement-qa-mcp-positive-core-operation-boundary/`

## Log
- 2026-08-26 recreated by R5-R2 as the clean positive-schema core successor.
- 2026-08-26 fast-forward produced one apply-ready bounded core change with
  intended-oracle RED, exact Linux/Windows offline verification and no public
  route integration.
- 2026-08-26 moved to `3.inprogress`; started test-first delivery.
- 2026-08-26 retained exact RED/GREEN, focused `406`, full non-live `1176` at
  `74.09%`, 292-line complexity, strict validation and exact-source Windows
  offline proof; synced the capability and archived the change for fresh
  independent review.
- 2026-08-26 independent review cycle 1 returned `NO-GO`: URL controls exposed
  only by the fourth decode or stripped by `urlsplit` were admitted. Bounded
  rescue 1 adds original/final-state control checks and exact adversarial cells.
- 2026-08-26 rescue 1 passed direct `368`, focused `604`, full non-live `1374`
  at `74.09%` and an exact-source Windows matrix of 198 C0/DEL cells; remote
  source hashes matched and the owned stage was removed with exact inventory
  preservation. Prepared fresh review cycle 2.
- 2026-08-26 independent review cycle 2 confirmed R1 closed but returned
  `NO-GO`: decoded authority delimiters could be reparsed/discarded, and
  receipt validation preceded artifact-local fields. Bounded rescue 2 adds
  structural-equivalence and Cartesian artifact-before-receipt oracles.
- 2026-08-26 rescue 2 passed direct `408`, focused `644`, full non-live `1414`
  at `74.09%`; exact-source Windows proof covered 20 decoded-authority
  structure cells, 12 artifact/receipt precedence cells and malformed receipt
  totality. Local/remote hashes matched and exact owned-stage cleanup preserved
  the zero-process/39-listener inventory. Prepared final review cycle 3.
- 2026-08-26 independent review cycle 3 returned `GO`: all `9/9` acceptance
  checks passed with zero findings and zero unbacked claims; rescue budget closed
  at `2/2`.
- 2026-08-26T10:58:32Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
