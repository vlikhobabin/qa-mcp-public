## ADDED Requirements

### Requirement: Windows host agent exposes display primitives
The protocol lab SHALL provide a Windows host-side agent that exposes the
display primitives needed by model-B remote-client mode without requiring 1C
libraries or a 1C TestManager process.

#### Scenario: Agent reports version and health
- **WHEN** the container connects to the host agent
- **THEN** `GET /version` returns an agent version and binary hash
- **AND** `GET /health` reports whether the agent is running in an interactive
  desktop session that can attempt input and screenshot primitives

#### Scenario: Agent sends Unicode text
- **WHEN** the Python backend asks the agent to type Unicode text
- **THEN** the agent uses Win32 `SendInput` Unicode key events
- **AND** the result reports success or a structured foreground/input error

#### Scenario: Agent captures a PNG screenshot
- **WHEN** the Python backend asks the agent for a screenshot of the target
  client window
- **THEN** the agent returns a PNG image of the Windows-rendered 1C client
- **AND** the response includes target-window diagnostics sufficient to
  distinguish blank, hidden and missing-window captures

### Requirement: Host agent transport is host-scoped and token-protected
The protocol lab SHALL expose the Windows host agent over a host-scoped HTTP
port with token protection for primitive endpoints.

#### Scenario: Primitive endpoint lacks token
- **WHEN** a primitive request omits or mismatches the configured token
- **THEN** the agent rejects the request with a stable authentication error
- **AND** it does not inject input, click, enumerate windows or return
  screenshots for that request

#### Scenario: Agent listens on host-only address
- **WHEN** the agent starts with the default configuration
- **THEN** it binds to a loopback or host-only address intended for Docker
  Desktop `host.docker.internal` access
- **AND** documentation states how to override the bind address for the lab
  only when local policy permits it
