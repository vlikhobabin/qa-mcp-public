# bridge-bootstrap-client Specification

## Purpose
Define the qa-mcp Windows host-agent consumer for the reviewed root team Git
onboarding contract, including one-time bridge registration credentials,
protected restart state, bounded refresh and fail-closed compatibility rules.

## Requirements
### Requirement: Team bridge bootstrap grant client
The component SHALL consume contract version `1` from root
`f5-40-c10-team-git-onboarding-contract` at commit
`5afed8cf668e0c9bdbb44a1d167470e9b58295e5`, redeem a short-lived
server/project/user-bound onboarding grant once and retain only protected,
secret-free bridge restart state.

#### Scenario: Bound onboarding input registers and refreshes
- **WHEN** protected grant and Git authorization file references, the exact
  user/project/server binding and a supported HTTPS or loopback onboarding URL
  are supplied
- **AND** the Git authorization uses the pinned root contract's
  case-insensitive `Basic`, `Bearer` or `token` scheme
- **THEN** the client validates the strict grant, artifact descriptors,
  canonical payload digest, expiry and returned binding before using the
  one-time registration credential
- **AND** subsequent heartbeats and restarts request and redeem fresh one-time
  credentials without reusing the initial grant

#### Scenario: Restart state remains secret-free
- **WHEN** initial redemption or a later registration succeeds
- **THEN** atomic protected state retains only schema/source/version, binding,
  grant identifiers, counts, statuses and SHA-256 digests
- **AND** it retains no raw grant, Git authorization, registration credential
  or bridge callback token

#### Scenario: Refresh respects the root grant bound
- **WHEN** the observed grant lifetime and requested registration lease imply a
  refresh cadence
- **THEN** the client spaces refreshes to keep headroom below the root
  eight-active-grant bound
- **AND** fails before redeeming the initial grant if no safe cadence fits the
  registration TTL

### Requirement: Explicit-token bridge registration compatibility
The component SHALL preserve the existing explicit-token registration mode as
an advanced/recovery path and SHALL keep it mutually exclusive with onboarding
bootstrap inputs.

#### Scenario: Existing explicit configuration is used
- **WHEN** the complete existing registry URL, user, token-file, bridge-token
  file and endpoint configuration is supplied without onboarding inputs
- **THEN** registration and heartbeat behavior remain compatible with the
  existing explicit-token contract

### Requirement: Team bridge bootstrap grant client safety
The component MUST never place raw grants, Git authorization values,
registration credentials or bridge tokens in argv, logs, health, retained
captures or ordinary output and MUST never fall back to explicit, anonymous or
default credentials after onboarding is selected.

#### Scenario: Invalid or unsafe input fails closed
- **WHEN** source/version, identity, project, server, expiry, replay, revoke,
  descriptor, digest, permission, URL transport or response validation fails
- **THEN** the component stops that exchange without usable partial state and
  emits only a bounded non-secret diagnostic code

#### Scenario: Installer receives protected references
- **WHEN** onboarding mode is installed as a scheduled Windows task
- **THEN** the installer applies the protected ACL boundary to the grant, Git
  authorization, state directory, state file and staged executable
- **AND** renders only protected file paths and non-secret binding values in
  task arguments

#### Scenario: Direct Windows startup receives an unsafe ACL
- **WHEN** the grant, Git authorization or restart-state file has an inherited
  or non-allow DACL entry, or an allow entry outside the current user,
  LocalSystem and built-in Administrators
- **THEN** the client rejects that protected reference before exchange or
  restart-state use

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
