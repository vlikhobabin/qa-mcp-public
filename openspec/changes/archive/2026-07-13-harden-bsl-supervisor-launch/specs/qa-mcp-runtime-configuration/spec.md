## ADDED Requirements

### Requirement: Workstation BSL helper launch is independent of service CWD
The host-agent SHALL launch the configured workstation BSL helper with its
working directory set to the helper binary directory, SHALL support an explicit
local child-output log, and SHALL close the parent log handle after each child
exit. The default readiness timeout SHALL be at least 480 seconds.

#### Scenario: Scheduled-task parent CWD is not writable
- **WHEN** host-agent runs from a service or scheduled-task CWD unrelated to the helper
- **THEN** the helper observes its own binary directory as CWD
- **AND** a valid fake helper reaches `ready` without using the parent CWD.

#### Scenario: Helper exits before opening its own log
- **WHEN** child-output capture is configured and the helper writes stderr then exits
- **THEN** the configured local log retains the bounded diagnostic
- **AND** the supervisor restarts without retaining an open parent file handle.

#### Scenario: Default cold warmup exceeds one minute
- **WHEN** no startup-timeout override is provided
- **THEN** both supervisor and host-agent CLI use a timeout of at least 480 seconds.
