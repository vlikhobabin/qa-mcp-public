## Context

I11 is published at `964e29fa7ee8ba87df12d0db903ca7a331113c2f`
with five final product/test blob identities recorded in its done card. Its
offline connected oracles prove closed predicate semantics and unchanged
predecessor call/control behavior, but I11 never executes the parent-required
exact-source matrix.

I13 is an evidence-only certification. It uses the existing ignored native test
harnesses for S3 control, S4 observation and S5 comparison against the required
platform version. There is no protocol capture or replay traffic. Retained
dynamic fields are limited to public-safe source hashes, row ids, bounded
outcomes, action counts/results, topology hashes, marker hashes and cleanup booleans; raw UI
text, screenshots, credentials, paths, process/window identities and broad
logs remain excluded.

## Goals / Non-Goals

**Goals:**

- Prove the exact published I11 bytes before and after every row.
- Obtain two-sample stable marker evidence from the complete S3/S4/S5 matrix.
- Prove zero action for passive S3/S4 and exactly one published addressed
  confirmation per S5 row with no forbidden/global input.
- Prove exact restoration and exact-owned cleanup after every row and on rerun.
- Retain enough bounded evidence for fresh critical independent review.

**Non-Goals:**

- Changing product/test code, fixtures or target identity.
- Adding diagnostics, retries, fallbacks, waits, authority, public surface or
  any action beyond the exact two S5-R1 certification confirmations.
- Treating skipped, unavailable, partially cleaned or source-drifted rows as
  certification.
- Resuming downstream work or finalizing the parent inside I13.

## Decisions

### 1. Bind certification to product/test blob identity

Before any row, compare the five I11 product/test blobs to the final lineage in
the published card and prove no change in those paths from commit `964e29f`.
Repeat the comparison after the matrix. Documentation commits after I11 are
allowed; changes to any bound product/test byte are not.

Alternative: bind only the current branch commit. Rejected because planning and
evidence documentation necessarily follow I11 while product identity must stay
exact.

### 2. Use one preflight followed by six isolated rows

Preflight proves the exact platform version, required fixture identities,
configuration before-image including bytes/ACL/metadata, source blobs and an
uncontended execution surface. The rows are exact S3, tracked S4 run A, tracked
S4 run B, uninstrumented S4, S5 run A and S5 run B. Each row uses an isolated
owned identifier and completes cleanup before the next begins.

S3/S4 rows are passive and MUST record zero action. Each S5 row inherits the
published S5-R1 contract and MUST perform exactly one hidden-desktop-local
addressed Return key-down/key-up confirmation after exact re-admission, with no
retry, global input, visible-desktop interaction or additional side effect.

Alternative: reuse one long-running stateful session. Rejected because row-
distinct evidence and cleanup recovery would be ambiguous.

### 3. Derive the marker only from passive hashed rows

Both passive samples in every applicable S4/S5 row must contain exactly one
matching privacy-safe marker hash under unchanged topology. A candidate marker
is frozen only when all applicable rows agree. Visual punctuation, OCR,
screenshots and raw UI text are not evidence.

Alternative: preselect a human-readable marker. Rejected because it breaks the
parent's privacy and derivation contract.

### 4. Make cleanup part of every row's verdict

Capture configuration bytes, ACL and required metadata before the matrix.
After each row, restore them exactly and remove only the row's owned task,
stage, process/job/desktop and transport state. Preserve unrelated fingerprints
and repeat the cleanup assertion after a second no-op cleanup pass.

Alternative: cleanup once after the matrix. Rejected because a failed early row
could contaminate later evidence.

### 5. Stop instead of repairing

Unavailable access, invalid preflight, source drift, any failed/skipped row,
unstable marker, topology drift or incomplete cleanup produces `BLOCKED` or
`NOT-VERIFIABLE`. I13 may update only evidence/docs/OpenSpec state and must
create or request a separately authorized investigation for any defect.

## Risks / Trade-offs

- [Evidence is bound to different bytes] -> Enforce before/after five-blob and
  path-diff gates.
- [Rows influence one another] -> Use isolated owned ids and exact cleanup
  between every row.
- [Private UI data leaks] -> Retain hashes/counts/bounded outcomes only and run
  a privacy scan before review.
- [A failed row becomes an implementation staircase] -> I13 has explicit zero
  implementation authority and stops for investigation.

## Migration Plan

1. Run the fail-closed source/fixture/config/execution preflight.
2. Run S3, two tracked S4, one uninstrumented S4 and two distinct S5 rows with
   exact per-row action counts and cleanup after each.
3. Validate stable marker/topology, source identity, privacy and rerun cleanup.
4. Rerun offline regression, deterministic unexecuted cross-builds and strict
   workflow gates.
5. Archive only a complete evidence-backed result and obtain fresh critical
   review. No runtime migration or rollback exists; cleanup restores the exact
   before-image after every row.

## Open Questions

None. Any unavailable prerequisite or failed assertion is a typed stop rather
than discretion to widen I13.
