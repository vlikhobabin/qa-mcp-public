## REMOVED Requirements

### Requirement: Host-agent probes file infobase markers without browsing
**Reason**: The public bridge exposes no general host-path probe; fixed target
validation is part of bounded lifecycle handling.
**Migration**: Supply the configured target to launch and consume redacted
lifecycle/target identity.

### Requirement: Host-agent executes only allowlisted local agent CLIs
**Reason**: Agent CLI execution is an AI for 1C integration, not standalone QA.
**Migration**: Use the private Runtime Proxy/agent component.

### Requirement: Host-agent preserves agent CLI reasoning effort
**Reason**: Agent CLI execution is removed from the public bridge.
**Migration**: Configure reasoning in the owning private agent runtime.

### Requirement: Host-agent agent selection remains explicit
**Reason**: Agent CLI selection is removed from the public bridge.
**Migration**: Select agents in the owning private runtime.

### Requirement: Agent completion reports bounded effective profile metadata
**Reason**: Agent completion is removed from the public bridge.
**Migration**: Consume profile metadata through the owning private runtime.

### Requirement: Host-agent executes only allowlisted COM worker operations
**Reason**: The public bridge has no COM worker dependency.
**Migration**: AI for 1C routes data access through its private Runtime Proxy and
live-mcp contracts.

### Requirement: Host-agent executes only allowlisted local 1C platform commands
**Reason**: Arbitrary platform command execution is outside the standalone
bridge boundary.
**Migration**: Keep fixed TestClient lifecycle internally; route other commands
through the owning private platform adapter.

### Requirement: Host-agent enforces platform argv mutation policy server-side
**Reason**: The public bridge exposes no generic platform command endpoint.
**Migration**: Enforce command policy in the owning private adapter.

### Requirement: Platform command output preserves localized diagnostics
**Reason**: Generic platform execution is removed.
**Migration**: Preserve diagnostics in the owning private adapter.

### Requirement: Host-agent health classifies COM worker feature impact
**Reason**: No COM worker is shipped or supervised.
**Migration**: Public health reports only standalone capabilities.

### Requirement: Host-agent exposes an authenticated COMConnector doctor
**Reason**: COMConnector is outside the open bridge.
**Migration**: Use the private live/platform diagnostic surface.

### Requirement: COMConnector doctor read-smoke works against a real Russian-locale file base
**Reason**: COMConnector is outside the open bridge.
**Migration**: Retain this proof in the owning private component.

### Requirement: Host-agent self-registers its immutable bridge identity
**Reason**: Public standalone uses local explicit configuration and no Team
registry.
**Migration**: Runtime Proxy owns private cloud registration.

### Requirement: Registration failures are secret-safe and do not degrade the bridge
**Reason**: Team registration is removed from the public bridge.
**Migration**: Apply the contract in the private Runtime Proxy.

### Requirement: Solo mode performs no registry I/O
**Reason**: The public executable contains no registry client at all.
**Migration**: No replacement is required.

### Requirement: Host-agent supervises the configured workstation bsl-agent
**Reason**: BSL supervision is not a standalone QA responsibility.
**Migration**: Use the private Runtime Proxy/BSL component.

### Requirement: Host-agent exposes only bounded authenticated BSL routes
**Reason**: BSL routes are removed from the public bridge.
**Migration**: Use the private BSL provider route.

### Requirement: Host-agent installer reconciles effective task arguments
**Reason**: The existing requirement includes product-specific helper and
registration arguments that are replaced by a new standalone installer
contract.
**Migration**: Reconcile only the narrow public bridge token, listener,
capability and lifecycle arguments under the new bridge specification.

### Requirement: Platform timeout diagnostics report spawned process identity
**Reason**: Generic platform execution is removed from the public bridge.
**Migration**: Fixed TestClient lifecycle retains its own bounded timeout and
owned-process diagnostics.

### Requirement: Host-agent window selection diagnostics identify weak matches
**Reason**: Broad title matching and `-WindowTitle` fallback are incompatible
with the public bridge's exact lifecycle/PID/TPort-owned window authority.
**Migration**: Call `/window_list` with a complete bridge-owned lifecycle target;
the bridge returns only that target's process-owned 1C window.

### Requirement: Host-agent resolves the display target window from the driven client TPort
**Reason**: Raw `client_port`, explicit-selector precedence and legacy generic
window fallback permit authority outside the complete lifecycle binding.
**Migration**: Supply the complete bridge-owned `client_target`; a selector is
only a non-authoritative compatibility hint.

### Requirement: Windows host-agent background helpers do not expose console windows
**Reason**: COM, CLI, generic platform, maintenance and BSL helper execution is
removed from the standalone public bridge.
**Migration**: Private helper processes and their window policy belong to the
owning private Runtime Proxy components.

## MODIFIED Requirements

### Requirement: Host-agent endpoints fail closed behind authenticated access

The host-agent SHALL reject missing or wrong tokens on standalone TestClient
lifecycle, relay, desktop-control, and sensitive status endpoints, SHALL
compare accepted tokens in constant time, and SHALL reject hostile browser
origins unless explicitly allowed. Any unauthenticated health response SHALL
be minimal and MUST NOT expose binary SHA, foreground window title, HWND,
token state, or desktop-session details.

#### Scenario: Wrong or missing token is rejected
- **WHEN** a request to a protected host-agent endpoint omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns an unauthorized response
- **AND** no lifecycle, relay, desktop action, screenshot capture or detailed
  status disclosure occurs.

#### Scenario: Authenticated request succeeds
- **WHEN** a request supplies the configured token and an allowed origin
- **THEN** the endpoint executes its normal host-agent behavior.

#### Scenario: Hostile origin is refused
- **WHEN** a browser-origin request supplies a non-allowlisted `Origin`
- **THEN** the endpoint rejects the request before performing any lifecycle,
  relay or desktop-control action.

#### Scenario: Unauthenticated status does not leak desktop state
- **WHEN** an unauthenticated client calls a public health/status endpoint
- **THEN** the response contains no binary SHA, foreground HWND, foreground
  title or other desktop-session details.

### Requirement: Host-agent bounds concurrent bridge execution

The Windows host-agent SHALL apply a shared in-flight concurrency cap to
TestClient lifecycle and bounded display/UIA endpoints after authentication.
The cap MUST cover `/testclient/{launch,status,stop}`, `/window_list`,
`/send_keys`, `/type`, `/click`, `/screenshot` and
`/uia/visible_list_cells`. A request that cannot acquire capacity MUST fail
closed before handler, process or driver work.

#### Scenario: N+1 bridge request is throttled before work
- **WHEN** the host-agent has reached its configured in-flight execution cap
- **AND** an authenticated caller sends another lifecycle or display request
- **THEN** the endpoint returns HTTP `429` with
  `execution-capacity-exhausted`
- **AND** no handler, subprocess or desktop driver work begins for that request

#### Scenario: Capacity is released after completion
- **WHEN** a protected endpoint acquires capacity and then returns success,
  failure, cancellation, or timeout
- **THEN** the in-flight slot is released
- **AND** a later valid request can acquire capacity normally

### Requirement: Host-agent binds display requests to an owned TestClient lifecycle

The Windows host-agent SHALL require a complete bridge-owned `client_target`
on authenticated key, type, click, screenshot, window-list, and
visible-list-cell requests. Before driver work it MUST validate the lifecycle
id, PID, listening TPort, ownership record and current process-owned visible 1C
window. Explicit selectors are compatibility hints and MUST NOT override or
suppress that lifecycle binding; no explicit-selector, foreground-window or
alternate-process fallback is permitted.

#### Scenario: Explicit selector cannot override lifecycle target
- **WHEN** a request supplies an explicit selector and a complete bridge-owned
  `client_target`
- **THEN** the bridge resolves only the lifecycle PID/TPort-owned 1C window
- **AND** ignores the selector as an authority source.

#### Scenario: Non-owned or stale target is refused before driver action
- **WHEN** the target is missing ownership or its lifecycle id, PID or TPort no
  longer identifies the same live TestClient window
- **THEN** the bridge returns a structured refusal
- **AND** no display/UIA driver action occurs.
