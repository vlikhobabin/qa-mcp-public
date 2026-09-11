## MODIFIED Requirements

### Requirement: Host-agent endpoints fail closed behind authenticated access
The host-agent SHALL reject missing or wrong tokens on desktop-control,
host-path, and sensitive status endpoints, SHALL compare accepted tokens in
constant time, and SHALL reject hostile browser origins unless explicitly
allowed. Any unauthenticated health response SHALL be minimal and MUST NOT
expose binary SHA, foreground window title, HWND, token state, desktop-session
details, or filesystem probe results.

#### Scenario: Wrong or missing token is rejected for infobase path probe
- **WHEN** a request to `POST /path/infobase` omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** no request path is validated, probed, logged, or passed to any
  filesystem operation.

### Requirement: Host-agent probes file infobase markers without browsing
The Windows host-agent SHALL expose `POST /path/infobase` as an authenticated
read-only endpoint that checks only whether one caller-supplied configured file
infobase directory exists and whether one expected marker filename exists
inside it. The endpoint MUST NOT return directory listings, file contents,
customer data, ACLs, owners, timestamps, sizes, or raw requested paths.

#### Scenario: Existing file infobase marker is reported
- **WHEN** an authenticated request supplies an existing file infobase directory
  and marker `1Cv8.1CD`
- **THEN** the response includes `ok: true`, `response_id:
  "infobase-path-probe"`, `host_path_exists: true`, and
  `database_file_exists: true`
- **AND** the response does not include the raw requested path or any directory
  listing.

#### Scenario: Missing marker is actionable
- **WHEN** an authenticated request supplies an existing directory whose marker
  file is absent
- **THEN** the response includes `host_path_exists: true`,
  `database_file_exists: false`, and
  `failure_reason: "database_file_missing"`
- **AND** the response includes only the marker filename, not sibling entries.

#### Scenario: Missing host path is actionable
- **WHEN** an authenticated request supplies a host path that does not exist
- **THEN** the response includes `host_path_exists: false`,
  `database_file_exists: false`, and `failure_reason: "host_path_missing"`
- **AND** the endpoint does not attempt to list a parent directory.

#### Scenario: Path-like marker is rejected before filesystem access
- **WHEN** an authenticated request supplies a marker containing a path
  separator, NUL byte, absolute path, `.` or `..`
- **THEN** the endpoint returns a fail-closed validation error
- **AND** no marker filesystem probe is attempted.
