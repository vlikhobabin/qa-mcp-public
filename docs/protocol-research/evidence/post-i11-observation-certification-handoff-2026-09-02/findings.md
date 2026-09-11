# Post-I11 Observation Certification Handoff

## Decision

Published commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`
closes the private main-predicate equivalence implementation defect and its
offline proof floor. It does not complete S4-R1 because I11 explicitly excludes
the exact-source S3/S4/S5 matrix, stable marker derivation and exact cleanup
observations required by the parent.

S4-R1 therefore remains blocked. The exact next card is I13:

`openspec/board/2.todo/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md`

I13 is certification-only. It starts from the unchanged published I11
product/test bytes and may retain evidence, but it has no authority to change
product or test code. Missing access, source drift, a failed row or incomplete
cleanup is a fail-closed stop for a separately authorized investigation.

## Published Identity

- Local `HEAD`: `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.
- `origin/main`: `964e29fa7ee8ba87df12d0db903ca7a331113c2f` over
  credential-free HTTPS with repository-local `!gh auth git-credential`.
- I11 card: tracked `4.done`.
- I11 archive:
  `openspec/changes/archive/2026-09-02-enforce-main-predicate-equivalence-contract/`.
- I11 synced capability:
  `openspec/specs/qa-mcp-main-predicate-equivalence-enforcement/spec.md`.

## Parent Acceptance Map

| Criterion | Classification | Published closure | Remaining evidence |
| --- | --- | --- | --- |
| Preserve S1-R1 through S3 and S5-R1/S6 while changing only the S4 seam | `remaining_certification` | I11 is limited to five private product/test paths, 259 added production LOC and no public/wire surface; focused/full tests, vet, repository coverage and deterministic cross-builds passed. | Exact-source S3 and run-distinct S5 rows must prove preservation for the published bytes. |
| Deterministic hidden desktop and observation-thread hold across transfer, both inventories and both passive samples | `remaining_certification` | I11 preserves predecessor calls, fences, sleeps and two-sample ordering in connected offline oracles. | Fresh exact-source S4 rows must prove the hold and both samples. |
| Inventory errors fail closed without unproved retry, sentinel or added assignment success | `closed_offline` | Published enforcement requires `exact`/`absent`/`invalid`, exact replay consumption, no extra membership operation and no cause for invalid or ambiguous state. | No additional classifier implementation is authorized; certification must still show the unchanged path behaves as published. |
| Derive and freeze the tracked marker from privacy-safe passive hash evidence | `remaining_certification` | I11 explicitly adds no marker derivation. | Two stable passive samples must supply the exact privacy-safe marker hash before the marker can be frozen. |
| Pass exact S3, two tracked S4 runs, one uninstrumented S4 confirmation and two run-distinct S5 rows | `remaining_certification` | I11 passes only offline tests and deterministic unexecuted cross-builds. | The entire named exact-source matrix remains unexecuted for the published I11 bytes. |
| Restore exact configuration bytes, ACL and metadata and remove only exact-owned state after every row | `remaining_certification` | I11 creates no external state, so its offline cleanup is not evidence for the parent matrix. | Each certification row needs before/after identity plus exact restoration and owned-cleanup proof. |
| Keep S7 blocked until S4-R1 review and publication | `preserved_block` | S7 remains blocked in the board and roadmap. | The block remains until I13 and then S4-R1 are independently reviewed and published. |

## I13 Evidence Boundary

I13 binds the five I11 product/test blobs recorded in the published I11 card
and proves no drift from commit `964e29f`. It runs only the parent-required
exact-source control/certification rows and retains public-safe row identities,
source hashes, marker hashes, outcomes, exact action counts and cleanup
summaries. S3/S4 remain zero-action; each S5 row inherits published S5-R1
authority for exactly one addressed confirmation with zero forbidden/global
input. Raw private text, screenshots and broad diagnostic dumps are excluded.

The required rows are:

1. exact S3 control;
2. two fresh tracked run-1 S4 rows;
3. one uninstrumented S4 confirmation;
4. two run-distinct S5 rows;
5. exact restoration and exact-owned cleanup after every row.

A positive outcome requires the same tracked fixture and argv to reach one
stable marker match in both passive samples on each applicable row. Any missing
main, inventory error, marker mismatch, topology drift, nonzero child failure
or incomplete cleanup remains a hard failure.

## Scope And Verification

I12 changes documentation and OpenSpec state only. Execution and test-first RED
evidence are not applicable to this decision payload because it changes no
behavior. Verification consists of strict OpenSpec validation, exact JSON
schema/value checks, parent/roadmap/I13 graph checks, docs/OpenSpec-only scope,
public-safety and license preservation, plus tracked and untracked whitespace
checks. No external execution or contact is part of I12.
