## ADDED Requirements

### Requirement: Bridge registration failures are actionable and secret-safe
The component SHALL preserve the configured registration URL verbatim while
reporting non-successful HTTP registration responses with bounded, secret-safe
diagnostics, and SHALL warn when an explicitly configured startup registry URL
has no endpoint path.

#### Scenario: Registry rejection exposes its HTTP status
- **WHEN** the configured registration endpoint returns a non-2xx response
- **THEN** authenticated health reports `state: "error"`, `last_error` as
  `registry-rejected-<status>`, and `last_http_status` as the integer HTTP
  status
- **AND** the host-agent log records that status and a response-body snippet of
  at most 512 bytes.

#### Scenario: Rejection diagnostics do not expose secrets or forge log lines
- **WHEN** a non-2xx response body is oversized, contains control characters,
  or contains the active registration credential or bridge token
- **THEN** the logged response-body snippet is redacted, bounded and escaped as
  one log entry
- **AND** neither credential appears in logs or authenticated health.

#### Scenario: Endpoint-less explicit registry URL warns without mutation
- **WHEN** startup receives a non-empty explicit `-registry-url` whose path is
  empty or slash-only
- **THEN** the host-agent emits one warning that a full registration endpoint
  URL is expected
- **AND** the client neither appends `/v1/bridges/register` nor otherwise
  rewrites the configured URL.

#### Scenario: Real registry router accepts the client request
- **WHEN** the real Go registration client is configured with the full
  `/v1/bridges/register` URL and sends its request through the root
  `team_registry.py` `do_POST` router on loopback
- **THEN** the router returns HTTP 201 and the client reports registered state
- **AND** the registry audit contains `bridge_registration` with `status: ok`
  for the authenticated principal.
