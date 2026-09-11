## ADDED Requirements

### Requirement: TestClient relay authenticates before fixed loopback access

When explicitly enabled, the Windows host-agent TestClient relay SHALL accept
only a bounded versioned preface authenticated with the configured bridge
secret, SHALL compare that secret in constant time, and SHALL dial only the
fixed loopback TestClient port after authentication succeeds.

#### Scenario: Authorized protocol session is relayed

- **WHEN** a client supplies the correct versioned preface and no other manager
  session is active
- **THEN** the relay connects to `127.0.0.1:<configured-TPort>`
- **AND** copies subsequent bytes transparently in both directions.

#### Scenario: Unauthorized or malformed preface is supplied

- **WHEN** a connection omits the preface, supplies a wrong token, exceeds the
  length/time bound or uses an unsupported version
- **THEN** it is closed with a bounded diagnostic before any loopback target
  connection is attempted
- **AND** no token value is logged or returned.

#### Scenario: TestManager session is already active

- **WHEN** a second authorized relay connection arrives while the one allowed
  session is active
- **THEN** it receives a bounded busy diagnostic
- **AND** no second target connection is opened.

#### Scenario: Relay is not configured

- **WHEN** the host-agent starts without a relay listen address
- **THEN** it exposes no TestClient relay listener
- **AND** regular HTTP/display/launch behavior is unchanged.
