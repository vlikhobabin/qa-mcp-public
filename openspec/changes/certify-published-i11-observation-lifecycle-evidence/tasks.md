## 1. Prove Source And Execution Preconditions

- [ ] 1.1 Verify the five I11 product/test blob ids equal the published final
  lineage and `git diff --quiet 964e29f -- <five-bound-paths>` passes before
  any execution row.
- [ ] 1.2 Run the exact-source preflight for required platform version, tracked
  fixtures, argv identity, uncontended execution surface and configuration
  bytes/ACL/all required metadata before-image; stop on any mismatch.
- [ ] 1.3 Create isolated exact-owned row ids and retained evidence locations;
  record unrelated protected fingerprints before the matrix.

## 2. Run The Exact Certification Matrix

- [ ] 2.1 Run exact S3 with `go test . -run
  '^TestHiddenWindowIsolationRealTestClientNative$' -count=1`, retain the
  bounded receipt and complete exact restoration/owned cleanup twice.
- [ ] 2.2 Run `TestHiddenDirectObservationNative` twice as fresh tracked S4
  run-1 rows and once through the uninstrumented S4 confirmation path, with
  row-distinct zero-action receipts and exact cleanup after each.
- [ ] 2.3 Run `TestHiddenPromptS5Native` in two distinct fresh rows using the
  same published source/fixture identity and published S5-R1 addressed-action
  contract; retain exactly one confirmation action per row, zero forbidden or
  global input, the bounded post-state, and exact cleanup after each.

## 3. Certify Marker Privacy And Cleanup

- [ ] 3.1 Prove both passive samples in every applicable row contain exactly
  one identical privacy-safe marker hash with unchanged topology; freeze only
  the one hash shared by all rows.
- [ ] 3.2 Prove exact configuration bytes/ACL/metadata restoration, zero
  exact-owned residue, no foreign removal and unchanged protected fingerprints
  after every row and after each no-op cleanup rerun.
- [ ] 3.3 Run retained-evidence schema/privacy checks and record `BLOCKED` or
  `NOT-VERIFIABLE` instead of modifying code when any source, access, row,
  marker, topology or cleanup assertion fails.

## 4. Offline Regression Review And Archive

- [ ] 4.1 Run focused/full Go tests and vet, repository Linux not-live coverage
  and deterministic unexecuted amd64/386 cross-build pairs against unchanged
  I11 product/test bytes.
- [ ] 4.2 Run strict change/capability/all OpenSpec, exact source/matrix/
  evidence/manifest graph, public-safety, Apache-2.0 and tracked-plus-untracked
  whitespace gates; repeat the five-blob identity check.
- [ ] 4.3 Sync the certification capability, archive only a complete evidence-
  backed result, leave I13 in `3.inprogress` and obtain a fresh critical review
  before scoped publication.
