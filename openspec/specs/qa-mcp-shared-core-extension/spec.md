# qa-mcp-shared-core-extension Specification

## Purpose

Define the public composition, executor, result and tool-profile contracts that
allow standalone qa-mcp and downstream products to share one product-neutral
protocol and scenario core without source forks or reverse private dependencies.

## Requirements

### Requirement: MCP applications are composed from explicit public contracts
qa-mcp SHALL expose a public application factory that accepts explicit runtime
settings, executor and tool profile inputs without importing downstream product
code.

#### Scenario: Standalone application is constructed
- **WHEN** the standalone entrypoint constructs the MCP application
- **THEN** it supplies the public standalone executor and tool profile
- **AND** the server does not require Runtime Proxy, live-mcp or Team modules.

#### Scenario: Fake downstream executor is constructed offline
- **WHEN** a contract test supplies a fake executor implementing the public
  interface
- **THEN** the application is created and its selected tools execute through
  that fake without importing AI for 1C code.

### Requirement: Tool profiles register only supported tools
The application factory MUST register tools from an explicit named profile and
MUST NOT register omitted tools as structured-unavailable placeholders.

#### Scenario: Standalone and research profiles differ
- **WHEN** the standalone and research profiles are listed offline
- **THEN** each exposes its documented deterministic tool set
- **AND** research-only tools are absent from the standalone registry.

### Requirement: Shared operations own behavior semantics
MCP wrappers and scenario steps SHALL invoke common qa-mcp operation functions
for equivalent TestClient actions and SHALL preserve one result/error taxonomy.

#### Scenario: Equivalent action paths return the same verdict class
- **WHEN** an MCP tool and a scenario step execute the same fake operation
- **THEN** both use the shared operation implementation
- **AND** success, blocked, ambiguous and failure verdict classes agree.

### Requirement: Runtime state is isolated per application
Attachment, target, session and executor state MUST belong to an explicit
application/runtime context and MUST NOT leak between separately constructed
servers.

#### Scenario: Two application instances attach different endpoints
- **WHEN** two servers attach different fake TestClient endpoints
- **THEN** each operation uses only its own attachment
- **AND** stopping one context does not clear or mutate the other.

### Requirement: Public extension contracts remain product neutral
Public contract models MUST describe generic target identity, lifecycle,
protocol/display primitives, artifacts and operation results without requiring
private AI for 1C identifiers or transports.

#### Scenario: Public dependency boundary is scanned
- **WHEN** public package imports and build metadata are inspected
- **THEN** no reverse dependency on Runtime Relay, RPW, live-mcp, Team or a
  private AI for 1C package is present.

### Requirement: Standalone screenshot success retains readable image evidence
A successful screenshot through the unbound standalone application factory MUST
return a readable path whose file still contains the captured bytes after the
call. The unbound ledger's default policy MUST NOT be interpreted as admitted
project-bound raw-image deletion authority. Deliberate direct-call compatibility
MUST remain useful.

#### Scenario: Standalone screenshot uses default output
- **WHEN** the real unbound factory captures an image using default output selection
- **THEN** its returned path exists after the call and contains the exact captured bytes.

#### Scenario: Standalone screenshot uses explicit output
- **WHEN** the real unbound factory captures an image to an explicit relative or absolute output path
- **THEN** its returned readable path identifies that output and retains the exact image bytes.

### Requirement: Bound screenshot retention remains governed by admitted policy
Project-bound screenshot evidence MUST remain governed by the admitted evidence
root and sanitized or explicitly approved full_local policy. Standalone retention
MUST NOT grant raw-image retention to a bound application.

#### Scenario: Bound sanitized screenshot succeeds
- **WHEN** an exact admitted bound session captures an image under sanitized policy
- **THEN** the result retains safe artifact identity and digest without a raw path or image
- **AND** the raw captured image is removed from the admitted evidence location.

#### Scenario: Bound full_local screenshot succeeds
- **WHEN** an exact admitted bound session captures an image under approved full_local policy
- **THEN** only its authorized image remains in the admitted evidence root with matching content and digest.

### Requirement: Screenshot failures report evidence truthfully
Capture or required-cleanup failure MUST NOT claim successful readable evidence.
The failure path MUST preserve unrelated files and MUST NOT expose raw paths or
backend-secret prose in bound public results.

#### Scenario: Capture fails to produce readable evidence
- **WHEN** the synthetic screenshot backend fails or produces no readable image through a real factory tool
- **THEN** the tool reports failure without a successful readable artifact
- **AND** unrelated fixture files remain byte-identical.

#### Scenario: Sanitized cleanup fails
- **WHEN** required removal of a bound sanitized screenshot fails
- **THEN** the public result reports cleanup failure without a successful raw artifact/path
- **AND** unrelated files remain unchanged and the failed cleanup is not described as successful privacy enforcement.

### Requirement: Window-list primitive failures preserve operation verdicts
The trusted window-list adapter MUST translate backend failures into a typed
non-success operation result before public reconstruction. A typed display
exception MUST NOT become success with an empty value. Ordinary exceptions MUST
also remain failures through the composed operation.

#### Scenario: Registered window-list backend fails
- **WHEN** an admitted bound or unbound composed get_window_list call encounters a controlled typed display error or ordinary backend exception
- **THEN** the real default executor returns a failure using existing fixed error vocabulary
- **AND** the bound public result does not claim success or a successful empty inventory.

### Requirement: Window inventory and generic successful data remain distinct from failure
Successful window inventories MUST retain an exact count, including zero for an
empty inventory. Generic handlers MUST NOT infer failure from arbitrary successful
dictionary keys; translation belongs to the trusted primitive adapter.

#### Scenario: Inventory succeeds empty or nonempty
- **WHEN** the registered window-list backend returns an empty or nonempty inventory
- **THEN** the composed result succeeds with the exact count of windows returned.

#### Scenario: Generic successful value resembles an error
- **WHEN** an unrelated generic handler returns successful data containing error, ok or verdict-like keys
- **THEN** the generic executor preserves success and the original value
- **AND** an explicit typed operation result retains its supplied verdict.

### Requirement: Window-list failures retain bound privacy and direct compatibility
Bound window-list results MUST expose fixed safe failure diagnostics without
arbitrary backend prose, private UI strings, credentials or physical paths.
Deliberate direct legacy calls MUST retain their typed error dictionary and
successful inventory shape while composed adapters preserve typed verdicts.

#### Scenario: Bound error contains hostile diagnostic fields
- **WHEN** a local or Windows-host bound window-list backend raises an error with secret-bearing text or metadata
- **THEN** the serialized result contains only the existing fixed public failure code/message and admitted provenance
- **AND** backend secret fragments, captions and paths are absent.

#### Scenario: Direct legacy window inventory is called
- **WHEN** a deliberate direct legacy call receives a typed backend error or valid inventory
- **THEN** its documented error dictionary or inventory fields/count remain compatible.

### Requirement: Bound active-window reads expose a useful safe observation
Bound `read_active_window` through the default handler MUST derive its public
observation from actual `ActiveWindowContext` data. Its value MUST contain the
fixed `window_state` and exact bounded `marker_count` without raw window
references, markers, captions or physical paths. A successful read MUST NOT
reduce to an unconditional empty object.

#### Scenario: Actual window observation states are distinguishable
- **WHEN** a well-formed actual active-window DTO has a nonempty reference present in its marker list, no reference and no markers, or another unresolved reference/marker combination
- **THEN** its safe state is respectively `observed`, `missing` or `ambiguous`, with the exact marker count
- **AND** these are DTO observation states, without a new protocol uniqueness claim.

#### Scenario: An unsuccessful or malformed native observation is returned
- **WHEN** the actual default handler receives unsuccessful base status or malformed reference/marker types
- **THEN** the bound operation produces a fixed non-success result rather than fabricating a successful observed window.

### Requirement: Expected-window predicates are evaluated against internal window data
An explicitly requested bound window predicate MUST be evaluated against the
internal reference/markers before public redaction. Only a safe boolean outcome
may cross the public boundary; neither expected text nor raw observation data
MUST be echoed. Missing or ambiguous observation and invalid/empty expectations
MUST NOT become passing window assertions.

#### Scenario: Match and mismatch use the actual read
- **WHEN** an expected substring matches an observed window reference/marker or does not match it
- **THEN** the public assertion outcome is respectively true or false
- **AND** text occurring only in capture metadata, credentials or the public result envelope does not produce a match.
