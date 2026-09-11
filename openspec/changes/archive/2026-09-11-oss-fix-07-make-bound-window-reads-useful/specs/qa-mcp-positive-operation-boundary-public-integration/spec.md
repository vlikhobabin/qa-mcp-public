## ADDED Requirements

### Requirement: Multi-session active-window assertions precede public projection
For bound read_active_window steps, ScenarioRunner.run MUST evaluate the requested
expected-window predicate at the trusted internal read seam before public
projection, then use its admitted boolean for StepResult assertion/status.
It MUST preserve the shared operation's route admission, selected executor,
provenance and non-success verdict behavior without retry or native fallback.

#### Scenario: Real default handler supports matching and mismatching assertions
- **WHEN** an admitted local or Windows-host default handler returns actual ActiveWindowContext through the shared MCP operation or ScenarioRunner.run
- **THEN** the safe observation agrees across those paths
- **AND** a requested actual window match passes while mismatch/missing/ambiguous fails, using one native read and no echoed raw window data.

#### Scenario: Bound assertion serialization remains private
- **WHEN** the trusted read or expected predicate contains private strings or the read fails
- **THEN** serialized operation and StepResult preview/error fields omit raw UI, reference, expected-string, credential and physical-path fragments
- **AND** successful matching does not require searching the normalized public preview.

#### Scenario: Declared compatibility remains deliberate
- **WHEN** an intentionally unbound direct or multi-session read uses its established contract
- **THEN** its useful legacy DTO/assertion behavior remains available
- **AND** this change does not claim default single-session BDD delivery or widen live authority.
