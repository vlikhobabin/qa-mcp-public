## ADDED Requirements

### Requirement: Windows installer renders durable bridge registration

The delivered Windows host-agent installer SHALL accept the complete bridge
registry identity, credential-file, advertised-endpoint, heartbeat and TTL
inputs as one all-or-nothing set, SHALL render them into the fixed scheduled
task for a verified executable, and SHALL preserve solo mode when the complete
set is absent.

#### Scenario: Complete bridge registration inputs are supplied

- **WHEN** the operator installs a verified artifact with registry URL, user,
  registry token file, bridge token file, advertised endpoint, heartbeat and
  TTL
- **THEN** the scheduled-task action contains the corresponding fixed
  `registry-*` flags
- **AND** the host-agent reports registered state through its authenticated
  health contract.

#### Scenario: Partial bridge registration inputs are rejected

- **WHEN** any registry input is supplied without the complete required set
- **THEN** the installer fails before copying the executable or replacing the
  scheduled task
- **AND** no credential value is printed.

#### Scenario: Registry inputs are absent

- **WHEN** the installer receives no registry inputs
- **THEN** it omits every `registry-*` task flag
- **AND** the installed host-agent retains its existing solo-mode behavior.
