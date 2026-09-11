## ADDED Requirements

### Requirement: Model-B remote display subset is live-verified
The protocol lab SHALL retain compact live evidence that model-B remote-client
mode can recover the display-bound input/screenshot subset through the Windows
host agent.

#### Scenario: Genuine object attribute edit is proven
- **WHEN** `write_form_value_xtest` is executed through the remote display
  backend against the Windows-rendered 1C client
- **THEN** retained evidence shows a genuine Unicode input event reached the
  target managed-form field
- **AND** the proof records screenshot or read-only data assertion evidence for
  the resulting state

#### Scenario: Host screenshot is proven
- **WHEN** `capture_screenshot` is executed through the remote display backend
- **THEN** retained evidence includes a PNG or sanitized screenshot summary
  produced from the host-rendered 1C window
- **AND** the proof distinguishes the host screenshot route from the Linux X11
  route

### Requirement: Remaining display tools publish explicit statuses
The protocol lab SHALL publish a compact status table for each display-bound
tool recovered by the host agent and for any tool intentionally deferred or
blocked.

#### Scenario: Display tool status is published
- **WHEN** the model-B display verification bundle is created
- **THEN** it lists `capture_screenshot`, `send_keys`,
  `write_form_value_xtest`, `write_form_fields_by_label`,
  `set_table_date_cell`, `get_window_list` and `open_external_processor`
- **AND** each row records passed, blocked, deferred or not-applicable status
  with evidence path or residual risk

#### Scenario: Raw runtime output remains ignored
- **WHEN** live verification produces screenshots, logs or temporary payloads
- **THEN** raw output remains under ignored runtime or artifact paths unless a
  sanitized curated file is explicitly selected for review
- **AND** reviewed docs link only compact evidence summaries
