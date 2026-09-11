## ADDED Requirements

### Requirement: Windows host-agent reinstall reconciles only its staged BSL helper

Before replacing the staged BSL artifact, the Windows host-agent installer SHALL
stop a stale helper only when its executable path exactly equals the
installer-owned target path. It SHALL NOT terminate every process with the
`bsl-agent.exe` image name.

#### Scenario: Previous owned helper survived supervisor termination

- **WHEN** reinstall finds a running `bsl-agent.exe` at the staged target path
- **THEN** it stops that process before copying the replacement and starting the
  scheduled task
- **AND** the new supervisor does not enter a bind-conflict restart loop.

#### Scenario: Unrelated helper has the same image name

- **WHEN** another `bsl-agent.exe` runs from a different path
- **THEN** installer cleanup leaves it unchanged.
