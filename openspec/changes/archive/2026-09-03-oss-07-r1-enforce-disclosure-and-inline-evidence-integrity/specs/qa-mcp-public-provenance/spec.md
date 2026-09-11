## MODIFIED Requirements

### Requirement: Exhaustive per-file redistribution ledger
The repository SHALL maintain a deterministic manifest containing every
Git-visible bundled protocol asset, protocol UI asset and curated evidence file
exactly once with path, size, lowercase SHA-256, provenance class,
redistribution decision and rationale. Before admission, every structured
curated evidence row that declares Base64 payload bytes with a byte count or
SHA-256 SHALL be validated against the decoded current payload; an inconsistent
or wrongly typed declaration MUST fail audit and provenance.

#### Scenario: Manifest matches the tree
- **WHEN** provenance verification recomputes the declared roots
- **THEN** the canonical manifest bytes match and no path is missing, extra,
  duplicated or digest-mismatched

#### Scenario: Unsupported binary is present
- **WHEN** an in-scope packaged artifact lacks source-complete provenance or an
  explicit redistribution basis
- **THEN** it is absent from the public snapshot and provenance verification
  fails if it reappears

#### Scenario: Inline payload declaration is inconsistent
- **WHEN** a curated JSON/JSONL row's declared byte count or SHA-256 does not
  match its decoded current Base64 payload bytes
- **THEN** audit and provenance return non-zero with a safe integrity category
  and do not expose payload or digest values

### Requirement: Fail-closed disclosure audit
The audit SHALL scan paths and bytes for every Git-visible file for
high-confidence credentials, personal/customer markers, private lab endpoints
and prohibited artifacts. It SHALL recognize case-insensitive password-key
suffixes with identifier prefixes consistently in quoted JSON, YAML and
environment/assignment syntax, including uninterrupted camel-case identifier
prefixes such as `databasePassword`. Every non-empty supported assignment value
MUST be detected without imposing a minimum secret length. It SHALL additionally decode structured Base64
protocol fields such as JSON/JSONL `payload_b64` and inspect raw, UTF-8 and
UTF-16 views. Every declared `*_b64` value MUST be a valid Base64 string; a
wrongly typed, malformed or undecodable declaration MUST fail closed while
independently valid JSONL lines continue to be inspected. The audit MUST report
only category/path/source/count and MUST return non-zero for an unallowlisted
finding. Any public fixture exception MUST bind one exact category,
repository-relative path, source, matched byte value and occurrence count;
configured and observed multiplicities MUST be equal, so both excess matches
and unused allowance capacity fail. This equality SHALL be reconciled globally
after scanning the complete configured allowance multiset, including configured
paths that are absent and configured sources replaced by another source type.
Directory-wide and whole-file exemptions are prohibited.

#### Scenario: Public tree is clean
- **WHEN** the audit runs against the reviewed working tree
- **THEN** it returns zero without emitting credential or matched-value bytes

#### Scenario: Secret-like value is introduced
- **WHEN** a non-fixture private key, service token or prefixed/unprefixed
  credential assignment is added in JSON, YAML or environment syntax to a
  Git-visible path
- **THEN** the audit returns non-zero and reports only its safe category and
  repository-relative path

#### Scenario: Disclosure is introduced under tests or beside a fixture
- **WHEN** a lowercase credential, private endpoint or other disclosure is
  added under `tests/` or to a path containing an allowed public fixture value
- **THEN** the audit returns non-zero unless that exact
  category/path/source/value/count tuple is allowlisted

#### Scenario: Fixture allowance count is not exact
- **WHEN** an allowed matched value occurs either more or fewer times than the
  configured category/path/source/value/count tuple
- **THEN** the audit returns non-zero without exposing that matched value

#### Scenario: Allowlisted path or source disappears
- **WHEN** an allowlisted path is absent or its configured raw source is
  replaced by a symlink/source of another type
- **THEN** global allowance reconciliation returns non-zero for the unused
  configured path/source capacity without exposing the matched value

#### Scenario: Structured payload cannot be completely inspected
- **WHEN** a JSON/JSONL line is malformed or a declared Base64 field is invalid
  or not a string
- **THEN** the audit returns non-zero with a safe parse/decode/type category
  while continuing to inspect independently valid lines

#### Scenario: Disclosure is encoded in a protocol payload
- **WHEN** a token, customer name or machine identity is present only in a
  structured Base64 payload, including UTF-16 bytes
- **THEN** the audit decodes it, returns non-zero and does not emit the value
