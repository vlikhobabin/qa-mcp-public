# qa-mcp operation evidence boundary design

## Purpose

Define the trusted/untrusted data split, total public serialization, structured
field and URL admission, route fail-closed rules and bounded successor
authorization required before the exhausted OSS-04D operation-identity work can
resume.

## Requirements

### Requirement: Exact exhausted-lineage investigation
The project SHALL retain an exact, secret-free investigation of both exhausted
operation-identity implementation lineages before another runtime successor is
started.

#### Scenario: Investigation traces final findings
- **WHEN** the design payload is reviewed
- **THEN** it identifies both final payload fingerprints, rescue budgets, final findings and retained evidence locations
- **AND** it classifies each finding by root cause and invariant rather than only by reproduced spelling or address
- **AND** any recovery source is mapped to its actually reconstructed tree without implying that a checkpoint is the final reviewed payload

### Requirement: Trusted and untrusted operation data are separated
The boundary design SHALL assign core-trusted provenance and
executor-controlled content to separate admission channels and SHALL define
total typed serialization for every emitted public field.

#### Scenario: Executor result is treated as hostile content
- **WHEN** a successor receives value, error, artifact or forged provenance data from an executor
- **THEN** only validated core provenance can be emitted as provenance
- **AND** executor content is reconstructed through bounded serializers without executing arbitrary callbacks

#### Scenario: Exceptional input cannot escape
- **WHEN** mapping iteration, key conversion, field access, sequence traversal or unknown object handling raises
- **THEN** the design requires a stable typed public failure or redacted sentinel
- **AND** no raw exception, attribute, traceback or input fragment is exposed

### Requirement: Field and URL admission is structured
The design SHALL use anchored semantic field names and structured URL/address
classification, preserving declared public metadata without treating arbitrary
matching tokens as sensitive or public.

#### Scenario: Benign reference metadata is preserved
- **WHEN** a public result contains `referenceCount`, `referenceLabel` or `documentationReference`
- **THEN** the design classifies those exact controls as non-connection metadata
- **AND** does not create a generic `reference` token exception

#### Scenario: Private or credential-bearing URL is rejected
- **WHEN** a documentation URL contains userinfo or a non-global IPv4/IPv6 host in any admitted textual form
- **THEN** structured parsing and address classification reject the route
- **AND** the public result contains no credential or private host fragment

#### Scenario: Legacy numeric host cannot fall through to DNS
- **WHEN** strict IP parsing rejects a one-to-four-component decimal, octal or hexadecimal numeric host such as `127.1`, `0177.0.0.1` or `0x7f.1`
- **THEN** a bounded numeric-host grammar rejects it before DNS admission
- **AND** ordinary alphabetic public documentation hosts and canonical global IP controls remain admissible

#### Scenario: Public documentation alias is admitted
- **WHEN** an explicitly registered documentation URL field contains a valid public HTTP or HTTPS URL without userinfo
- **THEN** the design preserves a canonical bounded documentation reference
- **AND** URL admission does not authorize arbitrary route fields

### Requirement: Artifact, error and route policy is closed
The design SHALL cover every artifact and error scalar, sealed `full_local`
path admission, and fail-closed route admission before Local or Windows
executor invocation.

#### Scenario: Sanitized artifact has no bypass scalar
- **WHEN** any direct or bound artifact scalar contains a secret, path or malformed value under `sanitized`
- **THEN** the design requires the scalar to be rejected or redacted
- **AND** artifact paths remain absent

#### Scenario: Full-local path requires core seal and containment
- **WHEN** an artifact requests `full_local` path disclosure
- **THEN** the design requires both an unforgeable core seal and resolved containment inside the approved evidence root

#### Scenario: Asymmetric session state blocks before adapter
- **WHEN** exactly one of current session or attachment is missing for a project-bound request
- **THEN** the design requires a blocked verdict with zero Local and Windows adapter calls

### Requirement: Investigation produces bounded successor authorization
The investigation SHALL create an ordered implementation successor and a
separate exact authorization source because the repeated defect class and
required typed boundary exceed ordinary patch-rescue policy.

#### Scenario: Successor chain is explicit
- **WHEN** this investigation is published
- **THEN** the roadmap places an exact authorization card before one named implementation successor
- **AND** the authorization ceiling is at most 500 production lines with no new authority or wire protocol
- **AND** OSS-04E remains blocked until that implementation successor publishes with fresh independent GO

### Requirement: Investigation remains design-only
The investigation SHALL NOT modify production runtime code, reapply a failed
payload or claim live/Windows behavior from documentation-only verification.

#### Scenario: Design payload is verified
- **WHEN** the investigation reaches review
- **THEN** its manifest contains only documentation, OpenSpec and board paths
- **AND** verification uses lineage, consistency, strict OpenSpec, diff and independent design review evidence
