## ADDED Requirements

### Requirement: Successor retains exhausted lineage without restoring payload
I2 MUST bind the latest safe published reference, reviewed dirty-payload
fingerprint, canonical verdict/history SHA-256 digests, exact cycle-3 blocker
summary and rescue budget state. It MUST NOT invent a predecessor path, claim
copied runtime evidence or restore, copy or reconstruct the unavailable I1
nine-path payload.

#### Scenario: Clean baseline admits the linked investigation
- **WHEN** the safe reference is `10598ef`, the retained verdict/history
  digests match the card and I1 rescue budget is `2/2` with zero remaining
- **THEN** I2 may author only its successor-owned design/freeze/verifier surface
  and MUST keep I1 unpublished

#### Scenario: Predecessor bytes are requested
- **WHEN** delivery would require an unavailable I1 file, runtime path or
  payload reconstruction
- **THEN** I2 MUST stop without inventing or importing that input

### Requirement: Matrix bytes and semantic rows are independently frozen
The successor verifier SHALL require deterministic matrix bytes, unique stable
row identities in exact order, exact per-row `P`/`S` semantic labels and exact
expected outcomes. A freeze record SHALL bind exact byte size and lowercase
SHA-256 for the matrix and `audit_design.py`, and the verifier SHALL bind the
exact freeze-record bytes independently of the helper.

#### Scenario: Canonical control is unchanged
- **WHEN** matrix, helper and freeze bytes match their trusted digests and every
  row matches the verifier's exact ordered semantic table
- **THEN** byte and row admission SHALL pass before helper results are accepted

#### Scenario: Row semantics are relabeled
- **WHEN** any `P`/`S` label is changed while a range or set-membership check
  would still accept it
- **THEN** the verifier MUST return a named non-zero semantic-row failure

#### Scenario: Matrix or helper bytes change
- **WHEN** one byte of the canonical matrix or `audit_design.py` differs
- **THEN** the verifier MUST reject the payload before trusting its aggregate
  result

### Requirement: Exact reviewed RED results are an external oracle
The outer verifier MUST contain and assert the exact ordered RED result tuple
`[46, 14, 5, "D14"]`. It MUST NOT derive expected values from actual helper or
matrix output, accept ranges or marker presence, or substitute a helper-reported
aggregate for per-row evidence.

#### Scenario: Exact RED tuple is observed
- **WHEN** the approved helper emits structured results for the canonical
  matrix
- **THEN** the verifier SHALL accept the aggregate only when it is exactly
  `46/14/5/D14` and every per-row result also matches

#### Scenario: One expected RED member changes
- **WHEN** any of `46`, `14`, `5` or `D14` is independently changed, omitted,
  reordered or inferred from actual output
- **THEN** the verifier MUST return a named non-zero expected-result failure

### Requirement: D12 execution is observed rather than inferred
`D12` SHALL count as executed only when the approved row-execution path emits a
structured receipt containing the current run nonce, exact row identity and
input digest. Source text, a string marker or an aggregate count MUST NOT prove
execution.

#### Scenario: D12 executes through the canonical callback
- **WHEN** the canonical D12 path runs and emits its bound execution receipt
- **THEN** the verifier SHALL record D12 as executed exactly once

#### Scenario: D12 marker remains but execution is bypassed
- **WHEN** a hostile mutation leaves the `D12` string present but bypasses its
  row-execution callback
- **THEN** the verifier MUST return a named non-zero D12-execution failure

### Requirement: G18 preserves original eligible-email bytes for every non-email rule
The matrix SHALL use the exact synthetic bytes `eligible@example.invalid` and
record their hex, length and SHA-256. Before each canonical non-email rule is
evaluated, the helper SHALL emit one receipt proving that rule received those
same original bytes; the verifier MUST require the exact rule set once each.

#### Scenario: Original bytes reach every non-email rule
- **WHEN** each canonical non-email rule receives the unchanged eligible-email
  bytes before evaluation and emits its rule-bound receipt
- **THEN** the verifier SHALL accept G18 byte flow for the complete exact set

#### Scenario: One rule receives changed or no bytes
- **WHEN** normalization, decoding/re-encoding, replacement, truncation,
  omission or post-rule instrumentation changes one rule's receipt
- **THEN** the verifier MUST return a named non-zero G18 original-byte-flow
  failure

### Requirement: Structured context and mutations fail closed
The helper context MUST allow only `schema`, `run_nonce`, `matrix_sha256`,
`helper_sha256` and `eligible_email_sha256` with exact documented primitive
types and formats. The successor verifier SHALL run an unchanged control and
independent hostile mutations of row labels, every RED tuple member, D12
execution, G18 byte flow, helper bytes and row topology while its trusted
oracle remains unchanged.

#### Scenario: Structured context is exact
- **WHEN** the context contains every allowlisted field once with its exact
  type and value and contains no other field
- **THEN** helper execution MAY proceed without changing row selection or
  expected outcomes

#### Scenario: Structured context is invalid
- **WHEN** a field is missing, extra, duplicate, mistyped, prose-derived or
  attempts to provide a path, command, credential, user data or expected-result
  override
- **THEN** verification MUST fail before helper execution

#### Scenario: Hostile matrix is complete
- **WHEN** the successor mutation mode runs every required mutation against
  owned temporary copies and the unmodified control
- **THEN** every hostile case MUST fail with its expected class, the control
  MUST pass and only the owned temporary directory may be removed

### Requirement: Investigation remains offline and successor-only
I2 MUST modify no production or test source and MUST create only the five
successor-owned files declared in its design plus card/OpenSpec workflow state.
It MUST preserve SPDX `Apache-2.0`, keep OSS-08 blocked and run no Windows, SSH,
1C, TestClient, live MCP, Apache service, capture, replay, network or external
side-effect work. Publication requires the inherited offline verification floor
and a fresh independent critical review of the exact payload.

#### Scenario: Exact design investigation completes
- **WHEN** the five-file surface passes its control/mutation oracle, exact scope
  and public-safety checks, strict OpenSpec validation and whitespace checks
- **THEN** it may enter fresh independent critical review without claiming
  broader OSS-07 or OSS-08 completion

#### Scenario: Scope or environment expands
- **WHEN** delivery would modify production/tests/baseline cards, choose a
  license other than `Apache-2.0`, touch OSS-08 or require a prohibited runtime
- **THEN** I2 MUST stop and require a separately authorized card
