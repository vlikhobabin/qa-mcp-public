## ADDED Requirements

### Requirement: Host-agent binds implicit display requests to a validated TestClient identity

The Windows host-agent SHALL accept a bounded `client_target` on authenticated key, type, click, screenshot, and visible-list-cell requests. When no explicit non-empty, non-wildcard window selector is present, the host-agent MUST validate the target's lifecycle id when supplied, PID, listening TPort, and current process-owned visible 1C window before invoking a display driver primitive. It SHALL resolve an empty-title `V8TopLevelFrame*` window by process/class rather than caption. Missing, stale, mismatched, wildcard-only, or ambiguous implicit targeting MUST fail closed and MUST NOT fall back to the OS foreground window or another 1C process.

#### Scenario: Owned lifecycle resolves an empty-title window

- **WHEN** an authenticated display request supplies a `client_target` whose lifecycle id, PID, and TPort match a live host-agent-owned TestClient
- **AND** that process owns a visible `V8TopLevelFrame*` window with an empty title
- **THEN** the host-agent resolves that exact process-owned window
- **AND** invokes the requested display primitive only for that target.

#### Scenario: Attach-only target is revalidated without ownership

- **WHEN** authenticated `/testclient/status` resolves an out-of-band TestClient listener to a PID and process-owned 1C window
- **THEN** it returns a bounded non-owning `client_target`
- **AND** each later display request re-checks the PID/TPort/window binding without creating stop authority.

#### Scenario: Stale or mismatched target is refused before driver action

- **WHEN** the supplied lifecycle id, PID, or TPort no longer identifies the same live TestClient/window
- **THEN** the host-agent returns a structured target-missing, stale, or mismatch error
- **AND** no focus, input, click, screenshot, UIA, generic 1C-window, or foreground-window operation occurs.

#### Scenario: Explicit selector remains authoritative

- **WHEN** a request supplies both a valid explicit non-empty, non-wildcard window selector and a `client_target`
- **THEN** the host-agent uses the explicit selector
- **AND** preserves the existing explicit-selector behavior.

#### Scenario: Window-target capability prevents legacy downgrade

- **WHEN** qa-mcp has an active implicit `client_target`
- **AND** the host-agent does not advertise `testclient-window-target`
- **THEN** qa-mcp refuses the request before posting the display primitive
- **AND** the older host-agent cannot ignore the target and apply a weak fallback.

### Requirement: Host-agent reports typed desktop-session availability

Before invoking a screenshot, key, text, click, or visible-list-cell primitive, the Windows host-agent SHALL classify whether its interactive desktop is active. A locked, disconnected, or non-interactive session MUST produce a distinct structured error and MUST NOT invoke the driver primitive. Diagnostics SHALL contain only bounded state/reason fields and MUST NOT disclose usernames, raw session inventories, HWNDs, titles, screenshots, or logs.

#### Scenario: Locked desktop is refused

- **WHEN** the target TestClient identity is valid but the interactive desktop is locked
- **THEN** the host-agent returns `desktop-session-locked`
- **AND** does not capture or send input.

#### Scenario: Disconnected desktop is refused

- **WHEN** the target TestClient identity is valid but its interactive session is disconnected
- **THEN** the host-agent returns `desktop-session-disconnected`
- **AND** does not capture or send input.

#### Scenario: Non-interactive desktop is refused

- **WHEN** the host-agent is executing without access to an interactive input desktop
- **THEN** it returns `desktop-session-noninteractive`
- **AND** does not attempt a foreground fallback or driver action.
