## ADDED Requirements

### Requirement: Manager fixture V1 case events are joined to proxy traffic

The protocol lab SHALL convert manager fixture V1 side-channel events and TCP
proxy traffic into reviewed per-case join evidence before generating corpus
rows from a live manager harness run.

#### Scenario: Case events are joined

- **WHEN** a manager fixture V1 runtime directory contains `case_events.jsonl`
  and `traffic.jsonl`
- **THEN** the analyzer maps each read-only command to manager and client
  chunk or frame ranges when boundaries are reviewable
- **AND** the join report records the selected ranges, command id, target
  marker and expected marker

#### Scenario: Join is unresolved

- **WHEN** a command lacks events, proxy chunks or unambiguous boundaries
- **THEN** the join report records a precise unresolved reason
- **AND** the command remains non-accepted

#### Scenario: Corpus row is generated

- **WHEN** a command has a reviewed range
- **THEN** the corpus row records frame range, request/response sizes,
  dynamic fields, normalized hash, operation token candidate, response markers
  and replay/probe status
- **AND** raw payloads remain under ignored runtime paths
