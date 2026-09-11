## ADDED Requirements

### Requirement: Windows host-agent background helpers do not expose console windows

The Windows host-agent SHALL start background console helpers without an
operator-visible console window and SHALL preserve those window attributes when
it adds process-group ownership. A helper that requires console semantics MAY
retain a console only when its initial window is explicitly hidden. Background
helper startup or restart MUST NOT steal focus from the interactive user.

#### Scenario: Short-lived helper is assigned a process group

- **WHEN** the host-agent applies no-window semantics and then adds a Windows
  process group to a COM, CLI, platform or maintenance helper
- **THEN** both `CREATE_NO_WINDOW` and `CREATE_NEW_PROCESS_GROUP` remain applied
- **AND** the helper creates no visible console window.

#### Scenario: BSL helper requires console semantics

- **WHEN** the supervisor starts the configured `bsl-agent.exe` workstation
  service
- **THEN** it preserves the console required by warmup and requests a hidden
  initial window
- **AND** normal launch or restart does not expose a console or take focus.
