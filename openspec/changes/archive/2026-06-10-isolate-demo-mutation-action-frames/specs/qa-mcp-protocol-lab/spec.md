## ADDED Requirements

### Requirement: Real demo mutation action frames are isolated from background traffic
The protocol lab SHALL separate action, background/refresh and recovery frame
ranges before using real demo mutation rows as corpus evidence.

#### Scenario: Action frames are isolated
- **WHEN** a guarded real-demo mutation run has phase events and reviewable
  traffic
- **THEN** the compact evidence records action frame range, background or
  refresh ranges and recovery ranges separately for each attempted row
- **AND** refresh-only or recovery-only traffic is not treated as proof of the
  mutation action

#### Scenario: Frame boundary is ambiguous
- **WHEN** action frames cannot be joined to the manifest row, phase events or
  chunk counters reliably
- **THEN** the row remains `candidate`, `blocked`, `partial`, `timeout` or
  `rejected` with unresolved reason, owner route and residual risk
- **AND** the row is not accepted as protocol knowledge

### Requirement: Real demo mutation rows require proof before accepted status
The protocol lab SHALL require same-action replay, direct Python-manager probe
or accepted typed contract proof before a real demo mutation row is accepted.

#### Scenario: Row is accepted
- **WHEN** a real demo mutation row is published as accepted
- **THEN** it has separated action-frame evidence plus same-action replay,
  direct Python-manager probe or accepted typed contract proof for that action
- **AND** the row retains normalized hash, dynamic-field, operation-token,
  response-marker, recovery and evidence-path details when available

#### Scenario: Proof is missing
- **WHEN** a row has runtime action and recovery evidence but lacks accepted
  replay, direct probe or typed contract proof
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** accepted mapping output excludes the row
