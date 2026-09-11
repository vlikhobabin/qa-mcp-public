## ADDED Requirements

### Requirement: Useful read-only element rows have reviewed request-hash evidence or an unavailable proof
The protocol lab SHALL capture, extract or explicitly prove unavailable the
reviewed request-frame hash evidence for useful read-only element probe rows
before their resolution is published.

#### Scenario: Reviewed element request hash is produced
- **WHEN** `form-element-details` or `typed-input-field-readonly` has captured
  or extractable manager-to-client request frames
- **THEN** the compact evidence records capture id, frame range, request and
  response sizes, normalized hash, dynamic fields, operation token, response
  markers, replay or direct Python-manager status and evidence path
- **AND** raw captures and full probe output remain in ignored runtime
  directories

#### Scenario: Reviewed element request hash is unavailable
- **WHEN** the current lab path cannot produce reviewed request-frame hash
  evidence for a useful element row
- **THEN** the compact evidence records the attempted source, command or
  extraction path, observed result, unresolved reason and next actionable
  blocker
- **AND** the row remains non-accepted for later classification and
  publication

### Requirement: Element request-hash capture remains read-only
The protocol lab SHALL keep element request-hash capture and probing within
read-only TestClient operations.

#### Scenario: Live element hash capture runs
- **WHEN** a live capture or direct Python-manager probe is run for element
  request-hash evidence
- **THEN** it uses read-only form/window/element query operations only
- **AND** it does not click controls, enter text, execute commands, change
  business data or terminate unrelated 1C processes
