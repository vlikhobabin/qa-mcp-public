## MODIFIED Requirements

### Requirement: Declared paths use one positive outcome partition
The boundary SHALL omit undeclared exact-string keys without inspecting their
values. At a declared path, every wrong class, non-exact built-in type/subclass,
non-member literal or invalid domain SHALL abort the complete reconstruction as
fixed invalid-executor-result, without a partial result or input fragment.
Finite-class test fixtures SHALL remain separate from the production active-window
value schema; changing that production schema MUST NOT weaken class-test or
public error.details reconstruction coverage.

#### Scenario: Same-path literal matrix is exact
- **WHEN** a declared finite-class fixture literal and public error.details.referenceLabel receive exact built-in Reference label 7, another string, path/credential/connection/local-endpoint forms, wrong types or a string subclass
- **THEN** only exact built-in Reference label 7 preserves at each declared path
- **AND** every other declared cell returns the same complete fixed failure without an original fragment.

#### Scenario: Unknown value is not inspected
- **WHEN** an undeclared key contains a value whose access or iteration would raise
- **THEN** reconstruction omits the key and completes without invoking that value.

## ADDED Requirements

### Requirement: Active-window production fields have a finite positive schema
The production read_active_window success schema MUST admit only its documented
observation fields: window_state with exact local literals observed, missing or
ambiguous, marker_count as reference_count and optional assertion_passed as an
exact boolean. It MUST retain immutable source-owned schema authority, trusted
provenance and the existing total structural, scalar, node, byte and artifact
receipt protections. This change MUST NOT authorize arbitrary UI strings.

#### Scenario: Declared active-window fields reject invalid data
- **WHEN** an executor supplies an invalid state literal, wrong field class/subclass, invalid count, malformed result or oversized admitted content
- **THEN** public reconstruction returns the existing complete fixed typed failure
- **AND** no partial value, input fragment or untrusted provenance is emitted.

#### Scenario: Generic reconstruction protection remains covered
- **WHEN** existing finite-class, URL, structural, byte and receipt controls run with explicit test fixtures or declared public error.details paths
- **THEN** their previous exact valid/invalid outcomes and bounds remain enforced
- **AND** no production synthetic operation or caller-supplied schema is introduced.
