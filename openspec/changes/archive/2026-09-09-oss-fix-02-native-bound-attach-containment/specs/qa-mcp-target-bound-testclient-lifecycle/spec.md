## ADDED Requirements

### Requirement: Bound attach requires observed target provenance
A non-owned project-bound attach MUST require current observation of the actual
process target and binding generation. Endpoint reachability, a PID/port check,
copied configuration or caller-supplied identity SHALL NOT establish that proof.
Missing, mismatched or stale observation MUST produce a typed blocked outcome
before session admission or protocol/UI commands.

#### Scenario: Reachable endpoint has no target observation
- **WHEN** a bound attach sees a reachable TCP endpoint or a listening remote PID/port without current observed target provenance
- **THEN** it returns a blocked result without admitting a session or sending protocol/UI commands
- **AND** previously admitted application state is unchanged

#### Scenario: Declared identity is presented as observation
- **WHEN** a profile copy, caller fingerprint or old owned handle is offered as proof for a new non-owned attach
- **THEN** it is rejected as insufficient current process observation
- **AND** the implementation does not synthesize a trusted observer result

#### Scenario: Supported lifecycle paths remain available
- **WHEN** validated owned launch or explicit unbound attach is used
- **THEN** its existing lifecycle and ownership contract is preserved
- **AND** documentation identifies general non-owned bound attach as unavailable until a reviewed observer supplies the required proof
