## ADDED Requirements

### Requirement: Manager fixture V1 live smoke gates full catalog expansion

The protocol lab SHALL publish a bounded non-dry-run manager fixture V1 smoke
before using the full V1 command catalog for broad read-only protocol corpus
research.

#### Scenario: Live smoke succeeds

- **WHEN** the bounded manager fixture V1 smoke runs against the client fixture
- **THEN** the reviewed evidence records the run id, executed command ids,
  runtime output paths, join report and corpus rows
- **AND** at least one row has a non-null reviewed range, request size,
  response size and normalized hash
- **AND** replay or direct Python-manager proof is attempted when supported

#### Scenario: Live smoke is provider-gapped

- **WHEN** the smoke cannot start because required runtime assets or provider
  capabilities are unavailable
- **THEN** the reviewed evidence records the provider gap, owner route,
  missing evidence type and residual risk
- **AND** no live protocol mapping is accepted from that run

#### Scenario: Full catalog expansion is considered

- **WHEN** the bounded smoke has no joined normalized row
- **THEN** the full V1 command catalog remains blocked
- **AND** the next blocker is recorded in reviewed evidence
