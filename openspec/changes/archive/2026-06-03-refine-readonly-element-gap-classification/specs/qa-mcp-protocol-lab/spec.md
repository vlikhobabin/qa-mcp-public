## ADDED Requirements

### Requirement: Element hash classification records precise unresolved reasons
The protocol lab SHALL classify useful read-only element hash gaps with
reviewable reason values that identify the next actionable blocker.

#### Scenario: Request frames are missing
- **WHEN** a useful element probe has response or direct-probe evidence but no
  reviewed manager-to-client request frame slice
- **THEN** classification evidence records the row as non-accepted with
  `missing_request_frames` or an equivalent stable reason

#### Scenario: Operation join is ambiguous
- **WHEN** probe evidence cannot be joined to a single reviewed operation
  shape, frame range or response marker set
- **THEN** classification evidence records the row as non-accepted with
  `ambiguous_operation_join` or an equivalent stable reason

#### Scenario: Normalizer coverage is incomplete
- **WHEN** request frames exist but dynamic fields cannot be normalized into a
  stable reviewed hash
- **THEN** classification evidence records the row as non-accepted with
  `incomplete_normalizer_coverage` or an equivalent stable reason

### Requirement: Element rows are accepted only with stable reviewed hashes
The protocol lab SHALL keep useful element direct-probe rows out of accepted
mapping output until stable reviewed request hashes and replay or direct-probe
proof support the same operation.

#### Scenario: Probe succeeds without complete wire evidence
- **WHEN** `form-element-details` or `typed-input-field-readonly` returns
  useful direct Python-manager data
- **BUT** repeated reviewed inputs do not provide a stable non-null normalized
  hash for the same operation
- **THEN** the row remains non-accepted and the classification report records
  the unresolved reason

#### Scenario: Stable wire evidence and probe proof match
- **WHEN** repeated reviewed inputs provide a stable non-null normalized hash
  and accepted replay or direct-probe evidence for the same element operation
- **THEN** classification evidence may mark the row accepted and retain the
  evidence fields required by the corpus evidence contract
