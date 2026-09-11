## ADDED Requirements

### Requirement: Certification binds exact published product and test bytes
I13 MUST prove before and after the matrix that all five I11 product/test blobs
equal the final lineage recorded by published I11 and that none of those paths
differs from commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.

#### Scenario: Bound source is exact
- **WHEN** all five blob identities and the path-diff gate match published I11
- **THEN** execution preflight may continue.

#### Scenario: Any bound byte differs
- **WHEN** a blob or path differs before or after a row
- **THEN** certification stops as `BLOCKED` without accepting that row.

### Requirement: The exact-source matrix is complete and row-distinct
Certification SHALL pass one exact S3 control, two fresh tracked run-1 S4 rows,
one uninstrumented S4 confirmation and two run-distinct S5 rows for the required
platform version with no source change between rows. S3/S4 MUST produce zero
action. Each S5 row MUST use exactly one published S5-R1 hidden-desktop-local
addressed confirmation with no retry, forbidden/global input or extra action.

#### Scenario: Every matrix row passes
- **WHEN** all six isolated rows use the exact fixture and argv identities and
  produce their required bounded outcomes and exact `0/0/0/0/1/1` action counts
- **THEN** the matrix may proceed to marker and cleanup certification.

#### Scenario: A row is skipped unavailable or fails
- **WHEN** any required row is skipped, cannot run or produces a nonconforming
  outcome
- **THEN** the matrix is not certified and the card stops fail-closed.

### Requirement: Marker evidence is passive stable and privacy-safe
Every applicable row MUST contain exactly one matching marker hash in both
passive samples with unchanged topology, and all applicable rows MUST agree on
the one frozen marker hash. Raw UI text, OCR, screenshots and visual
punctuation MUST NOT be retained or used.

#### Scenario: One marker is stable
- **WHEN** both samples in every applicable row contain one identical marker
  hash and topology remains exact
- **THEN** that privacy-safe hash may be frozen in the retained receipt.

#### Scenario: Marker or topology differs
- **WHEN** a marker is missing, duplicated or different, or topology changes
- **THEN** certification fails without deriving a replacement from raw UI.

### Requirement: Exact restoration and owned cleanup are part of each row
I13 MUST restore exact configuration bytes, ACL and required metadata and
remove only the current row's exact-owned task, stage, process/job/desktop and
transport state after every row. A second cleanup pass MUST be a no-op and
unrelated fingerprints MUST remain unchanged.

#### Scenario: Cleanup is exact and rerun-safe
- **WHEN** a row ends in success or failure and both cleanup assertions match
  the before-image with no foreign removal
- **THEN** the next isolated row may start.

#### Scenario: Cleanup is incomplete or foreign
- **WHEN** before-image restoration differs, owned residue remains or unrelated
  state changes
- **THEN** certification stops and retains a bounded cleanup failure receipt.

### Requirement: Certification has no implementation authority
I13 MUST change no product/test source and MUST add no public API, route, wire
field, runtime authority, retry, fallback or wait. Its only action authority is
the published S5-R1 one-addressed-confirmation contract for each of the two S5
rows; every other row and rejected path MUST produce zero action and no extra
external side effect.

#### Scenario: Behavior or access blocks certification
- **WHEN** execution access is unavailable or published behavior fails a row
- **THEN** I13 records `BLOCKED` or `NOT-VERIFIABLE` and requires a separately
  authorized investigation rather than modifying code.

### Requirement: Evidence enters fresh critical review
Certification MUST retain bounded row/source/marker/topology/cleanup evidence,
pass offline regression, deterministic unexecuted cross-builds, strict workflow
and privacy/license gates, and obtain a fresh critical review before publish.

#### Scenario: Review handoff is complete
- **WHEN** every mandatory receipt and verification command is bound to the
  unchanged payload and deterministic preflight is ready
- **THEN** a fresh independent critical reviewer may evaluate the card.
