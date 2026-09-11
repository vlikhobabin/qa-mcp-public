## MODIFIED Requirements

### Requirement: Full-local evidence requires a current exact-scope receipt
Each application SHALL own a ledger with frozen evidence root/policy. A
full-local artifact path SHALL require a current same-ledger, same-operation,
same-artifact receipt for an existing canonical non-symlink path strictly below
the exact built-in platform `Path` root. Sanitized output SHALL never emit a
path and executor-returned path/provenance/schema data SHALL grant no authority.

#### Scenario: Concurrent and stale authority fails closed
- **WHEN** overlapping contexts/scopes exchange receipts, a scope closes or raises, a receipt/root/policy/path is forged or mutated, or a `Path` subclass/symlink/outside path is supplied
- **THEN** only a current exact-scope authoritative record can emit a full-local path
- **AND** every other case returns a fixed typed failure without changing another scope

#### Scenario: Receipt scalar boundary is exact
- **WHEN** otherwise valid canonical receipt paths contain 2,047, 2,048 and 2,049 Unicode scalars
- **THEN** the first two remain eligible and 2,049 returns fixed `invalid-evidence-receipt`

The shared operation SHALL accept artifact authority only from current trusted
production, bound to application, scope, canonical path and actual content digest.
Raw executor references SHALL NOT create records. Explicit low-level trusted
recording SHALL bind the actual file hash. Full-local normalization SHALL reject
changed bytes, mismatched artifact hash, stale path or symlink before success.
Sanitized current production SHALL remain verifiable after owned raw-file deletion.
Local artifact type/size validation SHALL retain priority over receipt failures.

#### Scenario: Old-file and false-hash result claims
- **WHEN** an untrusted executor returns a pre-existing in-root file, a false well-formed hash or metadata without current trusted production
- **THEN** the shared result is non-success with the exact applicable fixed artifact/receipt failure and discloses no path
- **AND** the pre-existing file is unchanged

#### Scenario: Current bytes determine receipt validity
- **WHEN** trusted current evidence is changed, redirected through a symlink or returned with mismatching hash before normalization
- **THEN** the operation fails closed with no current artifact disclosure
- **AND** valid current full-local evidence retains its exact readable path and actual digest
