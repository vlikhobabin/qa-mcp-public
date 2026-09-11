## ADDED Requirements

### Requirement: V2 safe-action tooling exposes a manager fixture scenario

The protocol lab SHALL provide a `manager-fixture-v2-safe-action` capture
scenario for safe non-mutating manager fixture actions.

#### Scenario: Safe-action scenario requires reviewed rows

- **WHEN** the V2 safe-action capture scenario starts
- **THEN** it requires a reviewed manifest row for every action it will
  capture or execute
- **AND** rows outside the V2 allowlist fail closed before capture begins

#### Scenario: Safe-action scenario records action phases

- **WHEN** the scenario captures a safe UI action
- **THEN** it records pre-read, action, post-read and recovery phase events
- **AND** bootstrap and background refresh traffic remain visible outside the
  action phase

### Requirement: V2 safe-action runtime output stays outside reviewed git

The protocol lab SHALL keep raw safe-action captures, process logs and
generated replay payloads under ignored runtime paths.

#### Scenario: Runtime output is separated from reviewed evidence

- **WHEN** the V2 safe-action scenario writes capture output
- **THEN** raw traffic and generated runtime files stay under
  `runtime/protocol-research/`
- **AND** reviewed git changes contain only compact manifests, summaries or
  evidence links
