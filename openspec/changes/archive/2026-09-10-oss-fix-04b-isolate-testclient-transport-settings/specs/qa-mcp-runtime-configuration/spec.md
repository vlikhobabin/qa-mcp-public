## ADDED Requirements

### Requirement: Composed native transport uses application-owned relay settings

Every native connection and relay-readiness resolution within a composed call SHALL use the active application's relay settings. Bound explicit absence MUST
remain absence. A supplied low-level env mapping MUST NOT override an active
application scope. Session, replay, foreground, native write/mutation/XTEST and
lifecycle/attachment consumers SHALL share this setting source without weakening
existing target or session admission.

#### Scenario: Distinct factories and conflicting process relay (C1)

- **WHEN** two real factories have different relay endpoints/tokens and process environment contains a third relay
- **THEN** each invoked native consumer resolves only its active application's endpoint and authentication
- **AND** fake socket evidence identifies the actual requested destination and exact synthetic preface.

#### Scenario: Explicit absence remains direct (C1)

- **WHEN** a factory has no relay fields while process environment configures a relay
- **THEN** its direct connection sends no relay preface
- **AND** its listener-only check does not use the process relay.

### Requirement: Relay configuration failures are bounded before effects

Composed partial or malformed relay configuration SHALL fail before socket
creation and SHALL NOT be completed from process environment. Diagnostics MUST
exclude configured tokens and arbitrary peer-supplied prose. Authentication
refusal SHALL close the connection before protocol code receives it.

#### Scenario: Partial or malformed settings (C2)

- **WHEN** explicit Settings contains a partial pair, malformed endpoint or preface-unsafe token
- **THEN** configuration fails before any socket is created
- **AND** the diagnostic remains bounded and contains no token.

#### Scenario: Peer refusal and hostile reply (C2)

- **WHEN** the matching fake relay refuses authentication or replies with secret-bearing arbitrary bytes
- **THEN** the connector closes that socket and reports a bounded locally controlled failure
- **AND** no TestClient protocol payload is sent.

### Requirement: Scoped relay auth preserves exact matching and listener-only readiness

Scoped transport SHALL authenticate only the exact configured host and port;
other direct addresses SHALL receive no relay preface. Listener-only readiness
SHALL connect and close without an auth preface, protocol payload or acquisition
of the TestClient manager session.

#### Scenario: Matching and nonmatching endpoints (C3)

- **WHEN** native consumers connect to the exact configured relay or a different direct host/port
- **THEN** only the relay receives its application's auth preface before protocol bytes
- **AND** destination/timeout and existing endpoint parsing semantics remain intact.

#### Scenario: Lifecycle readiness does not consume the target (C3)

- **WHEN** lifecycle or attachment readiness checks the configured relay listener
- **THEN** fake socket observations contain no authentication or protocol bytes
- **AND** the socket closes, while a nonmatching endpoint is not accepted as relay readiness.

### Requirement: Native transport scope follows application activation lifetime

The existing application activation SHALL bind and restore the immutable
configuration view for sync and awaited async calls. Nested, concurrent and
exceptional calls MUST NOT change process environment or leak configuration or
attachment identity. Outside composition, explicit legacy env mappings SHALL
remain supported; an unbound call with no mapping retains documented process
configuration behavior.

#### Scenario: Inner exception restores the outer caller (C4)

- **WHEN** A calls B, B raises, and A catches the error and invokes another native connection
- **THEN** A's exact settings and attachment are active immediately after B exits
- **AND** each request's destination, credential and native port match its owner, and the original caller restores after A exits.

#### Scenario: Interleaving and explicit legacy mapping (C4)

- **WHEN** bound async calls interleave or actual factory dispatch uses a worker thread, followed by an unbound explicit env adapter call
- **THEN** bound operations keep their own settings and the legacy call consumes only its mapping
- **AND** process environment and other applications' state remain unchanged.
