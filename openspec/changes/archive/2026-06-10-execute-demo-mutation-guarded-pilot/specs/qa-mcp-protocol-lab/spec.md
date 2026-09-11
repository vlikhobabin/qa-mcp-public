## ADDED Requirements

### Requirement: Real demo mutation execution is guarded by manifest and pre-state
The protocol lab SHALL execute real demo mutation rows only when a reviewed
manifest row matches the current runtime target and pre-state.

#### Scenario: Reviewed row executes
- **WHEN** a real demo mutation row is complete, recoverable, scoped to the
  disposable demo10413 lab and the active form, target marker and pre-state
  match the manifest
- **THEN** the guarded pilot may execute the reviewed action
- **AND** the run records pre-state, action-start, action-end, post-state and
  recovery or cleanup phase evidence

#### Scenario: Execution gate fails
- **WHEN** the manifest is missing, incomplete, unrecoverable, externally
  side-effecting or the live pre-state does not match the reviewed row
- **THEN** the guarded pilot records a blocked or rejected summary without
  executing the action
- **AND** no accepted mapping output is produced for that row

#### Scenario: Live runtime preflight fails
- **WHEN** the live runtime preflight for the selected runtime route fails
  before any 1C process is started or attached
- **THEN** the guarded pilot records a `runtime_gap` blocker with the retained
  preflight result before any mutation attempt
- **AND** no 1C process is started, no action executes and no accepted mapping
  output is produced

### Requirement: Real demo mutation recovery is retained for every executed row
The protocol lab SHALL retain cleanup, reset or documented residue evidence for
each real demo mutation row that executes.

#### Scenario: Mutation is recovered
- **WHEN** a real demo mutation action changes or creates demo data
- **THEN** the pilot runs the reviewed recovery or cleanup path
- **AND** final-state evidence records either baseline restoration, removal of
  `QA_MCP_*` data or acceptable residue with owner and residual risk

#### Scenario: Recovery cannot be proven
- **WHEN** recovery markers, cleanup proof or final-state evidence are missing
  after a mutation attempt
- **THEN** the row remains blocked, rejected, partial or candidate
- **AND** the row is not promoted as accepted mutation evidence
