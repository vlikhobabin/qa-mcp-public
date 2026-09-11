## MODIFIED Requirements

### Requirement: Host-agent probes file infobase markers without browsing
The Windows host-agent SHALL expose `POST /path/infobase` as an authenticated
read-only endpoint that checks only whether one caller-supplied configured file
infobase directory exists and whether one expected marker filename exists
inside it. The endpoint MAY include a best-effort active 1C process signal for
the same supplied path. The endpoint MUST NOT return directory listings, file
contents, customer data, ACLs, owners, timestamps, sizes, raw requested paths,
raw process command lines, process ids, executable paths, usernames, passwords,
or full connection strings.

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

#### Scenario: Active 1C process signal is secret-safe
- **WHEN** an authenticated request supplies a file infobase path and the
  host-agent can inspect active 1C process metadata
- **THEN** the response includes an `active_processes` object with a source,
  availability status, path-match support flag, matching process count, and
  bounded process-name metadata
- **AND** it does not include raw command lines, process ids, executable paths,
  the requested infobase path, usernames, passwords, or full connection strings.

#### Scenario: Active 1C process signal is unavailable
- **WHEN** the host-agent cannot inspect active 1C process metadata on the
  current host
- **THEN** the response marks the active-process signal as unavailable with a
  stable failure reason
- **AND** it does not claim that no active client exists.
