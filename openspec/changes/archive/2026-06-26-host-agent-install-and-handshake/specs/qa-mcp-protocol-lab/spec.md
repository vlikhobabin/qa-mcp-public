## ADDED Requirements

### Requirement: Host agent install is an explicit Windows host step
The protocol lab SHALL provide a documented Windows host-side install command
that installs the host display agent into the interactive user session without
requiring the Linux container to copy or execute files on a cold host.

#### Scenario: Installer registers interactive startup
- **WHEN** the install command is run on the Windows host
- **THEN** it places the host agent executable in the documented location
- **AND** it registers an interactive logon Scheduled Task for the current
  user rather than a Session-0 service

#### Scenario: Installer configures access
- **WHEN** the install command completes successfully
- **THEN** it records the selected host-agent port and token configuration
- **AND** it configures or reports the firewall rule needed for Docker Desktop
  access through `host.docker.internal`

### Requirement: Remote backend verifies agent version and hash
The protocol lab SHALL verify the host agent version and binary hash before
using remote display primitives.

#### Scenario: Agent version matches expected version
- **WHEN** `/version` returns the expected version and hash
- **THEN** the remote display backend allows primitive calls
- **AND** the handshake result is available for diagnostics

#### Scenario: Agent is absent or mismatched
- **WHEN** the host agent cannot be reached or its version/hash differs from
  the expected value
- **THEN** remote display tools fail closed with a stable error code
- **AND** the error names the exact Windows install/update command
- **AND** v1 does not auto-replace the host binary
