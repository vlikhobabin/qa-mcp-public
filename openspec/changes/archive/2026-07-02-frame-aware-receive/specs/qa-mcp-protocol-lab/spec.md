## ADDED Requirements

### Requirement: Protocol receive uses frame tail markers before idle gaps
The Python manager SHALL read TestClient protocol responses until the protocol
tail marker is observed or a hard monotonic deadline expires, using idle timing
only as a fallback for responses without the known tail marker.

#### Scenario: Tail marker arrives after an idle gap
- **WHEN** a TestClient response is delivered in two socket chunks separated by
  more than the receive idle window and the second chunk contains the protocol
  tail marker
- **THEN** the receive layer returns one complete response buffer containing
  both chunks
- **AND** downstream value parsing can extract the response value from that
  buffer

#### Scenario: No tail marker is observed
- **WHEN** response bytes are received but the known tail marker is not present
  before the idle fallback or hard deadline
- **THEN** the receive layer returns the bytes collected so far without waiting
  indefinitely
- **AND** the deadline calculation uses monotonic time rather than wall-clock
  timestamps

### Requirement: Protocol receive implementation is shared
The Python manager SHALL use one shared receive implementation for the native
read session and native mutation session so frame-boundary semantics and timeout
handling stay consistent across read and mutation-facing protocol code.

#### Scenario: Existing receive callers drain responses
- **WHEN** `session.read_available` and `native_mutation._read_available` drain a
  protocol response
- **THEN** both call the same frame-aware helper
- **AND** neither implementation carries separate wall-clock idle-loop logic
