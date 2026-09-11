## ADDED Requirements

### Requirement: Protocol captures carry platform and configuration metadata
Curated protocol captures and manager-frame template sets SHALL expose a
sanitized metadata record that includes the captured platform build and
configuration identity when known. The metadata MUST NOT contain raw TCP payloads,
credentials, screenshots, infobase dumps, or customer data.

#### Scenario: Capture metadata is loaded
- **WHEN** qa-mcp loads metadata for a curated capture or template set
- **THEN** the metadata includes a schema id, capture id, platform build,
  configuration label fields, source/template paths, and notes
- **AND** the metadata can be serialized as reviewed text without exposing raw
  capture payloads or secrets

#### Scenario: Missing configuration metadata is explicit
- **WHEN** a legacy capture has no configuration tag
- **THEN** the selection metadata marks the configuration as unknown
- **AND** callers can report that no config-matched proof exists before relying
  on the capture for a real customer configuration

### Requirement: List-read capture selection prefers config-matched captures
The protocol runtime SHALL select list-read captures by requested platform build
and configuration metadata when those tags are supplied. If no exact
configuration match exists, the runtime MUST return an observable fallback
selection reason instead of silently treating a generic bundled capture as
config-matched proof.

#### Scenario: Exact config match is selected
- **WHEN** a list-read operation requests platform `8.3.27.2130` and
  configuration `Бухгалтерия 3.0`
- **AND** a capture metadata record matches both tags
- **THEN** the selector returns that capture
- **AND** the selection result records `match: "exact"`

#### Scenario: Generic fallback is visible
- **WHEN** no capture metadata record matches the requested configuration
- **THEN** the selector MAY fall back to the existing active bundled capture
- **AND** the selection result records that the capture is not config-matched
- **AND** the result names the requested platform/configuration tags that remain
  unproven

### Requirement: Manager-handshake drift is detected before list reads are trusted
Before using a selected capture for a live list-read contour, qa-mcp SHALL be
able to run a bounded manager-handshake preflight that verifies the client
ACK/GUID response after the captured or synthesized session-bootstrap frames.
If the ACK/GUID marker is absent or undecodable, the preflight MUST fail loudly
with a specific manager-handshake drift diagnostic.

#### Scenario: ACK GUID is observed
- **WHEN** the preflight sends manager frame 3 and the live client response
  contains the expected ACK/GUID marker
- **THEN** the preflight returns `ok: true`
- **AND** it records the observed ACK GUID, frame index, and selected capture
  metadata

#### Scenario: Manager handshake moved
- **WHEN** the preflight sends manager frame 3 and the response lacks the
  expected ACK/GUID marker
- **THEN** the preflight returns `ok: false`
- **AND** the error is `manager-handshake-moved`
- **AND** the diagnostic names the selected capture, requested platform/config
  tags, frame index, and refresh-capture action hint

#### Scenario: Handshake drift diagnostic is propagated
- **WHEN** a descriptor or list-read setup fails because the preflight reports
  `manager-handshake-moved`
- **THEN** the tool result reports the drift diagnostic as the specific cause
- **AND** it does not claim the list is empty or config-matched

### Requirement: Capture refresh procedure is reproducible and raw-data safe
The protocol lab SHALL provide a documented procedure and command-line helper
for re-recording the irreducible session bootstrap plus list-open/read templates
on a target platform/configuration. The procedure MUST retain only sanitized
metadata and bounded evidence in reviewed changes while keeping raw pcaps,
traffic logs, screenshots, platform logs, and infobase data in ignored runtime
paths.

#### Scenario: Refresh metadata is prepared
- **WHEN** an operator prepares a refresh for a target platform/configuration
- **THEN** the helper writes a sanitized metadata sidecar naming the target
  platform build, configuration label, capture id, raw runtime roots, and
  template output paths
- **AND** reviewed git changes contain only the sidecar/runbook/tool updates,
  not the raw capture streams

#### Scenario: Runtime proof is unavailable
- **WHEN** the target Windows [redacted third-party configuration] host is unavailable during delivery
- **THEN** the delivery records a qa-mcp provider gap for the positive-read proof
- **AND** no artifact claims that `read_list_grid` returned visible
  `Справочник.Валюты` rows on that host
