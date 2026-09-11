## ADDED Requirements

### Requirement: Host-agent installer reconciles effective task arguments

The Windows host-agent installer SHALL act as an idempotent ensure surface that
compares the desired scheduled-task action and copied artifact hashes with the
existing scheduled task and the running owned host-agent process before deciding
whether to restart. It MUST restart the scheduled task when effective arguments
or owned artifacts drift, MUST leave a matching running task alone, and MUST
report restart reasons without token values or secret file contents.

#### Scenario: Running process with stale project arguments is restarted

- **WHEN** the desired scheduled-task action contains BSL arguments for the
  selected project workspace
- **AND** the owned `qa-mcp-host-agent.exe` process is already running from the
  installed executable path with a different command line
- **THEN** the installer stops and starts the scheduled task
- **AND** the output includes a concise secret-safe restart reason for running
  process argument drift.

#### Scenario: Matching running process is left alone

- **WHEN** the existing scheduled task action, installed artifacts and running
  owned host-agent command line already match the desired state
- **THEN** a second installer run does not stop or start the scheduled task
- **AND** the output reports that restart was skipped because the running task
  already matches desired state.

#### Scenario: Owned BSL child is cleaned only during restart

- **WHEN** installer reconciliation decides that a restart is required
- **THEN** it may stop the owned `bsl-agent.exe` staged at the configured
  install path
- **AND** it MUST NOT kill BSL helper processes by executable name alone.

#### Scenario: Artifact drift triggers restart without secret leakage

- **WHEN** the staged host-agent or BSL helper artifact differs from the
  installed artifact
- **THEN** installer reconciliation restarts the scheduled task after copying
  the artifact
- **AND** restart diagnostics include only secret-safe reason labels or hashes,
  never token file contents or registry/onboarding credentials.
