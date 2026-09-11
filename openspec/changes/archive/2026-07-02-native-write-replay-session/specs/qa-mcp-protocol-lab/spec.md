## ADDED Requirements

### Requirement: Native write replay operations use a shared replay session

The Python manager SHALL execute native write, list, dialog and window replay
operations through one shared replay-session engine for socket setup, setup
frame replay, operation frame replay, response observation and cleanup. The
shared engine MUST preserve each operation's existing public arguments, result
shape and verdict semantics.

#### Scenario: Replay operation uses the shared receive point

- **WHEN** a native replay operation drains TestClient protocol responses
- **THEN** the replay engine calls `read_protocol_available`
- **AND** no converted operation carries its own idle-gap receive loop

#### Scenario: Retarget failures keep structured verdicts

- **WHEN** a converted write operation cannot retarget a frame that must contain
  the requested field leaf
- **THEN** the operation returns the existing structured `retarget_failed`
  verdict
- **AND** the shared replay engine does not mask the retarget failure as a
  generic replay divergence

#### Scenario: Operation-specific commit verdict is preserved

- **WHEN** a converted write operation reads back the target field value
- **THEN** its verdict callback applies the same normalized equality rules used
  before the refactor
- **AND** generic prefix matches do not prove a commit unless the documented
  date/reference formatting exception applies

#### Scenario: Send timeout remains distinct from response divergence

- **WHEN** sending a converted replay frame exceeds the send timeout
- **THEN** the result or raised error preserves the existing send-timeout reason
- **AND** the receive timeout is restored for subsequent response draining
