# qa-mcp-windows-host-agent-security Specification

## Purpose

Define the security boundary for the Windows host-agent that provides model-B desktop input and screenshot primitives to qa-mcp. The host-agent controls a logged-in desktop session, so installs and requests must fail closed by default.
## Requirements
### Requirement: Host-agent network exposure is scoped by default

The Windows host-agent installer SHALL NOT expose desktop-control endpoints to the whole LAN by default. A default install SHALL bind to loopback or create an inbound firewall rule scoped to an explicit Docker/host subnet. Any non-loopback bind MUST require an explicit remote-address allowlist or equivalent operator opt-in.

#### Scenario: Default install is locally scoped
- **WHEN** the host-agent is installed without an explicit remote-address allowlist
- **THEN** the listener/firewall combination does not accept arbitrary LAN clients
- **AND** the install script records the chosen local scope in its output or runbook guidance

#### Scenario: Non-loopback exposure requires an allowlist
- **WHEN** an operator configures a non-loopback bind address
- **THEN** the firewall rule is created with an explicit remote address or subnet
- **AND** the unsafe broad-LAN default is not silently restored

### Requirement: Host-agent token is not exposed in the service command line

The host-agent scheduled task SHALL obtain its bearer token from a protected token source such as an ACL-controlled file or environment source, not from a process command-line argument containing the token value.

#### Scenario: Scheduled task command hides the token
- **WHEN** the install script creates or updates the scheduled task action
- **THEN** the action command line does not include the bearer token value
- **AND** local process-list or WMI inspection cannot recover the token from the task action arguments

### Requirement: Host-agent endpoints fail closed behind authenticated access
The host-agent SHALL reject missing or wrong tokens on standalone TestClient
lifecycle, relay, desktop-control, and sensitive status endpoints, SHALL
compare accepted tokens in constant time, and SHALL reject hostile browser
origins unless explicitly allowed. Any unauthenticated health response SHALL
be minimal and MUST NOT expose binary SHA, foreground window title, HWND,
token state, or desktop-session details.

#### Scenario: Wrong or missing token is rejected
- **WHEN** a request to a protected host-agent endpoint omits `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns an unauthorized response
- **AND** no desktop action, screenshot capture or detailed status disclosure occurs

#### Scenario: Authenticated request succeeds
- **WHEN** a request supplies the configured token and an allowed origin
- **THEN** the endpoint executes its normal host-agent behavior

#### Scenario: Hostile origin is refused
- **WHEN** a browser-origin request supplies a non-allowlisted `Origin`
- **THEN** the endpoint rejects the request before performing any desktop-control action

#### Scenario: Unauthenticated status does not leak desktop state
- **WHEN** an unauthenticated client calls a public health/status endpoint
- **THEN** the response contains no binary SHA, foreground HWND, foreground title or other desktop-session details

### Requirement: Remote display backend uses bounded host-agent version compatibility

qa-mcp's remote display backend SHALL accept only explicitly supported
host-agent versions during `/version` handshake unless an operator supplies an
exact expected-version override. Unsupported versions MUST fail with a
structured `host-agent-version-mismatch` diagnostic before any desktop-control
or screenshot primitive is attempted.

#### Scenario: Current supported host-agent version is accepted by default
- **WHEN** qa-mcp is configured for remote-client mode without
  `QA_MCP_HOST_AGENT_EXPECTED_VERSION`
- **AND** the authenticated host-agent `/version` response reports a supported
  current version
- **THEN** `RemoteAgentBackend.handshake()` succeeds without requiring an
  environment override.

#### Scenario: Explicit expected-version override remains exact
- **WHEN** `QA_MCP_HOST_AGENT_EXPECTED_VERSION` is set to a specific version
- **AND** the authenticated host-agent reports a different version
- **THEN** `RemoteAgentBackend.handshake()` fails with
  `host-agent-version-mismatch`
- **AND** no host-agent desktop primitive is attempted.

#### Scenario: Unsupported default version is diagnosed honestly
- **WHEN** qa-mcp uses its default host-agent compatibility set
- **AND** the authenticated host-agent reports an unsupported version
- **THEN** the backend returns `host-agent-version-mismatch` with install
  guidance
- **AND** SHA-256 pinning, when configured, remains an exact independent check.

### Requirement: Host-agent resolves function keys for remote UI refresh

The Windows host-agent SHALL resolve named function keys `F1` through `F12` to
their corresponding Win32 virtual-key codes before sending authenticated
desktop input. Unsupported key names MUST still fail closed without sending an
input event.

#### Scenario: F5 is available for dynamic-list refresh
- **WHEN** an authenticated qa-mcp display-backend request sends key `F5`
- **THEN** the host-agent resolves the key as `VK_F5` (`0x74`)
- **AND** the request proceeds through the existing authenticated `SendInput`
  path.

#### Scenario: Function-key range is mapped consistently
- **WHEN** the host-agent resolves keys `F1` through `F12`
- **THEN** they map to contiguous Win32 virtual keys `0x70` through `0x7B`
- **AND** existing aliases such as `enter`, `escape`, navigation keys, letters,
  digits, and `F4` continue to resolve.

#### Scenario: Unknown key still fails closed
- **WHEN** an authenticated request supplies an unsupported key name
- **THEN** the host-agent returns an unsupported-key error
- **AND** no desktop input is sent for that key.

### Requirement: Host-agent sends refresh keys to the target window without foreground steal
The Windows host-agent SHALL deliver authenticated `F5` and `Escape` key
requests to the resolved 1C target window without requiring that window to
become the OS foreground window. The target-window key path MUST use the same
authenticated endpoint boundary and target-window resolution contract as the
existing display bridge.

#### Scenario: F5 refresh is sent to a non-foreground target
- **WHEN** an authenticated `/send_keys` request sends key `F5`
- **AND** the requested or default target resolves to a visible
  `V8TopLevelFrame*` 1C window that is not foreground
- **THEN** the host-agent sends key-down and key-up messages for `VK_F5` to that
  target window
- **AND** it does not call `SetForegroundWindow` for that request
- **AND** the response includes `ok: true` and the resolved target metadata.

#### Scenario: Escape clean-state sweep is sent to a non-foreground target
- **WHEN** an authenticated `/send_keys` request sends key `Escape`
- **AND** the target 1C window is visible but not foreground
- **THEN** the host-agent sends key-down and key-up messages for `VK_ESCAPE` to
  that target window
- **AND** it does not call `SetForegroundWindow` for that request.

#### Scenario: Other key sequences keep foreground semantics
- **WHEN** an authenticated `/send_keys` request contains a key or chord outside
  the focus-independent refresh-key allowlist
- **THEN** the host-agent uses the existing foreground-coupled input route for
  that request
- **AND** unsupported key names still fail closed before any desktop input is
  sent.

### Requirement: Foreground denial is reported as a structured host-agent result
The host-agent SHALL return a structured `foreground-denied` result instead of
a generic primitive failure or HTTP 500 when a display primitive still requires
the real foreground window and Windows denies foreground activation.

#### Scenario: Foreground-denied is not reported as HTTP 500
- **WHEN** an authenticated display primitive requires foreground activation
- **AND** the target window is resolved
- **AND** Windows denies `SetForegroundWindow`
- **THEN** the host-agent response includes `ok: false` and
  `error: "foreground-denied"`
- **AND** the HTTP status is not `500`
- **AND** the diagnostic distinguishes foreground denial from a missing target
  window or unreachable host-agent.

### Requirement: Host-agent version declares focus-independent refresh support
The host-agent and Python remote display backend SHALL advertise and accept a
bounded version family for the focus-independent refresh-key contract. The
default Python handshake MUST accept the new host-agent version before issuing
display primitives, while exact operator overrides and SHA-256 pinning remain
strict.

#### Scenario: New focus-independent host-agent version is accepted by default
- **WHEN** qa-mcp is configured for remote-client mode without
  `QA_MCP_HOST_AGENT_EXPECTED_VERSION`
- **AND** the authenticated host-agent `/version` response reports the
  focus-independent refresh-key version
- **THEN** `RemoteAgentBackend.handshake()` succeeds
- **AND** display primitives may be attempted through the host-agent.

#### Scenario: Exact version override remains strict
- **WHEN** `QA_MCP_HOST_AGENT_EXPECTED_VERSION` is set
- **AND** the authenticated host-agent reports any other version
- **THEN** `RemoteAgentBackend.handshake()` fails with
  `host-agent-version-mismatch`
- **AND** no host-agent desktop primitive is attempted.

### Requirement: Host-agent exposes authenticated 1C window and visible-cell diagnostics
The Windows host-agent SHALL expose bounded desktop diagnostics for qa-mcp
remote-client list reads behind the existing token and origin checks. Window
diagnostics MUST require a complete bridge-owned lifecycle target and return
only that exact PID/TPort-owned top-level 1C window with its class metadata;
they MUST NOT enumerate unrelated desktop windows. Visible-cell diagnostics
MUST execute only a fixed local UI Automation probe for the same resolved
target rather than arbitrary caller-supplied commands. When that target owns a
visible accessible descendant with a non-empty name and an allowlisted cell
control type, the diagnostic SHALL include that name in its bounded result
without retrying against a caption, wildcard, generic 1C, or foreground target.

#### Scenario: Lifecycle-bound window list includes exact class metadata
- **WHEN** an authenticated client calls `/window_list` with a complete
  bridge-owned lifecycle target
- **THEN** the response contains only that target's visible top-level 1C window
  with handle, title, class, PID, visibility and optional geometry
- **AND** no unrelated desktop window is enumerated.

#### Scenario: Visible-cell diagnostic is authenticated
- **WHEN** a request to the visible-cell diagnostic endpoint omits the
  host-agent token or supplies a wrong token
- **THEN** the endpoint returns an unauthorized response
- **AND** no UI Automation probe is executed.

#### Scenario: Visible-cell diagnostic targets the owned 1C frame
- **WHEN** an authenticated visible-cell diagnostic supplies a complete
  bridge-owned lifecycle target and omits an explicit window hint
- **THEN** the host-agent resolves only that lifecycle's visible
  `V8TopLevelFrame*` window
- **AND** it returns the resolved target metadata plus a bounded list of visible
  UI Automation text values.

#### Scenario: Exact empty-title target exposes its visible named descendant
- **WHEN** an authenticated visible-cell request resolves an exact
  process-owned empty-title `V8TopLevelFrame*` target
- **AND** that target contains a visible accessible descendant named
  `VisibleCell` with an allowlisted cell control type
- **THEN** the bounded result contains `VisibleCell`
- **AND** no caption, wildcard, generic 1C-window, or foreground fallback is
  attempted.

#### Scenario: Visible-cell diagnostic reports target misses
- **WHEN** the requested or default 1C target window cannot be found
- **THEN** the host-agent returns a structured `window-not-found` result
- **AND** it does not return an empty visible-cell list as if the target had no
  cells.

### Requirement: Host-agent bounds concurrent bridge execution

The Windows host-agent SHALL apply a shared in-flight concurrency cap to
TestClient lifecycle and bounded display/UIA endpoints after authentication.
The cap MUST cover `/testclient/{launch,status,stop}`, `/window_list`,
`/send_keys`, `/type`, `/click`, `/screenshot` and
`/uia/visible_list_cells`. A request that cannot acquire capacity MUST fail
closed before handler, process or driver work.

#### Scenario: N+1 bridge request is throttled before work
- **WHEN** the host-agent has reached its configured in-flight execution cap
- **AND** an authenticated caller sends another lifecycle or display request
- **THEN** the endpoint returns HTTP `429` with
  `execution-capacity-exhausted`
- **AND** no handler, subprocess or desktop driver work begins for that request

#### Scenario: Capacity is released after completion
- **WHEN** a protected endpoint acquires capacity and then returns success,
  failure, cancellation, or timeout
- **THEN** the in-flight slot is released
- **AND** a later valid request can acquire capacity normally

### Requirement: Host-agent failed-auth limiter evicts stale keys

The Windows host-agent SHALL remove failed-auth limiter entries whose retained
attempts have aged out of the limiter window. Eviction MUST prevent unbounded
map growth without weakening the existing wrong-token rate limit for currently
active failures.

#### Scenario: Expired failed-auth keys are removed
- **WHEN** failed-auth attempts for a client key are older than the configured
  limiter window
- **THEN** the limiter removes that key during maintenance
- **AND** the key no longer contributes to limiter map growth

#### Scenario: Active failed-auth attempts still rate limit
- **WHEN** a client key sends failed-auth attempts within the configured limiter
  window
- **THEN** the host-agent continues to reject attempts above the configured
  threshold with the existing rate-limit response

### Requirement: Host-agent window list preserves localized titles

The Windows host-agent SHALL return its lifecycle-bound `/window_list` entry
with a readable Unicode window title in JSON. Russian and other non-ASCII titles MUST
NOT be returned as mojibake, replacement-character noise, or host code-page
artifacts.

#### Scenario: Russian 1C title is readable
- **WHEN** an authenticated client calls `/window_list` for its owned lifecycle
  and that exact top-level window has the title `Клиент тестирования 3.1.5`
- **THEN** the JSON response contains that title as readable Unicode text
- **AND** the response does not contain mojibake such as `Ð` fragments for that
  title

#### Scenario: ASCII title remains unchanged
- **WHEN** an authenticated client calls `/window_list` and a visible top-level
  window has an ASCII title
- **THEN** the JSON response contains the same text content
- **AND** existing geometry fields and authentication behavior remain unchanged

### Requirement: Host-agent launches TestClient through a constrained detached endpoint

The Windows host-agent SHALL expose an authenticated sensitive endpoint for
detached 1C TestClient launch and status. The endpoint MUST construct the
`1cv8 ENTERPRISE ... /TESTCLIENT -TPort` command from semantic request fields,
resolve the platform executable from the configured catalog, reject arbitrary
executables or shell fragments, and start the process without a shell. On
Windows, newly spawned TestClient processes MUST be created from the active
interactive session primary token with the interactive desktop
`winsta0\\default`, rather than inheriting the long-running Task Scheduler
host-agent process token. The launch path MUST supply bounded GUI child
environment keys, rendered as a valid Windows environment block whose interior
NUL segment delimiters do not abort, corrupt or truncate the launch, and return
bounded launch metadata. For a newly spawned client, the endpoint MUST classify
readiness from process liveness and TPort liveness before returning: it MUST
report success only when the process is still alive and the TPort is listening
across a bounded persistence dwell, and it MUST return a structured failure when
the interactive launch context cannot be prepared, the process exits early, the
TPort drops during the dwell, or the TPort never becomes ready within the
bounded timeout.

#### Scenario: Authenticated TestClient launch returns ready process metadata
- **WHEN** an authenticated request supplies a valid connection string or file
  infobase path, user, TPort and optional safe startup flags
- **THEN** the host-agent resolves `1cv8` from the configured platform catalog
- **AND** on Windows it starts the TestClient with `CreateProcessAsUserW` using
  the active interactive session primary token and `winsta0\\default`
- **AND** it starts without a shell using bounded GUI child environment keys
- **AND** it waits until the process is alive and the TPort is listening
- **AND** it re-verifies that the process remains alive and the TPort remains
  listening after a bounded persistence dwell before returning success
- **AND** the response includes `ok: true`, spawned PID, `alive: true`,
  `listening: true`, `readiness: "ready"`, TPort, platform version or
  executable metadata, a redacted command summary, and bounded launch-context
  metadata that does not expose token handles or secret environment values.

#### Scenario: Bounded child environment is rendered without aborting on NUL delimiters
- **WHEN** the host-agent prepares the bounded GUI child environment for a
  TestClient launch and that environment contains one or more `KEY=VALUE`
  entries
- **THEN** the host-agent renders a Windows environment block that preserves
  each entry as a NUL-terminated UTF-16 segment followed by a final block
  terminator
- **AND** rendering the block does not panic, abort, corrupt or truncate the
  launch on the interior NUL segment delimiters
- **AND** the environment-block rendering is exercised by the offline Go suite
  independent of a Windows host.

#### Scenario: Launch rejects arbitrary execution inputs
- **WHEN** a request supplies an absolute executable path, shell fragment,
  unknown executable, invalid port, empty target, or NUL-containing argument
- **THEN** the endpoint returns a fail-closed response
- **AND** no process is spawned.

#### Scenario: Unauthorized launch is rejected before body validation
- **WHEN** a request to the TestClient launch endpoint omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** the request body is not validated, logged, or passed to any process.

#### Scenario: Passwords are redacted from diagnostics
- **WHEN** a launch request includes a TestClient password or a
  password-bearing connection string
- **THEN** returned command summaries, errors and logs do not include the secret
  value
- **AND** the response may report only that a password was supplied.

#### Scenario: Interactive session token is required on Windows
- **WHEN** the Windows host-agent cannot obtain or duplicate the active
  interactive session user token for a new TestClient launch
- **THEN** the endpoint returns `ok: false` with a structured launch-context
  diagnostic
- **AND** it does not fall back to direct Task Scheduler token inheritance
- **AND** no response claims the TestClient is attached or ready.

#### Scenario: Early process exit is not reported as ready
- **WHEN** the host-agent starts `1cv8` for a TestClient launch
- **AND** the process exits before its TPort becomes listening or during the
  bounded persistence dwell after its TPort first becomes listening
- **THEN** the endpoint returns `ok: false` with
  `error: "testclient-exited-early"`
- **AND** the response includes `alive: false`, `listening: false`, the PID
  when known, the redacted command summary, and bounded launch-context metadata
- **AND** the response does not claim the TestClient is attached or ready.

#### Scenario: Non-listening process is not reported as ready
- **WHEN** the host-agent starts `1cv8` for a TestClient launch
- **AND** the process is still alive when the bounded launch timeout expires
  or the requested TPort drops before the persistence dwell can prove readiness
- **AND** the requested TPort is not listening
- **THEN** the endpoint returns `ok: false` with
  `error: "testclient-not-listening"`
- **AND** the response includes `alive: true`, `listening: false`, the PID when
  known, the redacted command summary, and bounded launch-context metadata.

#### Scenario: Already-listening TPort can be reused
- **WHEN** an authenticated launch request targets a TPort that is already
  listening before a new process is spawned
- **THEN** the endpoint returns `ok: true`, `reused_existing: true`,
  `listening: true`, and `readiness: "ready"`
- **AND** no additional `1cv8` process is spawned.

#### Scenario: TestClient status reports bounded liveness metadata
- **WHEN** an authenticated client asks for TestClient launch status by TPort
  or PID
- **THEN** the host-agent reports process `alive` when a PID is supplied and
  reports whether the requested TPort is listening
- **AND** `listening: true` alone is not treated as proof that a supplied PID is
  alive
- **AND** unauthenticated clients cannot access the detailed status.

#### Scenario: Host-agent version declares interactive-session TestClient launch support
- **WHEN** qa-mcp performs the remote host-agent version handshake before
  `launch_test_client`
- **THEN** the reported host-agent version is accepted only if it belongs to the
  bounded compatibility family that includes honest TestClient launch readiness
  and Windows interactive-session launch support, unless an exact operator
  override is configured.

### Requirement: UIA visible-cells read tolerates a PowerShell CLIXML wrapper

The Windows host-agent `/uia/visible_list_cells` read SHALL return the visible
list cells even when the underlying PowerShell invocation prepends a
`#< CLIXML` progress/verbose wrapper to its redirected output.

#### Scenario: First-use module progress does not break the JSON parse

- **WHEN** the UIA PowerShell script's first `Add-Type` emits a "Preparing
  modules for first use" progress record that PowerShell serializes as a
  `#< CLIXML` wrapper around the JSON output
- **THEN** the host-agent SHALL suppress the progress stream and/or extract the
  JSON object from the wrapped output, and SHALL return `ok:true` with the real
  cells instead of a `primitive-failed` / invalid-JSON error

### Requirement: Windows TestClient launch uses a verified interactive task shell broker

The Windows host-agent SHALL launch a new 1C TestClient with its current token
only after its process session matches the active console session. The launch
SHALL retain the installed host-agent's InteractiveToken logon and Limited run
level without requiring `WTSQueryUserToken`, `SeTcbPrivilege` or a SYSTEM
principal. After that verification, it SHALL use a transient hidden
InteractiveToken task whose fixed action contains no TestClient credential. The
fixed broker SHALL receive the executable/argument request only over an
authenticated ephemeral loopback connection, and the task SHALL be removed
before launch returns.

#### Scenario: Normal installed principal launches a persistent client

- **WHEN** the Limited/Interactive host-agent receives a valid semantic
  TestClient launch request in an active user session
- **THEN** the fixed broker starts the resolved 1cv8 executable through the
  interactive Windows shell with the current user's normalized environment
- **AND** the broker returns no credential or PID handoff artifact
- **AND** the host-agent resolves the requested TPort listener owner, then
  reopens and reports that actual 1cv8 PID
- **AND** the returned PID, TPort and window remain live at the immediate and
  at-least-60-second probes.

#### Scenario: Interactive session verification fails

- **WHEN** no active console session exists or the host-agent runs in a
  different session
- **THEN** launch fails with `testclient-interactive-session-unavailable`
- **AND** no process, task, wrapper or PID handoff file is created.

### Requirement: Transient launch credentials are secret-safe

The Windows host-agent SHALL remove the exact transient launch task before
returning on success, failure or request cancellation. Production launch paths
SHALL invoke an idempotent cleanup boundary independent of the request context.
An explicit cleanup failure SHALL prevent a successful launch result and SHALL
leave an exact-name deferred retry armed.

#### Scenario: Cancellation and cleanup failure are proven on Windows

- **WHEN** the request context is canceled after an exact randomized QA-owned
  task has been registered
- **THEN** bounded cleanup independent of that context removes the exact task
- **AND** no wildcard or name-wide cleanup is used
- **AND** an injected first cleanup failure is returned as failure while the
  deferred fallback retries and removes that exact task
- **AND** the retained Windows-native result is bound to the same current source
  fingerprint as the delivered host-agent artifact and normal launch proof.

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

### Requirement: Host-agent stops only provider-owned launched TestClients

The Windows host-agent SHALL expose an authenticated TestClient stop route that
can terminate only a TestClient process previously launched and recorded by
that same host-agent process under an opaque lifecycle id. Stop requests with
unknown, stale, invalid, missing, or mismatched lifecycle ids MUST be refused
without terminating any process.

#### Scenario: Exact owned launched process is stopped

- **WHEN** `/testclient/launch` has returned a ready owned process PID and
  lifecycle handle id
- **AND** an authenticated caller invokes the stop route with that PID and
  lifecycle handle
- **THEN** the host-agent terminates only that recorded process
- **AND** the response includes a typed final state and sanitized lifecycle
  metadata.

#### Scenario: Started but not ready process remains owned for cleanup

- **WHEN** `/testclient/launch` starts a TestClient process
- **AND** the process remains alive but its TPort does not become listening
  before the launch timeout
- **THEN** the host-agent records that exact process under an opaque lifecycle
  id
- **AND** the launch failure response includes `owns_process: true` and a
  sanitized lifecycle handle with that id
- **AND** a later authenticated stop request with that lifecycle handle can
  terminate only that recorded process.

#### Scenario: Repeated stop returns final state

- **WHEN** a recorded TestClient process has already exited or has already been
  stopped through the host-agent
- **AND** the caller repeats the stop request for that lifecycle handle
- **THEN** the host-agent returns an idempotent already-finalized state
- **AND** no process-name, window-title, lock-file, or port-based broad cleanup
  is attempted.

#### Scenario: Unknown lifecycle handle is refused

- **WHEN** an authenticated caller invokes the stop route with a lifecycle handle
  id that was not issued and recorded by this host-agent process
- **THEN** the host-agent returns a structured `not-owned` refusal
- **AND** no process is terminated.

#### Scenario: PID-only stop is refused

- **WHEN** an authenticated caller invokes the stop route with a PID but without
  a lifecycle handle id
- **THEN** the host-agent returns a structured `missing_lifecycle_handle`
  refusal
- **AND** no process is terminated.

#### Scenario: Stop route remains authenticated

- **WHEN** a request to the TestClient stop route omits
  `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** no process lookup or termination is attempted.

### Requirement: Remote TestClient lifecycle evidence remains bounded

Host-agent TestClient lifecycle responses and retained qa-mcp evidence SHALL
include only sanitized lifecycle states, reason codes, PID/port values, launch
method, and process absence result. They MUST NOT include credentials, infobase
contents, screenshots, raw runtime logs, raw command lines, or unrelated 1C
process inventories.

#### Scenario: Stop evidence omits sensitive runtime data

- **WHEN** a remote TestClient launch/stop verification is retained
- **THEN** the evidence records the lifecycle route, typed state, PID/port, and
  absence or refusal result
- **AND** it excludes credentials, infobase contents, screenshots, raw runtime
  logs, and unrelated process inventories.

### Requirement: Host-agent binds display requests to an owned TestClient lifecycle

The Windows host-agent SHALL require a complete bridge-owned `client_target` on authenticated key, type, click, screenshot, window-list, and visible-list-cell requests. Before invoking a display driver primitive it MUST validate the target's lifecycle id, PID, listening TPort, ownership record, and current process-owned visible 1C window. An explicit window selector is only a compatibility hint and MUST NOT override or suppress that lifecycle binding. The host-agent SHALL resolve an empty-title `V8TopLevelFrame*` window by process/class rather than caption. Missing, non-owned, stale, recycled, mismatched, wildcard-only, or ambiguous targeting MUST fail closed and MUST NOT fall back to an explicit selector, the OS foreground window, or another 1C process.

#### Scenario: Owned lifecycle resolves an empty-title window

- **WHEN** an authenticated display request supplies a `client_target` whose lifecycle id, PID, and TPort match a live host-agent-owned TestClient
- **AND** that process owns a visible `V8TopLevelFrame*` window with an empty title
- **THEN** the host-agent resolves that exact process-owned window
- **AND** invokes the requested display primitive only for that target.

#### Scenario: Attach-only target cannot acquire display authority

- **WHEN** authenticated `/testclient/status` resolves an out-of-band TestClient listener to a PID and process-owned 1C window
- **THEN** it returns a bounded non-owning `client_target`
- **AND** a later display request is refused before driver work because the target has no bridge-owned lifecycle.

#### Scenario: Stale or mismatched target is refused before driver action

- **WHEN** the supplied lifecycle id, PID, or TPort no longer identifies the same live TestClient/window
- **THEN** the host-agent returns a structured target-missing, stale, or mismatch error
- **AND** no focus, input, click, screenshot, UIA, generic 1C-window, or foreground-window operation occurs.

#### Scenario: Explicit selector cannot override lifecycle target

- **WHEN** a request supplies both an explicit non-empty window selector and a complete bridge-owned `client_target`
- **THEN** the host-agent resolves only the lifecycle PID/TPort-owned 1C window
- **AND** ignores the selector as an authority source.

#### Scenario: Window-target capability prevents legacy downgrade

- **WHEN** qa-mcp has an active implicit `client_target`
- **AND** the host-agent does not advertise `testclient-window-target`
- **THEN** qa-mcp refuses the request before posting the display primitive
- **AND** the older host-agent cannot ignore the target and apply a weak fallback.

### Requirement: Host-agent reports typed desktop-session availability

Before invoking a screenshot, key, text, click, or visible-list-cell primitive, the Windows host-agent SHALL classify whether its interactive desktop is active. A locked, disconnected, or non-interactive session MUST produce a distinct structured error and MUST NOT invoke the driver primitive. Diagnostics SHALL contain only bounded state/reason fields and MUST NOT disclose usernames, raw session inventories, HWNDs, titles, screenshots, or logs.

#### Scenario: Locked desktop is refused

- **WHEN** the target TestClient identity is valid but the interactive desktop is locked
- **THEN** the host-agent returns `desktop-session-locked`
- **AND** does not capture or send input.

#### Scenario: Disconnected desktop is refused

- **WHEN** the target TestClient identity is valid but its interactive session is disconnected
- **THEN** it returns `desktop-session-disconnected`
- **AND** does not capture or send input.

#### Scenario: Non-interactive desktop is refused

- **WHEN** the host-agent is executing without access to an interactive input desktop
- **THEN** it returns `desktop-session-noninteractive`
- **AND** does not attempt a foreground fallback or driver action.

### Requirement: Windows TestClient launch distinguishes broker handoff from platform early exit

The Windows host-agent SHALL treat an authenticated shell-broker acknowledgement
as process-start provenance rather than lifecycle ownership. It SHALL bind an
owned lifecycle only to a live process that owns the requested TPort and matches
the verified interactive session. Launch failure metadata MUST remain bounded
and MUST NOT expose credentials, tokens or raw command lines.

#### Scenario: Broker fails before process acknowledgement

- **WHEN** task registration, authenticated rendezvous or shell start fails
  before a valid `started <pid>` acknowledgement
- **THEN** launch fails as a broker/start failure
- **AND** it does not claim that 1C accepted the launch or that a lifecycle is
  owned.

#### Scenario: Acknowledged process exits without a TPort owner

- **WHEN** the broker returns a valid process PID
- **AND** no process owns the requested TPort within the bounded launch wait
- **AND** the acknowledged PID is no longer alive
- **THEN** launch fails as `testclient-exited-early`
- **AND** reports the bounded PID, `alive:false`, `listening:false` and
  `readiness:"exited_early"` without a lifecycle handle.

#### Scenario: Listener owner differs from acknowledged PID

- **WHEN** the broker acknowledges a transient launcher PID and another process
  in the verified interactive session owns the requested TPort
- **THEN** the listener-owner PID becomes the authoritative lifecycle PID
- **AND** cleanup targets only that lifecycle handle and its exact transient
  task.

#### Scenario: Live acknowledged PID cannot be opened

- **WHEN** the acknowledged PID remains alive but the host-agent cannot open the
  required ownership handle and no TPort owner is available
- **THEN** launch fails with a bounded PID-handoff classification
- **AND** it does not classify the condition as a platform/file-infobase early
  exit.

#### Scenario: Live acknowledged PID never owns the requested TPort

- **WHEN** the host-agent opens and session-checks a process handle as its first
  operation after receiving the acknowledged PID, before waiting for task
  completion or unregistering the exact task
- **AND** the bounded listener-owner wait ends without a TPort owner while that
  retained process remains alive
- **THEN** the host-agent does not adopt that PID or continue through generic
  port readiness
- **AND** it terminates only through the retained acknowledged-process handle,
  without reopening the numeric PID, before returning
  `testclient-not-listening` without a lifecycle handle.

### Requirement: Disposable Windows TestClient proof uses a platform-restored infobase and exact cleanup

A cross-platform disposable TestClient proof SHALL create the Windows file
infobase through the target Windows platform and restore a portable backup, or
otherwise validate the copied format on Windows before launch. It MUST retain
before/after exact-owned inventory and MUST NOT clean unrelated tasks,
processes, ports, Docker resources or user data.

#### Scenario: Portable deployed proof is restored on Windows

- **WHEN** a disposable extension-bearing Linux proof is transferred to the
  authorized Windows station
- **THEN** a portable backup is restored into a Windows-created exact run-owned
  file infobase using the pinned platform build
- **AND** successful restore evidence precedes TestClient launch.

#### Scenario: UI mutation is recovered by exact stage cleanup

- **WHEN** qa-mcp creates a unique disposable catalog item in the restored proof
  infobase
- **THEN** retained evidence shows the item in the catalog UI and ignored
  screenshot evidence exists
- **AND** cleanup removes the exact restored stage and owned lifecycle resources
  so the item and infobase cannot survive the run.

#### Scenario: Cleanup proves a rerunnable contour

- **WHEN** the proof finishes or fails after staging
- **THEN** post-cleanup inventory shows the exact stage, scheduled tasks,
  host-agent/TestClient processes and proof listeners absent
- **AND** a fresh preflight confirms the same run namespace is clean without
  inspecting or removing unrelated user resources.
