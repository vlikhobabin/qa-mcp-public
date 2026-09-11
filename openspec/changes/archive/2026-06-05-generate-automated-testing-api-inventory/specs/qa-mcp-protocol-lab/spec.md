## ADDED Requirements

### Requirement: Automated testing API inventory is reviewed before broad corpus expansion

The protocol lab SHALL keep a compact reviewed inventory of the 1C automated
testing API surface before expanding the manager fixture corpus beyond the
bounded V1 smoke.

#### Scenario: Inventory is generated

- **WHEN** the API inventory is generated from platform help or `help-mcp`
- **THEN** it records the source platform version, object names, aliases,
  members, parameters, return types when available and default safety class
- **AND** it writes a machine-readable JSON artifact under
  `docs/protocol-research/api-inventory/`
- **AND** it writes a compact reviewed summary with counts and known gaps

#### Scenario: Help source is incomplete

- **WHEN** a required automated-testing object or member cannot be resolved
- **THEN** the inventory records an explicit gap with owner route and residual
  risk
- **AND** the missing topic is not treated as unsupported protocol behavior

#### Scenario: Inventory is used for corpus planning

- **WHEN** a later corpus manifest is built from the inventory
- **THEN** inventory labels are treated as semantic planning support
- **AND** accepted protocol mappings still require wire evidence and
  replay/probe proof
