## ADDED Requirements

### Requirement: Python protocol package contract is evidence-aware
The protocol lab SHALL expose read-only `qa_mcp.protocol` package contracts
that distinguish accepted mappings from unresolved protocol probes.

#### Scenario: Package operation descriptors are reviewed
- **WHEN** package code exposes a read-only TestClient operation descriptor
- **THEN** the descriptor records `case_id`, operation family, safety class,
  acceptance status and evidence path
- **AND** accepted descriptors retain the accepted normalized hash and source
  capture or comparison evidence
- **AND** unresolved descriptors retain an explicit reason such as
  `incomplete_hash`, `pending`, `partial` or `unsupported`

### Requirement: Package contract preserves the read-only boundary
The protocol lab SHALL keep promoted Python manager package APIs limited to
read-only TestClient operations until action/write evidence is accepted.

#### Scenario: Candidate operation can mutate UI or business data
- **WHEN** a package operation would click, input text, execute a command or
  mutate business data
- **THEN** it is excluded from the read-only protocol package contract
- **AND** the operation is routed to a later safe-action or mutation-specific
  card

### Requirement: Package contract is offline verifiable
The protocol lab SHALL make the package contract importable and testable from
committed compact evidence without requiring a live 1C runtime.

#### Scenario: Contract tests run without TestClient
- **WHEN** offline package tests inspect the read-only operation contract
- **THEN** accepted active-window and active-form mappings can be verified
  against committed compact evidence
- **AND** raw captures, raw probe output and process logs are not required
