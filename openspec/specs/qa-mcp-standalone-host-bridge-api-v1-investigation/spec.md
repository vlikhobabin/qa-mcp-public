# qa-mcp-standalone-host-bridge-api-v1-investigation Specification

## Purpose
TBD - created by archiving change investigate-qa-mcp-standalone-host-bridge-api-v1-boundary. Update Purpose after archive.
## Requirements
### Requirement: Bridge API v1 investigation names one exact successor
The project SHALL bind the standalone bridge API v1 investigation only to
`oss-05-extract-independent-open-windows-host-bridge` at its canonical
`3.inprogress` path.

#### Scenario: Exact successor is inspected
- **WHEN** the investigation decision is read from tracked `4.done` state
- **THEN** its `Blocks` relation names only the OSS-05 successor id
- **AND** a later authorization source must repeat the exact canonical path

### Requirement: Permitted wire scope is narrow
The investigation SHALL permit only public bridge API major `1`, authenticated
capability negotiation, TestClient lifecycle/relay and bounded display/UIA
operations already declared by the archived OSS-05 change.

#### Scenario: Removed private route is considered
- **WHEN** COM, BSL, agent CLI, Team/onboarding, path-probe or generic execution is proposed
- **THEN** it is outside the investigation decision
- **AND** a new investigation is required before such a surface can proceed

### Requirement: Machine ceiling does not expand implementation
The later authorization source SHALL use machine ceiling `301`, while OSS-05
MUST retain its independent at-most-`300` added production LOC gate.

#### Scenario: Authorization source is prepared
- **WHEN** the exact OSS-05 authorization object is created
- **THEN** `production_loc_ceiling` is `301`
- **AND** the successor card still forbids more than `300` added production LOC

### Requirement: Wire authorization is exact and non-reusable
The investigation SHALL permit `allow_new_authority_or_wire_protocol: true`
only for the exact OSS-05 successor and MUST NOT authorize another card, API
major, route family or OSS-06.

#### Scenario: Another successor references the decision
- **WHEN** a different card or path attempts to consume the authorization
- **THEN** deterministic preflight rejects it
- **AND** no complexity or wire-contract exception is granted

### Requirement: Investigation delivery is metadata-only
The investigation SHALL contain no production, test, protocol, runtime or
Windows implementation and SHALL perform no external action.

#### Scenario: Delivery scope is reconciled
- **WHEN** the investigation manifest is checked
- **THEN** every committable path is OpenSpec or board metadata
- **AND** Windows-native, live 1C and test-first runtime checks are recorded as not applicable
