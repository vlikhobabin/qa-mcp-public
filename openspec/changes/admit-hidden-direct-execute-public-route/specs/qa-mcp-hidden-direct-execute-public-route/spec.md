## ADDED Requirements

### Requirement: Public tool is project-bound and exposes no physical authority
The stable `open_external_processor` tool MUST retain its public name but SHALL
accept only a logical absolute EPF/ERF path and optional expected caption. It
MUST derive target, session, binding generation, endpoint, evidence policy and
cleanup identity from the admitted application context and MUST NOT expose
display, coordinate, timing, endpoint, retention or cleanup controls.

#### Scenario: Admitted project target invokes the logical tool
- **WHEN** a compatible standalone Windows target and current project binding
  invoke `open_external_processor` with an admitted EPF/ERF and optional caption
- **THEN** the operation derives every physical field from immutable context
  and begins capability negotiation without accepting caller targeting data

#### Scenario: Caller supplies hidden physical controls
- **WHEN** a caller supplies display, coordinate, endpoint, timeout, evidence
  root/policy or cleanup identity fields
- **THEN** schema or operation admission rejects the call before bridge launch,
  desktop action or filesystem evidence work

### Requirement: Windows success requires the exact hidden direct-execute receipt
The Windows route SHALL require the bridge capability
`testclient-hidden-desktop-direct-execute` and MUST validate the complete S6
typed envelope against independently supplied current-run identity. It MUST
accept only prompt-free or prompt-confirmed success whose S4/S5 identities,
marker, target/session/generation, PID, port, lifecycle and binding hash match
exactly.

#### Scenario: Exact prompt-free receipt is admitted
- **WHEN** the compatible bridge returns a schema-valid prompt-free S6 receipt
  for the exact current run and expected-caption marker
- **THEN** the tool reports bounded `form_opened` success and creates one
  exact-owned single-use cleanup lease

#### Scenario: Exact prompt-confirmed receipt is admitted
- **WHEN** one fresh exact-owned prompt is re-admitted, confirmed once and the
  resulting S4 post-state is bound in a valid prompt-confirmed S6 receipt
- **THEN** the tool reports bounded `form_opened` success without exposing UI,
  path, credential, handle or raw receipt content

#### Scenario: Capability or nested identity is invalid
- **WHEN** capability/version, marker, nested receipt, target, generation, PID,
  port, lifecycle or binding identity is missing, stale, foreign, replayed,
  malformed or ambiguous
- **THEN** the operation fails before public success and never invokes chooser,
  global input, foreground takeover, desktop switching or an older fallback

### Requirement: Cleanup is exact-owned and single-use
The route MUST revalidate the immutable S6 receipt immediately before cleanup,
atomically consume its caller-owned binding ledger and invoke only the injected
exact lifecycle stop once. Only `stopped` or `already_stopped` for the unchanged
identity SHALL count as successful cleanup; failure remains consumed and SHALL
NOT authorize an automatic retry or substituted stop.

#### Scenario: Exact lifecycle cleans once
- **WHEN** the admitted operation reaches success or a terminal owned failure
  with one unused unchanged cleanup binding
- **THEN** the binding is consumed before one exact stop callback and the public
  result reports the bounded cleanup outcome

#### Scenario: Stop is repeated or identity changes
- **WHEN** the same binding is reused concurrently/sequentially or any cleanup
  field changes after admission
- **THEN** cleanup is refused before a second callback and no foreign process,
  task, listener, desktop or session is signaled

### Requirement: Public result and retained evidence remain bounded
Public output SHALL use the fixed external-processor stage taxonomy and retain
only booleans, bounded counts, statuses and lowercase SHA-256 values. Raw UI,
paths, connection strings, credentials, OS handles, screenshots and exception
content MUST NOT cross the bridge/Python boundary or enter sanitized evidence.

#### Scenario: Successful result is sanitized
- **WHEN** the final exact receipt and cleanup validate
- **THEN** public output contains only bounded success/stage/caption/cleanup
  fields and no input path or private bridge payload

#### Scenario: Rejected result is sanitized
- **WHEN** launch, prompt, receipt, marker, post-state or cleanup validation
  fails
- **THEN** public output reports a fixed failure code/stage and retained
  evidence contains only hashes, counts and typed outcomes

### Requirement: Stable admission is gated by final exact-source proof
The tool MUST NOT be represented as stable until the final candidate remains
within `500` physical production additions from `312e914...`, preserves every
published S1-S6 source/test byte, passes the authorized exact-source Windows
matrix and receives a fresh critical `GO` followed by scoped publication.

#### Scenario: Final candidate satisfies every gate
- **WHEN** offline hostile/full/cross-build checks, prompt-off, two fresh
  prompt-on/recovery runs, Python-to-MCP proof, privacy, cleanup, LOC,
  predecessor and authorization checks all pass on final source
- **THEN** scoped publication may admit the tool in the stable standalone
  profile and record exact artifact hashes

#### Scenario: Any final gate is absent
- **WHEN** a proof is stale, a predecessor differs, runtime cleanup is
  incomplete, review is not `GO` or the LOC/authorization scope is exceeded
- **THEN** publication is forbidden and the stable route remains omitted
