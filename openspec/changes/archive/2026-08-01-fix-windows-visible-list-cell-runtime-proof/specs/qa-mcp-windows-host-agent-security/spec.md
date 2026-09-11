## MODIFIED Requirements

### Requirement: Host-agent exposes authenticated 1C window and visible-cell diagnostics
The Windows host-agent SHALL expose bounded desktop diagnostics for qa-mcp
remote-client list reads behind the existing token and origin checks. Window
diagnostics MUST include class names for top-level windows, and visible-cell
diagnostics MUST execute only a fixed local UI Automation probe for the resolved
target window rather than arbitrary caller-supplied commands. When the resolved
target owns a visible accessible descendant with a non-empty name and an
allowlisted cell control type, the diagnostic SHALL include that name in its
bounded result without retrying against a caption, wildcard, generic 1C, or
foreground target.

#### Scenario: Authenticated window list includes class metadata
- **WHEN** an authenticated client calls `/window_list`
- **THEN** each visible top-level window entry includes handle, title, class,
  PID, visibility, and geometry when available
- **AND** a 1C SDI frame can be identified by class `V8TopLevelFrame*`.

#### Scenario: Visible-cell diagnostic is authenticated
- **WHEN** a request to the visible-cell diagnostic endpoint omits the
  host-agent token or supplies a wrong token
- **THEN** the endpoint returns an unauthorized response
- **AND** no UI Automation probe is executed.

#### Scenario: Visible-cell diagnostic targets the 1C frame
- **WHEN** an authenticated visible-cell diagnostic omits an explicit window
- **AND** a visible `V8TopLevelFrame*` window exists
- **THEN** the host-agent resolves that 1C frame
- **AND** it returns the resolved target metadata plus a bounded list of visible
  UI Automation text values.

#### Scenario: Exact empty-title target exposes its visible named descendant
- **WHEN** an authenticated visible-cell request resolves an exact
  process-owned empty-title `V8TopLevelFrame*` target
- **AND** that target contains a visible accessible descendant named
  `VisibleCell` with an allowlisted cell control type
- **THEN** the bounded result contains `VisibleCell`
- **AND** no caption, wildcard, generic 1C-window, or foreground fallback is
  attempted.

#### Scenario: Visible-cell diagnostic reports target misses
- **WHEN** the requested or default 1C target window cannot be found
- **THEN** the host-agent returns a structured `window-not-found` result
- **AND** it does not return an empty visible-cell list as if the target had no
  cells.
