## ADDED Requirements

### Requirement: Manager fixture V1 pending rows are classified before promotion
The protocol lab SHALL classify every pending manager fixture V1 read-only row
from a reviewed cleanup run before accepting the row, changing its manifest
expectation or using it to unblock later action research.

#### Scenario: Pending row classification is published
- **WHEN** a manager fixture V1 cleanup report contains joined non-accepted rows
- **THEN** the protocol lab records a classification for each pending row
- **AND** the classification links the cleanup run id, case id, frame range,
  normalized hash, expected marker, observed marker evidence and replay/probe
  state

#### Scenario: Classification does not promote a row
- **WHEN** a pending row has joined frame evidence but no matching replay or
  direct-probe proof
- **THEN** the row remains non-accepted
- **AND** the classification records the next evidence needed for promotion

#### Scenario: Manifest correction is evidence-gated
- **WHEN** a pending row appears to use a too-strict or wrong expected marker
- **THEN** the protocol lab records a candidate manifest correction
- **AND** the correction is not treated as accepted protocol knowledge until
  replay or direct-probe evidence validates the corrected semantics
