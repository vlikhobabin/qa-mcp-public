## ADDED Requirements

### Requirement: Client fixture V1 targets are mapped before corpus capture
The protocol lab SHALL publish a compact target map for V1 fixture elements
before using those elements as read-only corpus targets.

#### Scenario: Target map records fixture markers
- **WHEN** the V1 target map is published
- **THEN** each mapped row includes a `PF_*` marker, element family, target path, expected state and expected response markers
- **AND** each row identifies whether the target is supported, pending, partial or blocked

#### Scenario: Target map links to corpus intent
- **WHEN** a V1 fixture target is intended for read-only corpus capture
- **THEN** the target map links the target to planned case ids or manifest rows
- **AND** the target map records semantic sources as supporting context rather than protocol proof

#### Scenario: Target map does not promote protocol mappings
- **WHEN** target-map evidence exists without capture and replay/probe evidence
- **THEN** the related corpus rows remain non-accepted
- **AND** accepted mappings still require frame ranges, normalized hashes, dynamic fields and replay or direct Python-manager status
