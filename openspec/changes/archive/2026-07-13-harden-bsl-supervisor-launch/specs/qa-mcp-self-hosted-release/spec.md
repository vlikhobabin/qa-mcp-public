## ADDED Requirements

### Requirement: Windows installer renders durable workstation BSL supervision
The delivered Windows host-agent installer SHALL accept the BSL helper and
workspace inputs, SHALL render configuration path, syntax-helper directory,
platform version, writable cache, child log and startup timeout into the fixed
scheduled-task command, and SHALL configure Task Scheduler to restart the
host-agent after failure.

#### Scenario: Complete thin-workstation BSL inputs are supplied
- **WHEN** the operator installs host-agent with the BSL helper, workspace,
  configuration, syntax-helper and platform-version inputs
- **THEN** the scheduled-task action contains the corresponding fixed `-bsl-*` flags
- **AND** cache and child-log paths resolve below writable local state
- **AND** the startup timeout is at least 480 seconds.

#### Scenario: Host-agent task exits unexpectedly
- **WHEN** the registered scheduled task exits with a failure status
- **THEN** Task Scheduler applies a bounded restart interval and count
- **AND** logon-trigger and unlimited execution-time behavior remain intact.
