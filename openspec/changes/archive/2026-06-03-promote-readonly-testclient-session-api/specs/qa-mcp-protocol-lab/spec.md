## ADDED Requirements

### Requirement: Read-only TestClient session API is reusable
The protocol lab SHALL expose a reusable package session API for direct
read-only communication with a running 1C TestClient without launching a 1C
TestManager instance.

#### Scenario: Package session sends a read-only query
- **WHEN** package code opens a `TestClientSession` to a configured
  `/TESTCLIENT` host and port
- **THEN** it can send generated read-only manager frames and read client
  responses
- **AND** the session cleanup closes only the socket it owns
- **AND** raw sent/received payloads are written only to ignored runtime paths
  when output capture is requested

### Requirement: Read-only query results preserve evidence status
The protocol lab SHALL return read-only query results with enough metadata to
distinguish accepted mappings from unresolved probes.

#### Scenario: Active form query result is returned
- **WHEN** a package read-only query returns active window or active form data
- **THEN** the result includes query id, status, evidence status, source
  capture/template information and response markers
- **AND** accepted active-window and active-form results can be linked to
  committed accepted-mapping evidence
- **AND** form element details or typed input remain marked unresolved until
  reviewed request hashes are accepted

### Requirement: Session API is verified offline before live use
The protocol lab SHALL verify read-only session behavior with offline tests
before requiring live TestClient execution.

#### Scenario: Session tests run without 1C runtime
- **WHEN** the package session tests run in an offline environment
- **THEN** fake socket or fixture tests cover send/read sequencing, response
  parsing and cleanup behavior
- **AND** live smoke evidence is optional unless the delivery explicitly runs
  against the configured TestClient
