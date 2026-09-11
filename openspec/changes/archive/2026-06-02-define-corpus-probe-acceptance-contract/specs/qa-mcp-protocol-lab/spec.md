## ADDED Requirements

### Requirement: Corpus rows can link direct-probe evidence
The protocol lab SHALL allow reviewed corpus rows to reference compact direct
Python-manager probe evidence without embedding raw probe output.

#### Scenario: Direct-probe result is attached to a corpus row
- **WHEN** a reviewed corpus row uses direct Python-manager probing as replay
  confirmation
- **THEN** the row records or links the compact probe evidence path, probe
  status, probe query or case family and response markers needed for review
- **AND** raw probe output, raw TCP traffic and local process logs remain under
  ignored runtime directories

### Requirement: Accepted read-only mappings require stable wire evidence and probe proof
The protocol lab SHALL promote a read-only corpus row to `accepted` only when
repeated normalized request evidence and replay or direct-probe proof support
the same operation.

#### Scenario: Stable repeated row is promoted
- **WHEN** repeated corpus rows for the same read-only `case_id` have the same
  non-null `normalized_hash`
- **AND** the row has accepted direct-probe or replay evidence for the expected
  operation and response markers
- **THEN** comparison evidence may classify the mapping as a stable accepted
  dictionary entry
- **AND** the accepted row retains capture ids, frame ranges, request/response
  sizes, dynamic fields, operation token, response markers and evidence paths

### Requirement: Direct-probe gaps remain explicit
The protocol lab SHALL keep direct-probe rows with missing request-frame or
hash evidence visible as unresolved evidence instead of promoting them.

#### Scenario: Direct probe returns useful data without reviewed request hash
- **WHEN** direct Python-manager probing returns useful read-only response
  data but the reviewed corpus row lacks request-frame or `normalized_hash`
  evidence
- **THEN** the row remains `partial`, `pending`, `incomplete_hash` or another
  explicit non-accepted status
- **AND** the row records the unresolved reason and the compact evidence path
  needed for the next investigation pass
