## ADDED Requirements

### Requirement: Protocol corpus cases have normalized evidence rows
The protocol lab SHALL define reviewed corpus case evidence as normalized rows
that map one marked 1C testing API operation to its protocol frame range,
dynamic fields, request/response signatures and replay status.

#### Scenario: Corpus case row is recorded
- **WHEN** a marked protocol case is promoted to reviewed evidence
- **THEN** the evidence row includes `case_id`, `api_call`, `frame_range`,
  request and response sizes, dynamic field descriptions, `normalized_hash`,
  response markers and `replay_status`
- **AND** the row references a compact evidence path under
  `docs/protocol-research/evidence/`
- **AND** raw capture payloads remain under ignored runtime directories

### Requirement: Protocol mappings require replay or probe status
The protocol lab SHALL record replay or Python-manager probe status before a
corpus mapping is treated as working protocol knowledge.

#### Scenario: Mapping is classified as accepted
- **WHEN** a corpus row claims that a 1C testing API operation maps to a
  protocol request shape
- **THEN** the row records whether replay or direct Python-manager probing
  accepted, rejected, partially accepted or timed out for that mapping
- **AND** missing replay evidence is visible as a non-accepted status

### Requirement: Semantic metadata does not replace wire evidence
The protocol lab SHALL treat help, metadata and EDT evidence as semantic
enrichment for corpus rows, not as sufficient proof of native protocol behavior.

#### Scenario: Metadata is linked to a corpus row
- **WHEN** a corpus row includes semantic labels from platform help, metadata or
  EDT tooling
- **THEN** the row still references capture and normalization evidence for the
  protocol claim
- **AND** the row identifies semantic metadata as supporting context rather than
  replay proof
