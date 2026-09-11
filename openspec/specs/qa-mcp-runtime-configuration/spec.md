# qa-mcp-runtime-configuration Specification

## Purpose

Define the centralized runtime configuration contract for qa-mcp environment variables and defaults.
## Requirements
### Requirement: QA MCP environment settings are parsed through one accessor

The Python manager SHALL document and parse supported `QA_MCP_*` environment
variables through a centralized settings accessor. Modules MUST NOT duplicate
remote-client truth parsing or OData default constants after migration.

#### Scenario: Settings can be built from an explicit environment mapping

- **WHEN** tests call `Settings.from_env()` with an explicit environment mapping
- **THEN** the returned settings object reflects that mapping
- **AND** the test does not need to mutate process-global environment variables

#### Scenario: Remote-client truth parsing is centralized

- **WHEN** modules need to decide whether the runtime is a remote-client contour
- **THEN** they use the settings/accessor path
- **AND** the truthy and default false behavior matches the pre-refactor code

#### Scenario: OData defaults are defined once

- **WHEN** the OData client and regression command line need default host, port
  or path values
- **THEN** they import the defaults from the shared configuration path
- **AND** the effective default values remain unchanged

#### Scenario: Supported QA_MCP variables are documented together

- **WHEN** a maintainer needs to inspect supported qa-mcp environment variables
- **THEN** the settings module names each supported `QA_MCP_*` variable and its
  default behavior in one place

### Requirement: Doctor configuration is centralized and secret-safe

The qa-mcp runtime settings accessor SHALL centralize non-secret diagnostic
configuration used by `qa_mcp_doctor`, including proxy bearer-token environment
presence, host-agent address, host-agent token presence, client endpoint, and
COM doctor inputs. Settings and diagnostic results MUST expose presence booleans
or redacted summaries instead of secret values.

#### Scenario: Bearer-token presence is parsed from an explicit environment

- **WHEN** tests build settings from an explicit environment mapping
- **THEN** the settings can report whether `QA_MCP_BEARER_TOKEN` is present
- **AND** the settings object does not expose the bearer token value through a
  diagnostic field

#### Scenario: Host-agent token presence is reported without the token

- **WHEN** the host-agent token is configured
- **THEN** doctor settings expose that the token is present
- **AND** no result field contains the token value

#### Scenario: Missing optional doctor inputs produce skipped checks

- **WHEN** optional COM doctor or host-agent inputs are absent
- **THEN** `qa_mcp_doctor` marks dependent checks as skipped with stable reason
  codes
- **AND** the missing inputs are reported by environment-variable name rather
  than by a raw credential or local secret value

### Requirement: Doctor COM timeout is centrally configured
The qa-mcp settings accessor SHALL parse
`QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS` as the default timeout for
`qa_mcp_doctor` COM checks. CLI and MCP tool timeout arguments MUST override
the environment setting for debugging, and doctor diagnostics MUST expose only
the effective numeric timeout.

#### Scenario: Doctor consumes environment timeout by default
- **WHEN** `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS=90` is present
- **AND** `qa_mcp_doctor` runs without an explicit timeout argument
- **THEN** the COMConnector doctor probe receives `timeout_sec=90`
- **AND** the check data reports `timeout_sec=90` without secret values.

#### Scenario: Explicit doctor timeout overrides profile
- **WHEN** `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS=90` is present
- **AND** a caller passes `timeout_sec=1.5`
- **THEN** the COMConnector doctor probe receives `timeout_sec=1.5`
- **AND** the reported effective timeout is `1.5`.

### Requirement: Doctor status distinguishes required failures from optional gaps
`qa_mcp_doctor` SHALL return `ok=false` and `status=fail` when any required
check fails. Optional skipped probes SHALL keep `ok=true` and produce
`status=partial` when every required check passes. Doctor results MUST identify
which checks are required without exposing credentials.

#### Scenario: Optional probe skipped yields partial success
- **WHEN** all required doctor checks pass
- **AND** an optional effective-user probe is unavailable
- **THEN** the doctor result reports `ok=true`
- **AND** the doctor result reports `status=partial`
- **AND** the skipped optional check is marked as not required.

#### Scenario: Required auth failure remains failed
- **WHEN** the required bearer-token check fails
- **THEN** the doctor result reports `ok=false`
- **AND** the doctor result reports `status=fail`
- **AND** the failed check is marked as required.

### Requirement: Doctor reports workstation bsl-agent supervision separately
`qa_mcp_doctor` SHALL include a separate `bsl_agent_supervision` check derived from authenticated host-agent health. Disabled optional supervision SHALL be reported as a passing solo-mode state; configured ready supervision SHALL report bounded state, version, and restart count; configured non-ready supervision SHALL fail with an actionable readiness code.

#### Scenario: Solo mode is healthy
- **WHEN** host-agent health reports `bsl_agent.configured=false`
- **THEN** the doctor check passes with state `disabled` and does not make the overall doctor incomplete.

#### Scenario: Configured helper is ready
- **WHEN** host-agent health reports a ready configured helper
- **THEN** the doctor check passes and includes version and restart count without local paths.

#### Scenario: Configured helper is not ready
- **WHEN** host-agent health reports starting, backoff, failed-closed, or stopped for a configured helper
- **THEN** the doctor check fails with bounded lifecycle detail.

### Requirement: Workstation BSL helper launch is independent of service CWD
The host-agent SHALL launch the configured workstation BSL helper with its
working directory set to the helper binary directory, SHALL support an explicit
local child-output log, and SHALL close the parent log handle after each child
exit. The default readiness timeout SHALL be at least 480 seconds.

#### Scenario: Scheduled-task parent CWD is not writable
- **WHEN** host-agent runs from a service or scheduled-task CWD unrelated to the helper
- **THEN** the helper observes its own binary directory as CWD
- **AND** a valid fake helper reaches `ready` without using the parent CWD.

#### Scenario: Helper exits before opening its own log
- **WHEN** child-output capture is configured and the helper writes stderr then exits
- **THEN** the configured local log retains the bounded diagnostic
- **AND** the supervisor restarts without retaining an open parent file handle.

#### Scenario: Default cold warmup exceeds one minute
- **WHEN** no startup-timeout override is provided
- **THEN** both supervisor and host-agent CLI use a timeout of at least 480 seconds.

### Requirement: Doctor reports host-agent compatibility relationship
`qa_mcp_doctor` SHALL report the authenticated host-agent build version,
display protocol and bounded version relationship when the handshake succeeds,
without exposing credentials or local paths.

#### Scenario: Newer protocol-compatible agent is connected
- **WHEN** host-agent handshake accepts an unknown build through the supported protocol
- **THEN** `host_agent_http` passes
- **AND** its data reports build version, display protocol and
  `version_relationship: protocol-compatible`.

#### Scenario: Exact operator pin is active
- **WHEN** the configured expected version exactly matches the host-agent build
- **THEN** doctor reports `version_relationship: pinned`.

### Requirement: TestClient relay routing is explicit and endpoint-bound

qa-mcp SHALL enable relay authentication only when both a relay endpoint and
token are configured, and SHALL apply the preface only to connections whose
host and port exactly match that endpoint.

#### Scenario: Relay endpoint matches

- **WHEN** a protocol helper connects to the configured relay host and port
- **THEN** the shared connector authenticates the relay before exposing the
  socket to protocol code.

#### Scenario: Relay is absent or endpoint differs

- **WHEN** relay configuration is absent or a helper connects to another
  address
- **THEN** the connector uses direct TCP without sending a relay preface
- **AND** existing solo/Linux/local TestClient contours remain compatible.

#### Scenario: Partial relay configuration is supplied

- **WHEN** only endpoint or token is configured
- **THEN** startup/config validation fails closed with a bounded diagnostic
- **AND** no secret value appears in the diagnostic.

#### Scenario: Relay listener and TestClient TPort differ

- **WHEN** protocol sockets use a configured relay endpoint and
  `QA_MCP_HOST_AGENT_CLIENT_PORT` names the real local TestClient TPort
- **THEN** protocol connections continue through the authenticated relay
- **AND** host-agent display/window commands target the real TestClient TPort
- **AND** omitting the override preserves the existing client-port behavior.

### Requirement: Composed display clients use application settings

For an application built with explicit Settings, qa-mcp SHALL select local or
remote display behavior and construct host-agent clients solely from that
application's settings. Address, token, version/hash policy, window selector,
native client port and timeout MUST NOT be inherited from process environment
during a composed call. Existing documented fallback between host-agent client
port and application client port SHALL remain application-local.

#### Scenario: Conflicting factories and environment (C1)

- **WHEN** local and remote factories have distinct complete settings and execute interleaved display calls while process environment names a third host
- **THEN** each call uses its own backend, request destination, authentication, pins, window, native port and timeout
- **AND** local calls do not reach remote HTTP and remote calls do not select local X11.

### Requirement: Host lifecycle consumers share configuration and current ownership

Composed host-agent lifecycle calls SHALL use the same application-owned configuration as display calls.
This covers launch, status, stop and supported attach compatibility calls.
Each operation SHALL apply its current admitted attachment independently and
MUST retain existing target/session/generation and cleanup restrictions.

#### Scenario: Distinct applications and changing attachment (C2)

- **WHEN** two applications operate on distinct fake lifecycle identities and one changes its attachment
- **THEN** subsequent calls use the corresponding current identity and cannot retain another application's or an older session's target
- **AND** stopping one application does not signal or clear the other's session.

#### Scenario: Unproven project attach remains blocked (C2)

- **WHEN** a project-bound non-owned attach lacks the required observation
- **THEN** it remains blocked before host-agent or native invocation
- **AND** settings isolation does not create new attach authority.

### Requirement: Composed filesystem consumers use application-owned roots

A composed application MUST resolve workspace capture/template lookup and default
output roots from its active Settings. Explicit empty settings MUST use the
existing documented fallback without inheriting process-env or another
application's root. Separately admitted binding.evidence_root and retention
policy MUST keep their authority over project-bound evidence outputs.

#### Scenario: Factories have conflicting workspace settings

- **WHEN** two real factories have distinct workspace roots and process env names a third root
- **THEN** actual capture/output consumers use their owning application's intended paths
- **AND** no output is created under the other application's or process-only root.

#### Scenario: Bound evidence authority differs from workspace

- **WHEN** an admitted bound operation creates evidence and workspace differs from binding.evidence_root
- **THEN** its evidence remains governed by the admitted root and retention policy without workspace fallback.

### Requirement: Ownership marker creation and discovery share the owning root

Composed owned-launch marker placement and later stop/cleanup discovery MUST
resolve the same application-owned root despite process-env drift. Explicit
ownership root MUST take precedence over workspace-derived ownership fallback.
PID, process start, process group, target/session and unowned-process checks MUST
remain intact. Cleanup MUST NOT scan, delete or signal another application's
markers or processes merely because process configuration changes.

#### Scenario: Owned launch is cleaned after environment drift

- **WHEN** a fake owned launch creates its marker and subsequent real cleanup policy runs after env drift
- **THEN** discovery finds the same owning marker and cleans only its validated fake process/resources
- **AND** the other application's marker and process inventory remain unchanged.

#### Scenario: Foreign or reused process is requested

- **WHEN** only another application's marker exists, or PID/start/group identity mismatches
- **THEN** cleanup refuses to signal the process and preserves unrelated markers/resources.

### Requirement: Root precedence preserves context and explicit legacy behavior

Root resolution MUST preserve existing explicit ownership-root precedence,
workspace fallback and intentionally unbound direct environment behavior.
Nested or overlapping composed calls and exceptional exits MUST restore the
caller's configuration scope. Bound sanitized public results MUST NOT expose
raw root paths; useful unbound path/retention contracts MUST remain intact.

#### Scenario: Root scopes nest and an inner call fails

- **WHEN** one application invokes another and catches its error before resolving paths again
- **THEN** each observation pairs the exact owning application with its intended roots
- **AND** the outer caller's context and all unrelated state are restored.

#### Scenario: Root settings are empty or direct legacy calls are made

- **WHEN** active Settings omit roots or a deliberately unbound direct call resolves them
- **THEN** active absence uses documented fallback and only the legacy call reads environment defaults.

### Requirement: Explicit absence cannot fall back to environment

Composed availability checks and associated mode/configuration diagnostics SHALL use the active application's settings.
Intentionally missing host-agent
configuration MUST NOT select a process-configured host or local fallback.
Configuration failures SHALL retain bounded diagnostics without credentials.

#### Scenario: Empty remote configuration and backend failure (C3)

- **WHEN** an explicit remote application lacks an agent address while process environment supplies one, or a configured fake backend fails
- **THEN** absence is reported without a request to that process host or local fallback
- **AND** the public error identifies the correct application mode without authentication tokens or private configuration values.

### Requirement: Configuration isolation preserves context and explicit legacy adapters

Application settings and backend target state MUST remain isolated under
nested, interleaved async and exceptional calls. Implementation MUST NOT mutate
process environment to route a composed operation. Explicit environment-based
backend construction outside composition SHALL retain its compatibility contract.

#### Scenario: Exceptional exit restores the caller and legacy controls (C4)

- **WHEN** calls from distinct factories interleave or raise, followed by a caller using an explicit legacy env mapping outside composition
- **THEN** application context is restored and neither factory's settings or attachment has leaked
- **AND** the legacy adapter reads only its supplied mapping with existing pin, timeout and port behavior.

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
