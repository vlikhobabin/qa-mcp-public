# OSS-07-I2 Fail-Closed Public-Safety Matrix Findings

## Boundary and lineage

This successor-only investigation started from exact safe published reference
`10598ef201fd5afe4b0a9fdf110a6e0fb7bace24`. The baseline tree contains no path
matching `audit_design.py`, an OSS-07-I1 marker, or this successor matrix. No
predecessor runtime path was resolved and no byte from the unavailable I1
nine-path payload was restored, copied, inferred or reconstructed.

The retained I1 state is lineage only:

- reviewed dirty tree: `e33a2d16a853bae7c3aaf43bbaf55f9e18d40b91`;
- reviewed dirty diff:
  `sha256:4446213a7ef51486ee957324e24fe9148d9cd2b33829ef70a31064dcfc74d38b`;
- canonical verdict SHA-256:
  `bc958dfee622ef892879beb0f4d5a70da3a239368a033ff834715541db2e1f3a`;
- review-history SHA-256:
  `53a81bfbf00f580843b001427e233763c716e59389fd2f4fb85d147a5a6d3292`;
- cycle 3 acceptance outcomes: 1, 2 and 4 failed; 3, 5 and 6 passed;
- one remaining R1 false-PASS blocker; same-card rescue budget 2/2 used,
  zero remaining, exhausted.

The only policy choice carried forward is SPDX `Apache-2.0`. This work created
no license, governance, release, production or test payload and did not touch
OSS-08.

## Frozen sources

The exact successor sources are:

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| `matrix.json` | 865 | `0de299bc935d3f7d9ac8aa3f855b0bead62f0249ed5e44e6db7c05f4bfa26ec3` |
| `audit_design.py` | 4259 | `1356bd4c954fb5178d009bd28e1c031ecef9ab46db90bcc61619c03d7d335cbc` |
| `freeze.json` | 534 | `fbfba8abdc249f152a9e5270d78933e463d53cae351efdf88502bf974979c884` |
| `verify_matrix.py` | 15594 | `cd2ed10c512c10a494c7072f34df18540438040910303582c9ed5decfa7ea0f2` |

`freeze.json` binds the matrix and helper byte size and digest. The outer
verifier embeds the freeze-record digest and independently embeds the exact
ordered rows `P46/P/46`, `S14/S/14`, `D12/P/5`, `G18/S/D14`, the literal RED
tuple `46/14/5/D14`, and the original eligible-email byte identity. The fresh
ChangeRail payload fingerprint and critical review bind the outer verifier and
this report.

The bounded pre-review simplification preserves this contract in 282 combined
added lines (`audit_design.py` 74, `verify_matrix.py` 208), below the
ChangeRail 300-line complexity ceiling.

## Control and hostile mutations

Command:

```text
python3 tools/protocol-research/oss07_i2/verify_matrix.py --run-mutations
```

Observed outcome: the unchanged control returned zero with exact RED result
`46/14/5/D14`; all 23 hostile cases returned non-zero and the independently
expected failure class.

The four `red-*` cases keep the canonical matrix, freeze and oracle bytes
unchanged while the frozen helper emits one wrong observed aggregate/per-row
value. Removing the outer observed-result comparison makes those four cases
unexpected and the suite non-zero, so they directly guard that oracle.

| Mutation | Expected class | Observed class |
| --- | --- | --- |
| `semantic-label-P46` | `semantic_rows` | `semantic_rows` |
| `red-46` | `expected_red` | `expected_red` |
| `red-14` | `expected_red` | `expected_red` |
| `red-5` | `expected_red` | `expected_red` |
| `red-D14` | `expected_red` | `expected_red` |
| `d12-bypass-marker-retained` | `d12_execution` | `d12_execution` |
| `g18-changed-before-P46` | `g18_original_bytes` | `g18_original_bytes` |
| `g18-omit-before-S14` | `g18_original_bytes` | `g18_original_bytes` |
| `helper-one-byte` | `helper_sha256` | `helper_sha256` |
| `row-add` | `row_topology` | `row_topology` |
| `row-remove` | `row_topology` | `row_topology` |
| `row-duplicate` | `row_topology` | `row_topology` |
| `row-reorder` | `row_topology` | `row_topology` |
| `context-missing` | `context` | `context` |
| `context-extra-unknown` | `context` | `context` |
| `context-duplicate` | `context` | `context` |
| `context-untyped` | `context` | `context` |
| `context-prose-derived` | `context` | `context` |
| `context-path` | `context` | `context` |
| `context-command` | `context` | `context` |
| `context-credential` | `context` | `context` |
| `context-user-data` | `context` | `context` |
| `context-expected-override` | `context` | `context` |

Every case used a separate verifier-owned temporary directory or an isolated
runtime fault against unchanged frozen files. Cleanup removed only that owned
temporary directory. No raw runtime log or generated mutation payload was
retained; the two reserved-domain fixture literals remain only in reviewed
source.

## R1 closure mapping

- Exact semantic mapping is backed: the oracle compares ordered row identity,
  label and typed expected result against constants outside the matrix; label,
  and topology mutations fail before helper output can be trusted, while each
  observed result mutation fails the independent aggregate/per-row comparison.
- Exact result and byte identity are backed: the oracle asserts the literal
  `46/14/5/D14`, verifies matrix/helper/freeze digests, and rejects a one-byte
  helper change.
- D12 and G18 flow are backed: D12 requires the one nonce- and row-bound
  `row_callback` receipt. Each canonical non-email rule requires one receipt
  for the same 24 original `eligible@example.invalid` bytes with SHA-256
  `4aa460464f7b5a72e497da3759deaa0aa0e962be8d587663d65f056c4292da15`
  before rule evaluation. Bypass, change and omission controls fail.

The helper accepts only `schema`, `run_nonce`, `matrix_sha256`,
`helper_sha256` and `eligible_email_sha256`, with exact string types and
formats. Invalid context fails before matrix row selection and callback
execution.

## Verification boundary

This is synthetic Linux-offline design evidence. Windows-native verification
is not applicable and was not run. SSH, 1C, TestClient, Vanessa, live MCP,
Apache service, capture, replay and network work are also not applicable and
were not run. The report makes no claim about production or test behavior,
broader OSS-07 completion, I1 publishability or OSS-08 admission.
