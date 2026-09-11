## ADDED Requirements

### Requirement: Host-agent network exposure is scoped by default

The Windows host-agent installer SHALL NOT expose desktop-control endpoints to the whole LAN by default. A default install SHALL bind to loopback or create an inbound firewall rule scoped to an explicit Docker/host subnet. Any non-loopback bind MUST require an explicit remote-address allowlist or equivalent operator opt-in.

#### Scenario: Default install is locally scoped
- **WHEN** the host-agent is installed without an explicit remote-address allowlist
- **THEN** the listener/firewall combination does not accept arbitrary LAN clients
- **AND** the install script records the chosen local scope in its output or runbook guidance

#### Scenario: Non-loopback exposure requires an allowlist
- **WHEN** an operator configures a non-loopback bind address
- **THEN** the firewall rule is created with an explicit remote address or subnet
- **AND** the unsafe broad-LAN default is not silently restored

### Requirement: Host-agent token is not exposed in the service command line

The host-agent scheduled task SHALL obtain its bearer token from a protected token source such as an ACL-controlled file or environment source, not from a process command-line argument containing the token value.

#### Scenario: Scheduled task command hides the token
- **WHEN** the install script creates or updates the scheduled task action
- **THEN** the action command line does not include the bearer token value
- **AND** local process-list or WMI inspection cannot recover the token from the task action arguments

### Requirement: Host-agent endpoints fail closed behind authenticated access

The host-agent SHALL reject missing or wrong tokens on desktop-control and sensitive status endpoints, SHALL compare accepted tokens in constant time, and SHALL reject hostile browser origins unless explicitly allowed. Any unauthenticated health response SHALL be minimal and MUST NOT expose binary SHA, foreground window title, HWND, token state or desktop-session details.

#### Scenario: Wrong or missing token is rejected
- **WHEN** a request to a protected host-agent endpoint omits `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns an unauthorized response
- **AND** no desktop action, screenshot capture or detailed status disclosure occurs

#### Scenario: Authenticated request succeeds
- **WHEN** a request supplies the configured token and an allowed origin
- **THEN** the endpoint executes its normal host-agent behavior

#### Scenario: Hostile origin is refused
- **WHEN** a browser-origin request supplies a non-allowlisted `Origin`
- **THEN** the endpoint rejects the request before performing any desktop-control action

#### Scenario: Unauthenticated status does not leak desktop state
- **WHEN** an unauthenticated client calls a public health/status endpoint
- **THEN** the response contains no binary SHA, foreground HWND, foreground title or other desktop-session details
