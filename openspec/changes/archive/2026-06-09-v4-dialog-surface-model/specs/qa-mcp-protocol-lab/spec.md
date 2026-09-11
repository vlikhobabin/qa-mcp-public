## ADDED Requirements

### Requirement: V4 dialog surfaces expose deterministic markers
The protocol lab SHALL expose warning, question and fixture-owned modal-form
surfaces through deterministic fixture-local `PF_*` markers before those
surfaces are captured or promoted.

#### Scenario: Fixture opens with V4 dialog baseline
- **WHEN** the V4 fixture surface is opened before any dialog scenario runs
- **THEN** read-only inspection can observe baseline markers for dialog family,
  lifecycle state, expected text, selected result and recovery state
- **AND** the baseline markers state that no dialog is currently active

#### Scenario: Dialog marker set names expected text
- **WHEN** a V4 warning, question or modal-form scenario is selected for
  implementation
- **THEN** the scenario declares stable expected text markers that can be
  compared in pre-state, result and recovery evidence

### Requirement: V4 dialog scenarios are classified before execution
The protocol lab SHALL classify every V4 dialog candidate before runtime
execution as fixture-local, mutation-like or special-recovery, with explicit
non-business safety constraints.

#### Scenario: Unsafe dialog candidate fails closed
- **WHEN** a V4 dialog candidate lacks a target marker, expected text marker,
  bounded lifetime, `mutates_business_data=false` or recovery expectation
- **THEN** the candidate is rejected before capture or manager-runner execution
- **AND** the rejection is routed to a later targeted card instead of broad V4
  delivery
