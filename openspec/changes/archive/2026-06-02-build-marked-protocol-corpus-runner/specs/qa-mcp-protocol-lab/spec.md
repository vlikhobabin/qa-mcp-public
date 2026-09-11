## ADDED Requirements

### Requirement: Protocol corpus runner records marked read-only cases
The protocol lab SHALL provide a Windows-native corpus runner that executes
short marked read-only 1C testing API cases and preserves case markers with the
captured TestManager/TestClient traffic.

#### Scenario: Marked corpus case is captured
- **WHEN** the corpus runner executes a read-only active-window, active-form or
  form-element case
- **THEN** the capture output includes case markers sufficient to derive the
  manager-to-client and client-to-manager frame range for that case
- **AND** the capture cleanup records and stops only PIDs created by the run

### Requirement: Corpus runner generates normalized case evidence
The protocol lab SHALL generate compact normalized evidence rows for corpus
cases without committing raw capture streams.

#### Scenario: Corpus evidence is generated
- **WHEN** a corpus capture is analyzed
- **THEN** the runner or analyzer writes a reviewed case row with `case_id`,
  `api_call`, `frame_range`, `normalized_hash`, dynamic fields,
  `operation_token`, `response_markers` and `replay_status`
- **AND** compact reports are linked from `docs/protocol-research/evidence-index.md`
- **AND** raw capture binaries and traffic logs remain under ignored runtime
  directories

### Requirement: Corpus mappings can be confirmed without TestManager
The protocol lab SHALL attempt replay or direct Python-manager confirmation for
corpus mappings whose frame family is supported by existing replay tooling.

#### Scenario: Replay confirmation is attempted
- **WHEN** a corpus case produces a supported read-only request family
- **THEN** the runner records the result of replaying or probing the mapping
  against a live TestClient without a 1C TestManager instance
- **AND** the case row distinguishes accepted mappings from rejected, timeout,
  partial or unsupported mappings
