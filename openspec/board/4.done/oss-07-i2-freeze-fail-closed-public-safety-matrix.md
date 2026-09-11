# Freeze Fail-Closed Public-Safety Matrix

## Status
4.done

## Owner
unassigned

## Series
oss-07-i2

## Order Index
406.4

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/1.backlog/oss-07-prepare-qa-mcp-public-repository-readiness.md`

## Recovery For
- `OSS-07-I1`, an unpublished public-safety design audit whose cycle-3
  independent review exhausted its same-card rescue budget. The predecessor
  card path and nine-path dirty payload are not present in this clean baseline
  and MUST NOT be invented, restored, copied or reconstructed by I2.

## Source Lineage
- Latest safe published reference: `10598ef`
  (`10598ef201fd5afe4b0a9fdf110a6e0fb7bace24`).
- Fresh cycle-3 reviewed dirty-payload fingerprint from the separate I1
  workspace: `HEAD 10598ef201fd5afe4b0a9fdf110a6e0fb7bace24`, tree
  `e33a2d16a853bae7c3aaf43bbaf55f9e18d40b91`, diff
  `sha256:4446213a7ef51486ee957324e24fe9148d9cd2b33829ef70a31064dcfc74d38b`.
- Canonical verdict SHA-256:
  `bc958dfee622ef892879beb0f4d5a70da3a239368a033ff834715541db2e1f3a`.
- Review-history SHA-256:
  `53a81bfbf00f580843b001427e233763c716e59389fd2f4fb85d147a5a6d3292`.
- The verdict and history remain in another workspace. I2 retains only these
  immutable digests and the concise findings below; it does not claim a copied
  runtime evidence path.
- Review cycle `3`: one blocker; acceptance `1`, `2` and `4` failed while `3`,
  `5` and `6` passed. Same-card rescue budget limit `2`, used `2`, remaining
  `0`, exhausted `true`; I1 cannot receive another same-card rescue and cannot
  publish.

## Prior Review Findings
- Unresolved `R1` class: the v3 public-safety matrix remains false-PASS-capable
  because `P`/`S` row labels are only range-checked; the wrapper does not
  assert the exact expected RED results `46/14/5/D14`; `D12` is treated as
  executed from mere string presence; `G18` does not prove that the original
  eligible-email bytes reach every non-email rule; and the `audit_design.py`
  helper bytes are not hash-bound.
- Unbacked claim: eligible-email original bytes reach every non-email rule.
- Unbacked claim: the matrix enforces the semantic exact `P`/`S` mapping.
- Unbacked claim: the matrix is byte-identical and false-pass-resistant.
- Cycle-2 `R2` and `R3` are closed. Cycle-2 `R1` is only partially closed and
  remains the sole blocker carried into I2.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Lineage rationale: predecessor I1 repeated the partially closed cycle-2/
  cycle-3 R1 false-PASS class and exhausted its same-card rescue budget.
- Investigation trigger: I2 is the required bounded design/investigation
  artifact for that predecessor lineage, not another implementation rescue.
- Live admission: `no`
- Final certification: `no`
- Linked-card investigation/simplification authority is the exhausted I1
  cycle-3 verdict/history state recorded above; no published complexity
  exception is declared or required.

## Summary
Create a small offline design/investigation successor that freezes one exact
successor-owned executable public-safety matrix and its audit helper, binds
their bytes, and defines fail-closed per-row outcomes. The investigation must
prove that semantic-label, expected-RED, `D12` execution, `G18` original-byte
flow or helper-byte mutations make verification fail before any broader
OSS-07 implementation resumes.

## Current Hypothesis
I1's false PASS is caused by an oracle that validates shapes and marker text
instead of independently binding executable bytes, exact row semantics and
observed control/data flow. A minimal immutable matrix contract plus an outer
hash-and-result oracle should close the class without restoring I1's payload or
changing production or test source.

## Acceptance
- I2 defines one canonical, successor-owned matrix with an explicit stable row
  identity, exact per-row `P`/`S` semantic label and exact expected result; set
  membership, range checks or self-reported labels are insufficient.
- A tracked freeze record binds the exact matrix bytes and the exact
  successor-owned audit-helper bytes with lowercase SHA-256 digests. The outer
  verifier checks both digests before execution and rejects absent, extra,
  duplicate, reordered, relabeled or otherwise changed rows.
- The outer verifier asserts the exact reviewed RED result tuple
  `46/14/5/D14`; it neither infers expected values from actual output nor
  accepts mere count ranges, marker presence or a helper-reported aggregate.
- `D12` has an execution-only receipt tied to the exact row and control-flow
  path. Source/string presence without that receipt fails, and a mutation that
  bypasses `D12` produces a non-zero verification result.
- `G18` proves with byte-level receipts that the same original eligible-email
  bytes reach every canonical non-email rule before rule evaluation. A
  normalization, replacement, truncation or per-rule omission mutation fails.
- The mutation matrix independently changes a row label, each expected RED
  result/count including `D14`, `D12` execution, `G18` original-byte flow and
  the audit helper itself while the trusted oracle remains unchanged; every
  mutation must fail and the unmodified control must pass.
- Structured context is limited to a documented allowlist of stable typed
  fields. Unknown, missing, duplicate, untyped or prose-derived context fails
  closed and cannot alter row selection or expected outcomes.
- The investigation produces only the exact successor-owned design/freeze/
  offline-verifier surface declared by its OpenSpec artifacts. It does not
  restore or recreate the I1 nine-path payload, change production or test
  source, create license files, expand public-release scope or touch OSS-08.
- The operator-approved license remains exactly SPDX `Apache-2.0`; I2 records
  that inherited constraint without choosing another license or implementing
  the broader OSS-07 licensing/governance payload.
- The inherited offline verification floor, strict OpenSpec validation,
  whitespace/untracked-file checks and a fresh independent critical review all
  pass before I2 may publish. No Windows, SSH, 1C, TestClient, live runtime,
  Apache service or network work is permitted.

## Change Set
1. `freeze-fail-closed-public-safety-matrix` -
   `openspec/changes/archive/2026-09-02-freeze-fail-closed-public-safety-matrix/`

## Dependencies
- Latest safe published reference `10598ef`.
- Immutable I1 verdict/history digests and concise cycle-3 findings recorded in
  this card; no predecessor runtime path or dirty-payload restoration.

## Blocks
- `OSS-07-I1` remains unpublished and exhausted; I2 is its only authorized
  continuation.
- `openspec/board/1.backlog/oss-08-publish-qa-mcp-github-ghcr-release-train.md`
  remains blocked until OSS-07 public-readiness work is delivered. I2 does not
  authorize or modify OSS-08.

## Verify
- `python3 tools/protocol-research/oss07_i2/verify_matrix.py --run-mutations`:
  control passed with exact `46/14/5/D14`; all 23 hostile semantic, result,
  D12, G18, helper-byte, topology and context cases returned non-zero with the
  expected class.
- Each of the four `red-*` cases now changes the helper-observed aggregate and
  per-row value while canonical matrix/freeze/oracle bytes remain unchanged;
  an isolated regression probe removing the outer observed-result comparison
  made those four cases unexpected and the suite exit non-zero.
- The simplified `audit_design.py` and `verify_matrix.py` contain 74 and 208
  lines respectively, 282 combined against the ChangeRail ceiling of 300.
- JSON parsing and in-memory Python compilation passed for the exact matrix,
  freeze, helper and verifier sources.
- Exact successor scope, reserved-fixture/public-safety and `Apache-2.0` scans
  passed; no production, test, baseline-card or OSS-08 path is present.
- `bin/openspec validate "freeze-fail-closed-public-safety-matrix" --strict`
  passed before archive; the synced capability and `bin/openspec validate
  --all --strict` passed after archive with 67/67 items.
- `git diff --check` and an isolated temporary-index `git diff --cached
  --check` passed while the real index remained empty.
- Retained command evidence:
  `.runtime/changerail/evidence/oss-07-i2-freeze-fail-closed-public-safety-matrix/index.json`.
- Fresh independent ChangeRail review at critical risk. Retained I1 hashes are
  lineage, not a reusable positive verdict; this review is pending.

## Archive
- `openspec/changes/archive/2026-09-02-freeze-fail-closed-public-safety-matrix/`

## Related
- `openspec/board/1.backlog/oss-07-prepare-qa-mcp-public-repository-readiness.md`
- `openspec/board/1.backlog/oss-08-publish-qa-mcp-github-ghcr-release-train.md`
- `openspec/changes/archive/2026-09-02-freeze-fail-closed-public-safety-matrix/`

## Result
Implementation, hostile-mutation proof, spec sync and archive completed from
the exact safe baseline. The five-file successor surface closes only the
retained R1 design class; I1 remains unpublished and OSS-08 remains blocked.
Publication is pending a fresh independent critical `GO`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `freeze-fail-closed-public-safety-matrix`

### Why
I1's v3 oracle remained false-PASS-capable after two same-card rescues because
it did not independently bind exact bytes, row meanings, RED outcomes or
observed D12/G18 flow.

### Goal
Produce one clean-room, successor-owned, byte-frozen offline matrix and
independent hostile-mutation proof that closes only the retained R1 class.

### Scope
- Create exactly the five design-declared curated evidence/verifier files plus
  this card's OpenSpec delivery/archive state.
- Bind exact ordered `P`/`S` row semantics, `46/14/5/D14`, D12 execution, G18
  original bytes, helper bytes and the structured-context allowlist.
- Preserve `Apache-2.0`, the inherited offline verification floor and fresh
  independent critical review.
- No I1 payload restore/reconstruction, production/tests, baseline OSS-07 or
  roadmap edits, OSS-08, Windows, SSH, 1C, live, Apache-service or network work.

### Acceptance
- Every top-level card criterion and delta requirement passes with exact
  command-bound evidence.
- The unchanged control passes and every required semantic/byte/control-flow/
  data-flow/context mutation fails with its named class.
- Exact scope, strict OpenSpec, whitespace/untracked and public-safety checks
  pass before a fresh independent critical review.

### Depends On
- Safe published reference `10598ef` and the immutable exhausted I1 lineage
  recorded in this card; no predecessor files or runtime evidence paths.

### Related
- `openspec/changes/archive/2026-09-02-freeze-fail-closed-public-safety-matrix/`

## Log
- 2026-09-02T20:26:17Z linked I2 successor created from the immutable I1
  cycle-3 `NO-GO` summary after same-card rescue budget `2/2` was exhausted.
- 2026-09-02T20:26:17Z accepted into `2.todo` with one apply-ready offline
  design/investigation change; no implementation, review or publication ran.
- 2026-09-02T20:38:43Z delivery started from exact safe published reference
  `10598ef201fd5afe4b0a9fdf110a6e0fb7bace24`; only the I2 card, OpenSpec
  lifecycle state and five successor-owned offline files are in scope.
- 2026-09-02T20:48:40Z offline control passed and all 23 hostile mutations
  failed closed with their exact expected classes; JSON/Python, exact-scope,
  public-safety, strict OpenSpec and temporary-index whitespace gates passed.
- 2026-09-02T20:51:24Z delta requirements synced to the new main capability
  spec and the completed change archived; Windows, SSH, 1C, live, Apache
  service and network work remained explicitly not applicable and were not run.
- 2026-09-02T21:08:15Z authorized pre-review simplification reduced the two
  research tools from 812 to 282 added lines while preserving the exact frozen
  contract; helper/freeze/verifier hashes, the full offline gate, retained
  evidence and the same 12-path manifest handoff were refreshed.
- 2026-09-02T21:14:34Z fresh independent critical review cycle 1 returned
  `NO-GO`: blocker R1 found the four RED cases changed matrix declarations
  rather than bad helper-observed results; minor R2 found two historical failed
  evidence attempts with success-worded summaries.
- 2026-09-02T21:18:16Z same-card rescue attempt 1 redirected the same four
  named RED cases through frozen helper output faults without changing the
  23-case count or expected classes; the regression probe now fails as required
  and the two historical evidence summaries were corrected in ignored state.
- 2026-09-02T21:32:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
