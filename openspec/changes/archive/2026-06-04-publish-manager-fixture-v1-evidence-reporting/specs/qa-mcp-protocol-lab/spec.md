## ADDED Requirements

### Requirement: Manager fixture V1 evidence is reviewed before corpus use

The protocol lab SHALL publish compact reviewed evidence for manager fixture
V1 read-only runs before using those runs as protocol-corpus inputs.

#### Scenario: Manager V1 evidence summary is published

- **WHEN** a manager fixture V1 read-only run is reviewed
- **THEN** the summary records run id, command catalog version, bootstrap
  status, runtime output paths, command counts, failure details and evidence
  owner routes
- **AND** raw TCP streams, full event logs, platform logs and generated replay
  output remain under ignored runtime paths

#### Scenario: Frame join status is reported

- **WHEN** manager side-channel events are compared with proxy traffic
- **THEN** the reviewed report records per-case frame-join status, frame or
  chunk ranges when known, unresolved reason when not known and whether replay
  or direct Python-manager proof exists
- **AND** no command is published as an accepted protocol mapping until frame
  ranges, dynamic fields, normalized hashes and replay or direct-probe status
  support that claim
