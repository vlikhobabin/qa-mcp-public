## ADDED Requirements

### Requirement: Host-agent resolves function keys for remote UI refresh
The Windows host-agent SHALL resolve named function keys `F1` through `F12` to
their corresponding Win32 virtual-key codes before sending authenticated
desktop input. Unsupported key names MUST still fail closed without sending an
input event.

#### Scenario: F5 is available for dynamic-list refresh
- **WHEN** an authenticated qa-mcp display-backend request sends key `F5`
- **THEN** the host-agent resolves the key as `VK_F5` (`0x74`)
- **AND** the request proceeds through the existing authenticated `SendInput`
  path.

#### Scenario: Function-key range is mapped consistently
- **WHEN** the host-agent resolves keys `F1` through `F12`
- **THEN** they map to contiguous Win32 virtual keys `0x70` through `0x7B`
- **AND** existing aliases such as `enter`, `escape`, navigation keys, letters,
  digits, and `F4` continue to resolve.

#### Scenario: Unknown key still fails closed
- **WHEN** an authenticated request supplies an unsupported key name
- **THEN** the host-agent returns an unsupported-key error
- **AND** no desktop input is sent for that key.
