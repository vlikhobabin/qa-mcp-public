## ADDED Requirements

### Requirement: Exhaustive per-file redistribution ledger
The repository SHALL maintain a deterministic manifest containing every
Git-visible bundled protocol asset, protocol UI asset and curated evidence file
exactly once with path, size, lowercase SHA-256, provenance class,
redistribution decision and rationale.

#### Scenario: Manifest matches the tree
- **WHEN** provenance verification recomputes the declared roots
- **THEN** the canonical manifest bytes match and no path is missing, extra,
  duplicated or digest-mismatched

#### Scenario: Unsupported binary is present
- **WHEN** an in-scope packaged artifact lacks source-complete provenance or an
  explicit redistribution basis
- **THEN** it is absent from the public snapshot and provenance verification
  fails if it reappears

### Requirement: Fail-closed disclosure audit
The audit SHALL scan paths and bytes for every Git-visible file for
high-confidence credentials, personal/customer markers, private lab endpoints
and prohibited artifacts. It SHALL additionally decode structured Base64
protocol fields such as JSON/JSONL `payload_b64` and inspect raw, UTF-8 and
UTF-16 views. It MUST report only category/path/source/count and MUST return
non-zero for an unallowlisted finding. Malformed structured payloads and invalid
declared Base64 MUST fail closed. Any public fixture exception MUST bind one
exact category, repository-relative path, source, matched byte value and
occurrence count; directory-wide and whole-file exemptions are prohibited.

#### Scenario: Public tree is clean
- **WHEN** the audit runs against the reviewed working tree
- **THEN** it returns zero without emitting credential or matched-value bytes

#### Scenario: Secret-like value is introduced
- **WHEN** a non-fixture private key, service token or credential assignment is
  added to a Git-visible path
- **THEN** the audit returns non-zero and reports only its safe category and
  repository-relative path

#### Scenario: Disclosure is introduced under tests or beside a fixture
- **WHEN** a lowercase credential, private endpoint or other disclosure is
  added under `tests/` or to a path containing an allowed public fixture value
- **THEN** the audit returns non-zero unless that exact
  category/path/source/value/count tuple is allowlisted

#### Scenario: Structured payload cannot be completely inspected
- **WHEN** a JSON/JSONL line is malformed or a declared Base64 field is invalid
- **THEN** the audit returns non-zero with a safe parse/decode category while
  continuing to inspect independently valid lines

#### Scenario: Disclosure is encoded in a protocol payload
- **WHEN** a token, customer name or machine identity is present only in a
  structured Base64 payload, including UTF-16 bytes
- **THEN** the audit decodes it, returns non-zero and does not emit the value

### Requirement: Historical evidence keeps meaning without private identity
Sanitized historical evidence SHALL preserve the tested topology, operation,
version and result while removing personal account, customer and routable
private-lab identity. Reserved historical labels SHALL be documented as
redactions rather than presented as runnable accounts, hosts, products or
paths.

#### Scenario: Historical report is sanitized
- **WHEN** a report formerly named a lab account, customer or private endpoint
- **THEN** it uses a reserved documentation identity and the technical outcome
  remains unchanged

### Requirement: I2 oracle gates provenance admission
The audit and provenance write/check commands SHALL run the published OSS-07-I2
hostile-mutation verifier and MUST fail if its frozen byte, semantic, D12, G18,
result or context contracts drift. Provenance write/check MUST also fail before
admission when the policy or disclosure scan has any finding.

#### Scenario: I2 bytes or outcome drift
- **WHEN** the I2 verifier detects any reviewed mutation class or frozen-byte
  mismatch
- **THEN** the public audit returns non-zero before a provenance PASS
