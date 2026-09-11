## ADDED Requirements

### Requirement: Bridge advertises a bounded hidden direct-execute capability
The standalone bridge SHALL advertise
`testclient-hidden-desktop-direct-execute` through its existing versioned
capability document only when the authenticated TestClient launch/stop surface
can compose the published S1-S6 foundations. The capability MUST NOT authorize
a generic executable, command line, arbitrary file type, desktop input route or
API-major downgrade.

#### Scenario: Compatible capability is advertised
- **WHEN** the exact bridge build includes the closed S1-S6 adapter and existing
  authenticated launch/stop handlers
- **THEN** its capability document contains the direct-execute token without
  removing or changing existing standalone capability meanings

#### Scenario: Capability implementation is incomplete
- **WHEN** the adapter, typed receipt or exact lifecycle stop is unavailable
- **THEN** the bridge omits or refuses the capability before hidden worker or 1C
  process creation

### Requirement: Direct-execute request and receipt are closed
The existing authenticated launch route SHALL accept direct-execute input only
as an absolute Windows EPF/ERF path paired with a lowercase SHA-256 marker. It
MUST return a schema-valid closed S6 receipt bound to one current lifecycle and
MUST reject unknown, missing, malformed or conflicting fields before creating
the hidden desktop worker.

#### Scenario: Exact request returns a closed receipt
- **WHEN** an authenticated request supplies one admitted absolute EPF/ERF path,
  marker and the existing target/lifecycle inputs
- **THEN** the bridge runs native hidden `/Execute` and returns only the typed
  receipt and immutable lifecycle identity needed for independent validation

#### Scenario: Request is malformed or over-authorized
- **WHEN** the path is relative or has another extension, the marker is not
  lowercase SHA-256, fields conflict, or a generic command/input is supplied
- **THEN** the bridge rejects the request before process, desktop, action or
  cleanup ownership is created

### Requirement: Direct-execute stop preserves exact lifecycle ownership
The existing stop route MUST accept a direct-execute lifecycle only when PID,
native port, lifecycle id and immutable handle match the current bridge-owned
record. It SHALL remove only that worker/job/1C/listener/desktop state and MUST
NOT select a stop target from unvalidated receipt fields.

#### Scenario: Exact lifecycle is stopped
- **WHEN** stop receives the unchanged identity returned by the admitted launch
- **THEN** it removes only exact run-owned state and returns `stopped` or
  `already_stopped`

#### Scenario: Stop identity is stale or foreign
- **WHEN** PID, port, lifecycle id, handle or receipt binding differs from the
  current owned record
- **THEN** stop returns a bounded refusal without signaling another 1C process
  or cleaning unrelated bridge/runtime state
