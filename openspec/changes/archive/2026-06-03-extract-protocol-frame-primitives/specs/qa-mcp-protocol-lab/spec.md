## ADDED Requirements

### Requirement: Protocol frame primitives live in the package
The protocol lab SHALL provide package-owned primitives for rendering and
summarizing accepted read-only TestClient protocol frames.

#### Scenario: Template frame is rendered offline
- **WHEN** package code renders a captured manager-frame template with dynamic
  ACK GUID, sequence, nonce or managed-form values
- **THEN** the rendered payload and replacement metadata are returned without
  opening a network socket
- **AND** the replacement metadata records field name, offset, length,
  original bytes and replacement value

### Requirement: Capture bootstrap loading is reusable
The protocol lab SHALL expose reusable package code for reading the captured
bootstrap frames required before generated read-only UI queries.

#### Scenario: Bootstrap fixture is loaded
- **WHEN** package code loads a curated bootstrap fixture or approved capture
  source
- **THEN** it separates manager-to-client and client-to-manager frames
- **AND** it rejects incomplete bootstrap data with a clear error
- **AND** tests do not require raw ignored runtime captures unless a live
  operator explicitly supplies them

### Requirement: Dynamic field behavior is fixture-tested
The protocol lab SHALL verify package frame/template primitives with offline
fixtures before they are used by live TestClient sessions.

#### Scenario: Dynamic replacements are inspected
- **WHEN** offline tests render a template frame twice with different dynamic
  values
- **THEN** expected dynamic field locations change
- **AND** preserved semantic fields remain visible rather than being silently
  normalized away
