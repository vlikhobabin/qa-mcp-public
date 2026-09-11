## ADDED Requirements

### Requirement: V2 fixture safe-action target manifest is published

The protocol lab SHALL publish reviewed safe-action target rows for the V2
fixture surface.

#### Scenario: Target row is published

- **WHEN** a V2 safe-action target is documented
- **THEN** the published row includes `target_id`, `target_marker`, allowed
  action family, expected local state markers, reset hook and compact
  evidence path
- **AND** the row is linked from the fixture target map or evidence index

#### Scenario: Excluded controls stay out

- **WHEN** a control would require text input, value mutation, business
  command execution or external side effects
- **THEN** it is not published as a V2 safe-action target
- **AND** it is routed to later mutation or recovery work

### Requirement: Fixture safe-action manifest rows remain candidate until proof

The protocol lab SHALL keep fixture safe-action manifest rows as candidate or
planned evidence until replay or direct Python-manager proof exists.

#### Scenario: Candidate row needs proof

- **WHEN** a manifest row is published before acceptance
- **THEN** it records its evidence path and unresolved proof status
- **AND** raw runtime payloads remain outside reviewed git changes
