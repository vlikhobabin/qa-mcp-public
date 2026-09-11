## ADDED Requirements

### Requirement: V4 scenarios recover to the baseline
The protocol lab SHALL prove that every V4 warning, question, modal,
expected-error and bounded-wait scenario can return to the V1 baseline through
documented recovery markers.

#### Scenario: Dialog scenario recovers
- **WHEN** a V4 dialog or modal scenario completes, is cancelled or fails
- **THEN** the recovery path reads the V4 marker set after cleanup
- **AND** the marker set matches the documented baseline or a documented
  candidate-only residual state

#### Scenario: Wait scenario recovers after cancel or retry
- **WHEN** a V4 bounded wait scenario is cancelled, retried or times out
- **THEN** recovery evidence records the cleanup path and final wait markers
- **AND** the fixture can run the same scenario again after reset

### Requirement: V4 recovery evidence separates phase ranges
The protocol lab SHALL keep V4 dialog/action, background, expected-error and
recovery evidence ranges separate before any V4 row is promoted.

#### Scenario: Capture review labels V4 phases
- **WHEN** a V4 scenario publishes compact reviewed evidence
- **THEN** the report identifies pre-read, action-or-dialog, result,
  background and recovery phases where those phases exist
- **AND** unresolved or ambiguous ranges remain candidate, blocked or rejected
  rather than accepted

### Requirement: V4 expected errors require matching diagnostics
The protocol lab SHALL classify a V4 expected-error row as expected only when
the controlled diagnostic marker matches the reviewed scenario contract.

#### Scenario: Diagnostic mismatch fails closed
- **WHEN** a V4 expected-error row returns an unreviewed diagnostic or missing
  marker
- **THEN** the row is classified as infrastructure failure, rejected or blocked
- **AND** the recovery path must still restore the fixture baseline before
  another case runs
