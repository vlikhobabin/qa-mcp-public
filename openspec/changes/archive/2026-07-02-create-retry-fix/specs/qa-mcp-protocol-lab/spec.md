## ADDED Requirements

### Requirement: Create-form label locate retry is reachable for production foreground methods

The qa-mcp label-write path SHALL either run its bounded create-form activation retry for foreground methods produced
by the current code, or remove retry metadata that cannot be emitted. A first-screenshot render race on a create form
SHALL NOT be reported as a final label miss before the configured one-shot activation retry is attempted.

#### Scenario: First screenshot miss retries activation

- **WHEN** `write_form_fields_by_label` foregrounds a create form and the first screenshot cannot locate the requested
  label
- **THEN** qa-mcp performs one activation retry through the foreground resource or Ctrl+Tab
- **AND** captures another screenshot before deciding whether the label is missing
- **AND** result metadata names the `activation_retry` path when the retry was used

#### Scenario: Retry remains bounded

- **WHEN** the label is still missing after the retry
- **THEN** qa-mcp returns the normal `"label not located"` result
- **AND** it does not continue retrying indefinitely

#### Scenario: No dead foreground method guard remains

- **WHEN** the label-write source is inspected
- **THEN** retry behavior is keyed to actual foreground methods or the retry branch is absent
- **AND** no unreachable `create_splice`-only guard determines production behavior
