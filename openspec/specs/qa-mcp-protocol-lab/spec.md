## Purpose

Define the local qa-mcp protocol research lab used to capture, replay and
classify the native 1C TestClient protocol.
## Requirements
### Requirement: Protocol evidence is reproducible

The project SHALL keep enough curated evidence to reproduce each protocol
claim without committing full raw runtime captures.

#### Scenario: Protocol claim is documented

- **WHEN** a document describes a new frame family, dynamic field or operation
  token
- **THEN** it references a capture id, frame range and normalized evidence file
- **AND** raw large capture files remain under ignored runtime directories

### Requirement: Python manager work is verified offline first

Reusable Python manager code SHALL have offline tests or compile checks before
live TestClient execution is required.

#### Scenario: Static check is run

- **WHEN** `scripts\check.ps1` is executed
- **THEN** Python source under `src` and `tools/protocol-research` is compiled
- **AND** pytest is run when it is installed

### Requirement: Runtime scripts clean only owned processes

Protocol capture and replay scripts SHALL clean only PIDs that they started or
can prove they own.

#### Scenario: Capture cleanup runs

- **WHEN** a protocol capture script exits
- **THEN** it stops only recorded owned PIDs
- **AND** unrelated `1cv8.exe` processes remain running

### Requirement: Protocol corpus cases have normalized evidence rows

The protocol lab SHALL define reviewed corpus case evidence as normalized rows
that map one marked 1C testing API operation to its protocol frame range,
dynamic fields, request/response signatures and replay status.

#### Scenario: Corpus case row is recorded

- **WHEN** a marked protocol case is promoted to reviewed evidence
- **THEN** the evidence row includes `case_id`, `api_call`, `frame_range`,
  request and response sizes, dynamic field descriptions, `normalized_hash`,
  response markers and `replay_status`
- **AND** the row references a compact evidence path under
  `docs/protocol-research/evidence/`
- **AND** raw capture payloads remain under ignored runtime directories

### Requirement: Protocol mappings require replay or probe status

The protocol lab SHALL record replay or Python-manager probe status before a
corpus mapping is treated as working protocol knowledge.

#### Scenario: Mapping is classified as accepted

- **WHEN** a corpus row claims that a 1C testing API operation maps to a
  protocol request shape
- **THEN** the row records whether replay or direct Python-manager probing
  accepted, rejected, partially accepted or timed out for that mapping
- **AND** missing replay evidence is visible as a non-accepted status

### Requirement: Semantic metadata does not replace wire evidence

The protocol lab SHALL treat help, metadata, source-authoring, BSL diagnostic,
platform-admin and read-only runtime evidence as semantic or support enrichment
for corpus rows, not as sufficient proof of native protocol behavior.

#### Scenario: Metadata is linked to a corpus row

- **WHEN** a corpus row includes semantic labels from platform help, metadata,
  source-authoring, BSL diagnostic, platform-admin or read-only runtime tooling
- **THEN** the row still references capture and normalization evidence for the
  protocol claim
- **AND** the row identifies semantic metadata as supporting context rather
  than replay proof

### Requirement: Semantic source inventory is documented

The protocol lab SHALL document approved semantic and support sources before
using them to label corpus evidence, including the provider owner, source build
or version when known, external workspace or snapshot boundary, allowed use and
compact readiness evidence or provider-gap record. Current approved support
routes are `help-mcp`, `meta-mcp`, `config-mcp`, `bsl-mcp`, `admin-mcp` and
`live-mcp`; retired `edt-mcp` references are historical evidence only.

#### Scenario: Semantic source is approved for corpus labeling

- **WHEN** help, metadata, source-authoring, BSL diagnostic, platform-admin or
  read-only runtime context is used to select or label a protocol corpus case
- **THEN** the source inventory records the provider id, source purpose,
  source location or external boundary, readiness evidence path and owner
- **AND** generated EDT workspaces, infobase exports, raw provider payloads and
  local runtime output remain outside reviewed git changes

#### Scenario: Semantic source is unavailable

- **WHEN** an optional semantic or support source cannot be reached or cannot
  inspect the needed object model
- **THEN** the source inventory or compact evidence records the provider gap,
  affected semantic use, owner route and residual risk
- **AND** raw TCP capture, normalization, replay and direct Python-manager
  probing remain usable without that source

### Requirement: Corpus semantic mappings link to primary evidence

The protocol lab SHALL keep semantic mappings between corpus case ids and
help/meta/EDT references as compact supporting artifacts that identify the
primary wire evidence path, mapping status, semantic source and unresolved
reason when applicable.

#### Scenario: Corpus case receives a semantic mapping

- **WHEN** a reviewed corpus case is linked to a form, element, object-model
  term or help topic from help, metadata or EDT tooling
- **THEN** the semantic mapping records the `case_id`, target family or object,
  provider source, mapping status and primary protocol evidence path
- **AND** the mapping states that capture frames, normalized hashes and
  replay/probe status remain the protocol evidence of record

#### Scenario: Corpus case cannot be mapped

- **WHEN** a corpus row has no stable metadata object, form element, GUID,
  name or help topic that can be linked safely
- **THEN** the semantic mapping records the row as unresolved or partial with a
  reason and residual risk
- **AND** the unresolved mapping remains visible instead of being omitted from
  reviewed coverage notes

### Requirement: Protocol corpus runner records marked read-only cases

The protocol lab SHALL provide a Windows-native corpus runner that executes
short marked read-only 1C testing API cases and preserves case markers with
the captured TestManager/TestClient traffic.

#### Scenario: Marked corpus case is captured

- **WHEN** the corpus runner executes a read-only active-window, active-form
  or form-element case
- **THEN** the capture output includes case markers sufficient to derive the
  manager-to-client and client-to-manager frame range for that case
- **AND** the capture cleanup records and stops only PIDs created by the run

### Requirement: Corpus runner generates normalized case evidence

The protocol lab SHALL generate compact normalized evidence rows for corpus
cases without committing raw capture streams.

#### Scenario: Corpus evidence is generated

- **WHEN** a corpus capture is analyzed
- **THEN** the runner or analyzer writes a reviewed case row with `case_id`,
  `api_call`, `frame_range`, `normalized_hash`, dynamic fields,
  `operation_token`, `response_markers` and `replay_status`
- **AND** compact reports are linked from
  `docs/protocol-research/evidence-index.md`
- **AND** raw capture binaries and traffic logs remain under ignored runtime
  directories

### Requirement: Corpus mappings can be confirmed without TestManager

The protocol lab SHALL attempt replay or direct Python-manager confirmation
for corpus mappings whose frame family is supported by existing replay
tooling.

#### Scenario: Replay confirmation is attempted

- **WHEN** a corpus case produces a supported read-only request family
- **THEN** the runner records the result of replaying or probing the mapping
  against a live TestClient without a 1C TestManager instance
- **AND** the case row distinguishes accepted mappings from rejected, timeout,
  partial or unsupported mappings

### Requirement: Read-only corpus matrix covers common form element families

The protocol lab SHALL define an expanded read-only corpus matrix for common
1C form element families before action or write protocol cases are accepted.

#### Scenario: Expanded element case is captured

- **WHEN** a corpus case targets a supported read-only element family such as
  button, table, command bar, page, label, checkbox or typed input field
- **THEN** the case row identifies the element family, 1C testing API call,
  UI target, expected state and safety class
- **AND** the case row records frame ranges, normalized hash, dynamic fields,
  operation token, response markers and replay status

### Requirement: Missing element families are explicit corpus gaps

The protocol lab SHALL make unsupported or unavailable read-only element
families visible instead of silently omitting them from the matrix.

#### Scenario: Element family is unavailable in the current lab form

- **WHEN** the expanded matrix includes an element family not present in the
  current TestClient fixture
- **THEN** the corpus evidence records the family as `unsupported` or
  `pending`
- **AND** the reviewed notes identify whether a new fixture, metadata mapping
  or Python-manager probe is needed before acceptance

### Requirement: Controlled read-only fixture plans cover missing element families

The protocol lab SHALL maintain a controlled fixture coverage plan before
promoting new read-only element-family mappings for `Button`, `Table`,
`CommandBar`, `Page`, `Label` or `CheckBox`.

#### Scenario: Missing family is planned for coverage

- **WHEN** a missing read-only element family is selected for fixture coverage
- **THEN** the fixture plan records the family, case id, target form or
  fixture source, expected state, expected response markers, safety class,
  planned evidence paths and provider owner
- **AND** any generated EDT workspace, infobase export, raw fixture output or
  raw capture remains outside reviewed git changes

#### Scenario: Missing family cannot be covered yet

- **WHEN** a missing read-only element family cannot be safely represented in
  the current lab fixture
- **THEN** the fixture plan records the family as blocked or out of scope with
  a reason, owner route and residual risk
- **AND** the corpus matrix keeps the family visible as unsupported or pending
  until compact capture and replay/probe evidence exists

### Requirement: Fixture-derived corpus cases remain read-only and evidence-backed

The protocol lab SHALL feed controlled fixture surfaces into corpus capture
through explicit read-only case definitions and SHALL require compact wire
evidence plus replay or direct Python-manager proof before fixture-derived
rows become accepted mappings.

#### Scenario: Fixture case is added to the corpus

- **WHEN** a controlled fixture surface is added to a corpus manifest or seeded
  matrix
- **THEN** the case definition records the read-only API call, element family,
  UI target, expected state, expected response markers and safety class
- **AND** the case excludes clicks, text input, command execution, navigation
  with business-data mutation and other write/action semantics

#### Scenario: Fixture-derived mapping is promoted

- **WHEN** a fixture-derived corpus row is considered for accepted mapping
- **THEN** the reviewed evidence records capture id, frame range, normalized
  hash, dynamic fields, operation token, response markers and replay or direct
  Python-manager status
- **AND** help, metadata or EDT labels remain semantic support rather than
  proof of native protocol behavior

### Requirement: Controlled fixture source readiness is reviewed before capture

The protocol lab SHALL document the controlled source boundary for read-only
fixture cases before those cases are used for live corpus capture.

#### Scenario: Fixture source is ready for a family

- **WHEN** a planned fixture family is prepared for live capture
- **THEN** the reviewed source evidence records the case id, element family,
  external source boundary, target form or element, expected read-only state
  and provider validation summary
- **AND** generated EDT workspaces, infobase exports, provider payloads and
  runtime logs remain outside reviewed git changes

#### Scenario: Fixture source is not ready for a family

- **WHEN** a planned fixture family cannot be represented safely in the
  controlled source
- **THEN** the reviewed source evidence records the family as `blocked`,
  `pending` or `partial` with owner route, unresolved reason and residual risk
- **AND** no later corpus row for that family is accepted from inferred
  metadata alone

### Requirement: Fixture read-only capture records compact wire evidence

The protocol lab SHALL generate compact corpus evidence for available
controlled read-only fixture cases before those cases are classified.

#### Scenario: Fixture case is captured

- **WHEN** a controlled fixture case is run through the Windows-native corpus
  capture path
- **THEN** the reviewed row records case id, element family, capture id, frame
  range, request and response sizes, normalized hash, dynamic fields,
  operation token, response markers and replay or probe status when available
- **AND** raw capture payloads and process logs remain under ignored runtime
  paths

#### Scenario: Fixture capture cannot produce a row

- **WHEN** the fixture source, runner, live 1C runtime or provider support
  cannot produce reviewed wire evidence for a family
- **THEN** the compact evidence records `pending`, `partial`, `unsupported`,
  `timeout`, `rejected` or another explicit unresolved status with reason
- **AND** the row is not accepted from fixture plan or metadata evidence alone

### Requirement: Fixture probes remain read-only

The protocol lab SHALL keep fixture direct probes and replay confirmation
limited to read-only TestClient queries.

#### Scenario: Direct probe is run for a fixture family

- **WHEN** a direct Python-manager probe is used to confirm a fixture mapping
- **THEN** the probe evidence records query, family, expected response markers,
  status and evidence path
- **AND** the probe excludes clicks, command execution, text input, checkbox
  toggles, table edits and other write/action semantics

### Requirement: Fixture evidence is classified before publication

The protocol lab SHALL classify every planned controlled read-only fixture
family before publishing accepted fixture mappings.

#### Scenario: Fixture family has complete evidence

- **WHEN** repeated fixture corpus rows have stable non-null normalized hashes
  and accepted replay or direct-probe evidence for the expected operation
- **THEN** classification evidence may mark the family as `accepted`
- **AND** the evidence records capture ids, frame ranges, request/response
  sizes, dynamic fields, operation tokens, response markers, probe status and
  reviewed evidence paths

#### Scenario: Fixture family has incomplete evidence

- **WHEN** fixture evidence lacks a frame range, stable normalized hash,
  response marker, replay/probe confirmation or source readiness
- **THEN** classification evidence marks the family as `partial`, `pending`,
  `unsupported`, `timeout`, `rejected` or `blocked` with unresolved reason
- **AND** the family is not published as an accepted mapping

### Requirement: Fixture classification does not rewrite historical evidence

The protocol lab SHALL write fixture classification results under a new
reviewed evidence id instead of modifying historical corpus rows in place.

#### Scenario: Fixture comparison is generated

- **WHEN** fixture corpus runs are compared or classified
- **THEN** compact comparison, normalizer or accepted-mapping outputs use a new
  evidence directory
- **AND** raw capture streams, raw probe output and historical corpus rows
  remain unchanged

### Requirement: Fixture mapping publication is evidence-gated

The protocol lab SHALL publish controlled read-only fixture mapping results
only from reviewed classification evidence.

#### Scenario: Accepted fixture mapping is published

- **WHEN** a fixture family is classified as accepted
- **THEN** the published accepted-mapping docs link capture ids, frame ranges,
  normalized hashes, dynamic fields, operation tokens, response markers,
  replay or probe status and reviewed evidence paths
- **AND** raw captures and full probe output remain outside reviewed git
  changes

#### Scenario: Fixture family remains unresolved

- **WHEN** a fixture family is classified as `partial`, `pending`,
  `unsupported`, `timeout`, `rejected` or `blocked`
- **THEN** publication keeps the unresolved status, reason and next owner
  visible in corpus, comparison or evidence-index notes
- **AND** the family is not listed as an accepted mapping

### Requirement: Fixture publication preserves evidence lineage

The protocol lab SHALL preserve source, corpus, probe, comparison and accepted
mapping evidence lineage for fixture-derived rows.

#### Scenario: Fixture evidence is indexed

- **WHEN** fixture evidence is published
- **THEN** the evidence index links the source summary, corpus output, probe
  output, comparison/classification output and accepted-mapping output that
  were produced
- **AND** each link points to compact reviewed evidence rather than ignored
  runtime payloads

### Requirement: Expanded corpus evidence remains read-only

The protocol lab SHALL keep the expanded corpus matrix limited to read-only
queries until action and write semantics have separate recovery evidence.

#### Scenario: Proposed case would mutate business data

- **WHEN** a candidate case requires input, click, command execution or other
  business-data mutation
- **THEN** it is excluded from the read-only matrix
- **AND** it is routed to a later safe-action or mutation-specific card

### Requirement: Corpus cases are compared across repeated captures

The protocol lab SHALL compare repeated corpus captures for the same case set
before treating expanded read-only mappings as stable dictionary entries.

#### Scenario: Repeated corpus rows are compared

- **WHEN** two or more corpus runs contain the same `case_id`
- **THEN** the comparison records capture ids, evidence paths, normalized
  hashes, request/response sizes, operation tokens and replay statuses for
  that case
- **AND** stable and divergent values are reported separately

### Requirement: Repeatability gaps are visible

The protocol lab SHALL report missing cases or unsupported replay outcomes in
repeatability evidence instead of hiding them.

#### Scenario: Repeated capture is missing a case

- **WHEN** a comparison input does not contain a case that exists in another
  run for the same matrix
- **THEN** the comparison report marks that case as a gap
- **AND** the report keeps the mapping out of accepted stable entries until
  the gap is explained

### Requirement: Divergence feeds dynamic-field investigation

The protocol lab SHALL route unexplained normalized-hash divergence to a
dynamic-field investigation path.

#### Scenario: Normalized hash diverges for the same case

- **WHEN** repeated captures have the same `case_id` but different
  `normalized_hash` values
- **THEN** the comparison report lists candidate differing fields or marks the
  case for normalizer investigation
- **AND** the mapping remains non-stable until the divergence is explained

### Requirement: Dynamic-field normalizer changes are evidence-backed

The protocol lab SHALL add dynamic-field normalizer rules only when reviewed
evidence shows why the bytes are safe to replace.

#### Scenario: New dynamic range is normalized

- **WHEN** a new dynamic range is added to corpus normalization
- **THEN** reviewed evidence records the range name, source class, direction,
  offset or locator, length, replacement label and observed values
- **AND** the evidence links to repeated captures or replay/probe results that
  justify the replacement

### Requirement: Normalizer reports before and after hash behavior

The protocol lab SHALL report how a normalizer change affects request-shape
hashes for repeated corpus cases.

#### Scenario: Normalizer rule stabilizes a repeated case

- **WHEN** a new normalizer rule changes divergent hashes into a stable
  normalized hash
- **THEN** the compact evidence records the before-hash set, after-hash set
  and cases affected
- **AND** response markers or replay/probe status still support the mapping

### Requirement: Ambiguous dynamic ranges remain visible

The protocol lab SHALL keep ambiguous byte or text ranges visible instead of
normalizing them as accepted dynamic fields.

#### Scenario: Candidate range may be semantic

- **WHEN** a differing range cannot be proven session-specific
- **THEN** the analyzer marks it as ambiguous or pending investigation
- **AND** any affected mapping is not promoted as a stable accepted dictionary
  entry

### Requirement: Corpus rows can link direct-probe evidence

The protocol lab SHALL allow reviewed corpus rows to reference compact direct
Python-manager probe evidence without embedding raw probe output.

#### Scenario: Direct-probe result is attached to a corpus row

- **WHEN** a reviewed corpus row uses direct Python-manager probing as replay
  confirmation
- **THEN** the row records or links the compact probe evidence path, probe
  status, probe query or case family and response markers needed for review
- **AND** raw probe output, raw TCP traffic and local process logs remain under
  ignored runtime directories

### Requirement: Accepted read-only mappings require stable wire evidence and probe proof

The protocol lab SHALL promote a read-only corpus row to `accepted` only when
repeated normalized request evidence and replay or direct-probe proof support
the same operation.

#### Scenario: Stable repeated row is promoted

- **WHEN** repeated corpus rows for the same read-only `case_id` have the same
  non-null `normalized_hash`
- **AND** the row has accepted direct-probe or replay evidence for the expected
  operation and response markers
- **THEN** comparison evidence may classify the mapping as a stable accepted
  dictionary entry
- **AND** the accepted row retains capture ids, frame ranges, request/response
  sizes, dynamic fields, operation token, response markers and evidence paths

### Requirement: Direct-probe gaps remain explicit

The protocol lab SHALL keep direct-probe rows with missing request-frame or
hash evidence visible as unresolved evidence instead of promoting them.

#### Scenario: Direct probe returns useful data without reviewed request hash

- **WHEN** direct Python-manager probing returns useful read-only response
  data but the reviewed corpus row lacks request-frame or `normalized_hash`
  evidence
- **THEN** the row remains `partial`, `pending`, `incomplete_hash` or another
  explicit non-accepted status
- **AND** the row records the unresolved reason and the compact evidence path
  needed for the next investigation pass

### Requirement: Probe-confirmed rows are promoted by repeatability comparison

The protocol lab SHALL allow repeatability comparison to classify stable
read-only rows as accepted when compact replay or direct-probe evidence
confirms the same operation.

#### Scenario: Stable row has accepted probe evidence

- **WHEN** two or more reviewed corpus inputs contain the same read-only
  `case_id` with the same non-null `normalized_hash`
- **AND** the row has accepted replay or direct Python-manager probe evidence
  linked to the same operation and expected response markers
- **THEN** the comparison report classifies the mapping as stable accepted
- **AND** the report lists the accepted case id, source captures, probe
  evidence path and normalized hash

### Requirement: Probe promotion preserves unresolved rows

The protocol lab SHALL keep rows without complete request-hash evidence or
unambiguous probe joins out of accepted comparison results.

#### Scenario: Probe evidence is useful but request evidence is incomplete

- **WHEN** a direct Python-manager probe returns useful data for a read-only
  family
- **BUT** the reviewed corpus row lacks request-frame or non-null
  `normalized_hash` evidence
- **THEN** comparison evidence records the row as `incomplete_hash`,
  `partial`, `pending` or another explicit non-accepted class
- **AND** the report records the unresolved reason for the next protocol pass

### Requirement: Accepted mapping evidence is compact and reproducible

The protocol lab SHALL generate compact accepted-mapping evidence without
committing raw captures or full probe output.

#### Scenario: Accepted mapping report is generated

- **WHEN** accepted read-only mappings are produced from repeated corpus rows
  and probe evidence
- **THEN** the reviewed evidence records capture ids, frame ranges, request
  and response sizes, normalized hashes, dynamic fields, operation tokens,
  response markers, probe status and evidence paths
- **AND** raw capture streams, process logs and full probe outputs remain
  under ignored runtime directories

### Requirement: Python protocol package contract is evidence-aware

The protocol lab SHALL expose read-only `qa_mcp.protocol` package contracts
that distinguish accepted mappings from unresolved protocol probes.

#### Scenario: Package operation descriptors are reviewed

- **WHEN** package code exposes a read-only TestClient operation descriptor
- **THEN** the descriptor records `case_id`, operation family, safety class,
  acceptance status and evidence path
- **AND** accepted descriptors retain the accepted normalized hash and source
  capture or comparison evidence
- **AND** unresolved descriptors retain an explicit reason such as
  `incomplete_hash`, `pending`, `partial` or `unsupported`

### Requirement: Package contract preserves the read-only boundary

The protocol lab SHALL keep promoted Python manager package APIs limited to
read-only TestClient operations until action/write evidence is accepted.

#### Scenario: Candidate operation can mutate UI or business data

- **WHEN** a package operation would click, input text, execute a command or
  mutate business data
- **THEN** it is excluded from the read-only protocol package contract
- **AND** the operation is routed to a later safe-action or mutation-specific
  card

### Requirement: Package contract is offline verifiable

The protocol lab SHALL make the package contract importable and testable from
committed compact evidence without requiring a live 1C runtime.

#### Scenario: Contract tests run without TestClient

- **WHEN** offline package tests inspect the read-only operation contract
- **THEN** accepted active-window and active-form mappings can be verified
  against committed compact evidence
- **AND** raw captures, raw probe output and process logs are not required

### Requirement: Protocol frame primitives live in the package

The protocol lab SHALL provide package-owned primitives for rendering and
summarizing accepted read-only TestClient protocol frames.

#### Scenario: Template frame is rendered offline

- **WHEN** package code renders a captured manager-frame template with dynamic
  ACK GUID, sequence, nonce or managed-form values
- **THEN** the rendered payload and replacement metadata are returned without
  opening a network socket
- **AND** the replacement metadata records field name, offset, length,
  original bytes and replacement value

### Requirement: Capture bootstrap loading is reusable

The protocol lab SHALL expose reusable package code for reading the captured
bootstrap frames required before generated read-only UI queries.

#### Scenario: Bootstrap fixture is loaded

- **WHEN** package code loads a curated bootstrap fixture or approved capture
  source
- **THEN** it separates manager-to-client and client-to-manager frames
- **AND** it rejects incomplete bootstrap data with a clear error
- **AND** tests do not require raw ignored runtime captures unless a live
  operator explicitly supplies them

### Requirement: Dynamic field behavior is fixture-tested

The protocol lab SHALL verify package frame/template primitives with offline
fixtures before they are used by live TestClient sessions.

#### Scenario: Dynamic replacements are inspected

- **WHEN** offline tests render a template frame twice with different dynamic
  values
- **THEN** expected dynamic field locations change
- **AND** preserved semantic fields remain visible rather than being silently
  normalized away

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

### Requirement: Research tools reuse package protocol APIs

The protocol lab SHALL keep exploratory protocol tools aligned with promoted
`qa_mcp.protocol` APIs after package promotion.

#### Scenario: Probe tool imports package session API

- **WHEN** a protocol research script needs promoted frame, template or
  read-only session behavior
- **THEN** it imports the package API instead of maintaining a divergent copy
- **AND** any remaining script-local logic is limited to CLI parsing,
  evidence file layout or research-specific orchestration

### Requirement: Existing protocol research CLIs remain compatible

The protocol lab SHALL preserve existing Windows-native protocol research CLI
entrypoints during package promotion.

#### Scenario: Research CLI is invoked after package promotion

- **WHEN** an operator runs an existing protocol research command such as
  `python_manager_probe.py`, `protocol_corpus_runner.py` or
  `compare_corpus_runs.py`
- **THEN** documented arguments and output schemas continue to work or a
  documented migration note explains the change
- **AND** compatibility is covered by offline tests or smoke commands

### Requirement: Wrapper changes do not rewrite historical evidence

The protocol lab SHALL avoid silently replacing committed protocol evidence
when research tools are refactored around package APIs.

#### Scenario: Wrapper refactor affects evidence generation

- **WHEN** a wrapper refactor changes generated compact evidence
- **THEN** new evidence is written under a new reviewed evidence id
- **AND** `docs/protocol-research/evidence-index.md` records the new output
- **AND** raw runtime output remains ignored

### Requirement: Read-only element hash gaps are audited before promotion

The protocol lab SHALL audit useful read-only element direct-probe rows against
the corpus evidence contract before promoting them or publishing a final
unresolved status.

#### Scenario: Element row evidence is inventoried

- **WHEN** `form-element-details` or `typed-input-field-readonly` is reviewed
  for possible promotion
- **THEN** the audit records the source evidence paths, capture ids, frame
  ranges, request and response sizes, normalized hashes, dynamic fields,
  operation token, response markers and replay or direct Python-manager status
  currently available for that row

#### Scenario: Element row gap is classified

- **WHEN** a useful element direct-probe row lacks complete accepted evidence
- **THEN** the audit records whether the gap is caused by missing request
  frames, an ambiguous operation join, unsupported fixture state, incomplete
  normalizer coverage or another explicit reviewed reason
- **AND** the row remains non-accepted until a later change supplies accepted
  evidence and publication updates

### Requirement: Element hash audits preserve raw evidence boundaries

The protocol lab SHALL keep raw captures, full probe output and local process
logs out of reviewed audit artifacts.

#### Scenario: Audit report references runtime evidence

- **WHEN** the audit needs to reference raw capture or probe output
- **THEN** it links or names the ignored runtime source location without
  copying raw TCP payloads, full runtime logs, credentials or local infobase
  data into committed evidence

### Requirement: Useful read-only element rows have reviewed request-hash evidence or an unavailable proof

The protocol lab SHALL capture, extract or explicitly prove unavailable the
reviewed request-frame hash evidence for useful read-only element probe rows
before their resolution is published.

#### Scenario: Reviewed element request hash is produced

- **WHEN** `form-element-details` or `typed-input-field-readonly` has captured
  or extractable manager-to-client request frames
- **THEN** the compact evidence records capture id, frame range, request and
  response sizes, normalized hash, dynamic fields, operation token, response
  markers, replay or direct Python-manager status and evidence path
- **AND** raw captures and full probe output remain in ignored runtime
  directories

#### Scenario: Reviewed element request hash is unavailable

- **WHEN** the current lab path cannot produce reviewed request-frame hash
  evidence for a useful element row
- **THEN** the compact evidence records the attempted source, command or
  extraction path, observed result, unresolved reason and next actionable
  blocker
- **AND** the row remains non-accepted for later classification and
  publication

### Requirement: Element request-hash capture remains read-only

The protocol lab SHALL keep element request-hash capture and probing within
read-only TestClient operations.

#### Scenario: Live element hash capture runs

- **WHEN** a live capture or direct Python-manager probe is run for element
  request-hash evidence
- **THEN** it uses read-only form/window/element query operations only
- **AND** it does not click controls, enter text, execute commands, change
  business data or terminate unrelated 1C processes

### Requirement: Element hash classification records precise unresolved reasons

The protocol lab SHALL classify useful read-only element hash gaps with
reviewable reason values that identify the next actionable blocker.

#### Scenario: Request frames are missing

- **WHEN** a useful element probe has response or direct-probe evidence but no
  reviewed manager-to-client request frame slice
- **THEN** classification evidence records the row as non-accepted with
  `missing_request_frames` or an equivalent stable reason

#### Scenario: Operation join is ambiguous

- **WHEN** probe evidence cannot be joined to a single reviewed operation
  shape, frame range or response marker set
- **THEN** classification evidence records the row as non-accepted with
  `ambiguous_operation_join` or an equivalent stable reason

#### Scenario: Normalizer coverage is incomplete

- **WHEN** request frames exist but dynamic fields cannot be normalized into a
  stable reviewed hash
- **THEN** classification evidence records the row as non-accepted with
  `incomplete_normalizer_coverage` or an equivalent stable reason

### Requirement: Element rows are accepted only with stable reviewed hashes

The protocol lab SHALL keep useful element direct-probe rows out of accepted
mapping output until stable reviewed request hashes and replay or direct-probe
proof support the same operation.

#### Scenario: Probe succeeds without complete wire evidence

- **WHEN** `form-element-details` or `typed-input-field-readonly` returns
  useful direct Python-manager data
- **BUT** repeated reviewed inputs do not provide a stable non-null normalized
  hash for the same operation
- **THEN** the row remains non-accepted and the classification report records
  the unresolved reason

#### Scenario: Stable wire evidence and probe proof match

- **WHEN** repeated reviewed inputs provide a stable non-null normalized hash
  and accepted replay or direct-probe evidence for the same element operation
- **THEN** classification evidence may mark the row accepted and retain the
  evidence fields required by the corpus evidence contract

### Requirement: Read-only element hash resolution is published as accepted or unresolved

The protocol lab SHALL publish the final resolution for useful read-only
element hash gaps as either accepted mapping evidence or a precise unresolved
report.

#### Scenario: Element row is accepted

- **WHEN** `form-element-details` or `typed-input-field-readonly` has stable
  reviewed request hashes and accepted replay or direct Python-manager proof
  for the same operation
- **THEN** the published evidence records capture ids, frame ranges, request
  and response sizes, normalized hashes, dynamic fields, operation tokens,
  response markers, replay or probe status and evidence paths
- **AND** package descriptors may expose the row as accepted

#### Scenario: Element row remains unresolved

- **WHEN** accepted evidence is unavailable or incomplete for an element row
- **THEN** the published evidence records the non-accepted status, precise
  unresolved reason, source evidence paths and next actionable blocker
- **AND** package descriptors continue to expose `incomplete_hash` or another
  explicit non-accepted status for that row

### Requirement: Read-only element publication does not broaden action coverage

The protocol lab SHALL keep read-only element hash publication separate from
safe UI action, input and write behavior.

#### Scenario: Publication completes

- **WHEN** accepted or unresolved read-only element hash evidence is published
- **THEN** no click, input, command execution, business-data mutation or
  safe-action protocol descriptor is introduced by the publication change

### Requirement: Safe UI action scope is explicitly gated

The protocol lab SHALL define the allowed safe UI action families and excluded
mutation semantics before accepting any action protocol case.

#### Scenario: Candidate action is selected

- **WHEN** a safe UI action candidate is added to the protocol case matrix
- **THEN** the candidate records its action family, UI target, pre-state,
  expected post-state and recovery or cleanup expectation
- **AND** the candidate is limited to focus or element activation, existing
  window activation, tab or page switching, or menu expansion that does not
  execute a command

#### Scenario: Candidate action would mutate business data

- **WHEN** a candidate requires text input, command execution, checkbox
  toggling, table editing, save/post/delete behavior or another persisted data
  mutation
- **THEN** the candidate is excluded from the safe UI action matrix
- **AND** the exclusion records that a separate mutation-specific card is
  required before capture

### Requirement: Safe UI actions preserve unresolved read-only evidence gates

The protocol lab SHALL keep controlled fixture and read-only element hash
outcomes visible when choosing safe UI action targets.

#### Scenario: Read-only prerequisite is unresolved or deferred

- **WHEN** a safe UI action target depends on a read-only fixture family or
  element request shape with non-accepted evidence
- **THEN** the action candidate records the unresolved status, owner route and
  residual risk
- **AND** the candidate is not accepted as protocol knowledge until later
  capture and replay or probe evidence satisfies the safe action contract

### Requirement: Safe action case events record state transitions

The protocol lab SHALL record safe UI action case events with enough
state-transition detail to review the intended action independently from raw
traffic.

#### Scenario: Safe action event row is emitted

- **WHEN** the runner or analyzer emits a safe UI action case event
- **THEN** the event records `case_id`, `api_call`, `ui_target`,
  `pre_state`, `action`, `post_state`, `recovery_expectation` and
  `action_result_markers`
- **AND** the event records whether the case is `supported`, `pending`,
  `unsupported`, `partial`, `timeout` or `rejected`

### Requirement: Action frame ranges are separated from background refresh

The protocol lab SHALL distinguish action-related frames from background
refresh frames in reviewed action evidence.

#### Scenario: Background traffic surrounds an action

- **WHEN** a captured safe UI action includes active-window, active-form,
  idle or refresh traffic outside the selected action boundary
- **THEN** the compact evidence records the action frame range separately from
  background or refresh frame ranges
- **AND** the row does not treat refresh-only frames as proof of the action

### Requirement: Safe action rows preserve corpus evidence fields

The protocol lab SHALL retain the core corpus evidence fields for safe UI
action rows.

#### Scenario: Safe action row is generated

- **WHEN** compact reviewed evidence is generated for a safe UI action case
- **THEN** the row includes `case_id`, `api_call`, `ui_target`,
  `frame_range`, `normalized_hash`, dynamic fields, `operation_token`,
  `response_markers`, `replay_status` and action result markers
- **AND** raw request and response payloads remain outside reviewed evidence

### Requirement: Safe UI action captures produce compact evidence

The protocol lab SHALL retain compact reviewed evidence for every attempted
safe UI action capture and keep raw runtime output outside reviewed git
changes.

#### Scenario: Safe action capture is reviewed

- **WHEN** a Windows-native capture runs a safe UI action case
- **THEN** reviewed evidence records `case_id`, `api_call`, `ui_target`,
  pre-state, action, post-state, recovery expectation, frame range,
  normalized hash, dynamic fields, operation token, response markers, replay
  status and action result markers
- **AND** raw TCP captures, platform logs and case-event runtime payloads
  remain under ignored `runtime/protocol-research/` paths

### Requirement: Unsupported safe UI action captures remain visible

The protocol lab SHALL record unavailable or unsupported safe UI action cases
instead of silently omitting them from the matrix.

#### Scenario: Safe action target is unavailable

- **WHEN** a selected safe UI action cannot be performed against the current
  lab form or cannot be joined to a reviewed frame range
- **THEN** the compact evidence records `unsupported`, `pending`, `partial`,
  `timeout` or `rejected` status with an unresolved reason
- **AND** the row is not accepted as protocol knowledge

### Requirement: Safe action capture performs no business mutation

The protocol lab SHALL prevent safe UI action captures from writing persisted
business data.

#### Scenario: Capture scenario attempts a mutating operation

- **WHEN** a capture scenario would execute a command with side effects, enter
  text, toggle persisted values, edit a table, save, post, delete or otherwise
  mutate business data
- **THEN** the scenario is rejected before capture
- **AND** the rejected operation is routed to a separate mutation-specific
  card with rollback expectations

### Requirement: Safe UI action mappings require classification

The protocol lab SHALL classify safe UI action evidence before using an action
row as working protocol knowledge.

#### Scenario: Safe action evidence is classified

- **WHEN** compact safe UI action evidence is compared or reviewed
- **THEN** every row is classified as `accepted`, `pending`, `unsupported`,
  `partial`, `timeout`, `rejected` or `blocked`
- **AND** the classification records capture ids, action frame ranges,
  background refresh ranges, normalized hashes, dynamic fields, operation
  tokens, response markers, action result markers and evidence paths when
  available

### Requirement: Accepted safe UI action mappings require replay or probe proof

The protocol lab SHALL require replay or direct Python-manager confirmation
before a safe UI action mapping is accepted.

#### Scenario: Safe action row is accepted

- **WHEN** a safe UI action row is promoted to accepted mapping evidence
- **THEN** the row has reviewed action frame evidence and accepted replay or
  direct Python-manager proof for the same non-mutating action
- **AND** the row retains pre-state, post-state, recovery expectation,
  normalized hash, dynamic fields, operation token, response markers and
  action result markers

#### Scenario: Replay or probe is unavailable

- **WHEN** current tooling cannot safely replay or directly probe a safe UI
  action row
- **THEN** the row remains `pending`, `unsupported`, `partial`, `timeout`,
  `rejected` or `blocked` with an owner route and residual risk
- **AND** the row is not published as an accepted mapping

### Requirement: Safe action publication preserves unresolved rows

The protocol lab SHALL publish unresolved safe UI action outcomes without
rewriting historical evidence.

#### Scenario: Safe action publication completes

- **WHEN** safe UI action classification or accepted-mapping evidence is
  published
- **THEN** the evidence index links compact capture, classification,
  replay/probe and accepted or unresolved mapping artifacts
- **AND** unsupported or unresolved rows remain visible with reason values
  instead of being omitted from reviewed coverage

### Requirement: Client fixture processor shell is target-bound and marker-visible

The protocol lab SHALL provide a dedicated V1 client fixture processor shell in
the `client` EDT target before adding broad read-only control coverage.

#### Scenario: Fixture shell is authored in the client target

- **WHEN** the processor shell is implemented
- **THEN** it is added under the `vanessa_client` EDT project
- **AND** `validate_project_infobase_binding(target_id="client", timeout_seconds=90)` is used before retrieve, update or hot-deploy work

#### Scenario: Fixture shell exposes top-level markers

- **WHEN** TestClient opens the fixture form
- **THEN** read-only form inspection can observe `PF_FORM_MAIN`
- **AND** read-only form inspection can observe `PF_FIXTURE_VERSION`
- **AND** the visible or inspectable version value is `protocol-fixture.v1`

#### Scenario: Fixture shell avoids business mutation

- **WHEN** the fixture form initializes
- **THEN** it does not create, edit, post or delete business objects
- **AND** it does not require catalogs, documents, registers or external services to expose its shell markers

### Requirement: Client fixture V1 exposes stable read-only control families

The protocol lab SHALL expose a broad, deterministic V1 control surface in the
client fixture processor for read-only TestClient protocol research.

#### Scenario: Fixture form exposes common control families

- **WHEN** the V1 fixture form is opened
- **THEN** read-only form inspection can identify markers for edit fields, checkboxes, choice or radio-style input, buttons, command bar, table, label, group and pages
- **AND** each target family has a unique `PF_*` marker

#### Scenario: Fixture values are deterministic

- **WHEN** the V1 fixture form initializes
- **THEN** string, number, date, checkbox, choice and table values are populated from local fixture state
- **AND** the values do not depend on current business documents, catalogs, registers or external services

#### Scenario: V1 controls are not accepted as actions

- **WHEN** V1 read-only evidence is reviewed
- **THEN** the existence of buttons, commands, checkboxes and pages does not by itself accept click, command, toggle, input or page-switch protocol mappings
- **AND** unsupported action semantics remain out of scope until later fixture versions

### Requirement: Client fixture V1 targets are mapped before corpus capture

The protocol lab SHALL publish a compact target map for V1 fixture elements
before using those elements as read-only corpus targets.

#### Scenario: Target map records fixture markers

- **WHEN** the V1 target map is published
- **THEN** each mapped row includes a `PF_*` marker, element family, target path, expected state and expected response markers
- **AND** each row identifies whether the target is supported, pending, partial or blocked

#### Scenario: Target map links to corpus intent

- **WHEN** a V1 fixture target is intended for read-only corpus capture
- **THEN** the target map links the target to planned case ids or manifest rows
- **AND** the target map records semantic sources as supporting context rather than protocol proof

#### Scenario: Target map does not promote protocol mappings

- **WHEN** target-map evidence exists without capture and replay/probe evidence
- **THEN** the related corpus rows remain non-accepted
- **AND** accepted mappings still require frame ranges, normalized hashes, dynamic fields and replay or direct Python-manager status

### Requirement: Manager fixture runner shell is target-bound

The protocol lab SHALL provide a manager-side fixture runner shell in the
`manager` EDT target before using a 1C TestManager instance as the controlled
read-only corpus generator.

#### Scenario: Manager runner shell is prepared

- **WHEN** the manager fixture runner shell is implemented
- **THEN** source and deploy operations use `target_id="manager"` with project
  `vanessa_manager` and infobase `vanessa_manager`
- **AND** retained evidence records a successful manager project-to-infobase
  binding check before runtime apply or hot deploy

#### Scenario: Manager runner shell bootstraps the client fixture

- **WHEN** the manager runner starts a V1 run
- **THEN** it accepts `run_id`, proxy TestClient port, client fixture
  navigation target and output directory as explicit run context
- **AND** it labels client fixture form-open traffic as bootstrap rather than
  a read-only corpus case
- **AND** it performs no TCP parsing or protocol normalization inside 1C

### Requirement: Manager fixture V1 commands are manifest-driven and read-only

The protocol lab SHALL define manager V1 command execution through a manifest
and command catalog that describe only read-only TestManager API operations
against the client fixture V1 surface.

#### Scenario: Read-only manifest is loaded

- **WHEN** the manager V1 harness starts a read-only run
- **THEN** the input manifest records `run_id`, `case_id`, `command_id`, target
  fixture path, proxy TestClient port, target `PF_*` marker and expected
  response marker for each command
- **AND** commands that require text input, clicks, page switching, row
  selection, business commands or object writes are rejected from the V1
  accepted command catalog

#### Scenario: Command event is emitted

- **WHEN** the manager V1 harness executes one manifest command
- **THEN** it writes side-channel events with before and after timestamps,
  command status, target marker, expected marker, result preview and exception
  details when present
- **AND** it writes compact run output such as `case_events.jsonl` and
  `manager_harness_result.json` under the runtime directory selected by the
  capture runner

### Requirement: Manager fixture V1 capture shares one run id

The protocol lab SHALL orchestrate manager fixture V1 read-only runs so proxy
traffic, manager side-channel events and runtime logs share one capture or
run id.

#### Scenario: Manager fixture capture is run

- **WHEN** the Windows-native capture runner executes the manager fixture V1
  scenario
- **THEN** it routes the TestClient connection through the TCP proxy and passes
  the proxy endpoint to the manager harness
- **AND** it stores proxy traffic, manager output and 1C logs under the same
  ignored runtime run directory

#### Scenario: Capture runner cleanup runs

- **WHEN** the manager fixture V1 capture exits successfully or fails
- **THEN** the runner records owned TestClient, proxy and manager PIDs and
  stops only those owned processes
- **AND** unrelated 1C sessions are left running
- **AND** raw TCP payloads and full process logs remain outside reviewed git
  changes

### Requirement: Manager fixture V1 evidence is reviewed before corpus use

The protocol lab SHALL publish compact reviewed evidence for manager fixture
V1 read-only runs before using those runs as protocol-corpus inputs.

#### Scenario: Manager V1 evidence summary is published

- **WHEN** a manager fixture V1 read-only run is reviewed
- **THEN** the summary records run id, command catalog version, bootstrap
  status, runtime output paths, command counts, failure details and evidence
  owner routes
- **AND** raw TCP streams, full event logs, platform logs and generated replay
  output remain under ignored runtime paths

#### Scenario: Frame join status is reported

- **WHEN** manager side-channel events are compared with proxy traffic
- **THEN** the reviewed report records per-case frame-join status, frame or
  chunk ranges when known, unresolved reason when not known and whether replay
  or direct Python-manager proof exists
- **AND** no command is published as an accepted protocol mapping until frame
  ranges, dynamic fields, normalized hashes and replay or direct-probe status
  support that claim

### Requirement: Manager fixture V1 harness executes manifest runs end to end

The protocol lab SHALL provide a manager-side V1 harness entrypoint that loads
a read-only manifest, executes each command against the proxied TestClient and
writes side-channel evidence under the selected runtime directory.

#### Scenario: Manifest command sequence is executed

- **WHEN** the manager V1 harness is invoked with a valid read-only manifest
- **THEN** it connects to the TestClient through the manifest proxy port
- **AND** it executes the manifest commands in order
- **AND** it writes before and after `case_events.jsonl` records for each
  command
- **AND** it writes `manager_harness_result.json` with command counts and final
  run status

#### Scenario: Command failure is retained as evidence

- **WHEN** one read-only command raises a TestManager or platform exception
- **THEN** the harness records the exception summary in the command after-event
- **AND** the final result records failed and completed counts
- **AND** already written events remain in the runtime directory

#### Scenario: Non-read-only command is rejected

- **WHEN** the manifest contains an action, input, command execution or write
  command kind
- **THEN** the manager V1 harness rejects the run before executing the command
- **AND** the result records a fail-closed status without accepting any
  protocol mapping

### Requirement: Manager fixture V1 command catalog is synchronized

The protocol lab SHALL keep the manager fixture V1 read-only command catalog
consistent across BSL source, capture-runner manifests and reviewed evidence.

#### Scenario: Manifest is generated from reviewed command ids

- **WHEN** the capture runner writes `manager_harness_manifest.json`
- **THEN** every command id in the manifest matches the reviewed V1 command
  catalog
- **AND** the manifest records the selected smoke subset separately from the
  full catalog when only part of the catalog is executed

#### Scenario: BSL catalog matches tooling catalog

- **WHEN** the manager harness source defines V1 read-only commands
- **THEN** its command ids, command kinds, target markers and expected markers
  match the reviewed catalog used by protocol tooling
- **AND** catalog drift is reported by offline verification before live capture

### Requirement: Manager fixture V1 live capture invokes the custom harness

The protocol lab SHALL execute non-dry-run `manager-fixture-v1-readonly`
captures by invoking the dedicated manager fixture harness through the TCP
proxy and preserving all runtime outputs under one run id.

#### Scenario: Live manager fixture capture runs

- **WHEN** the capture runner starts a non-dry-run
  `manager-fixture-v1-readonly` scenario
- **THEN** it starts or prepares the TestClient, proxy and manager processes
  using Windows-native entrypoints
- **AND** it passes the shared run id, proxy TestClient port, output directory
  and manifest path to the manager harness
- **AND** the runtime directory contains proxy `traffic.jsonl`, manager
  harness manifest, case events and result output

#### Scenario: Required runtime asset is missing

- **WHEN** the configured Vanessa EPF or required manager runtime asset is not
  available
- **THEN** the capture runner fails closed or records a compact provider gap
- **AND** the run is not reported as live protocol evidence

#### Scenario: Capture cleanup runs

- **WHEN** the live capture exits successfully or fails
- **THEN** the runner stops only the TestClient, proxy and manager PIDs it
  created
- **AND** unrelated 1C sessions remain untouched

### Requirement: Manager fixture V1 case events are joined to proxy traffic

The protocol lab SHALL convert manager fixture V1 side-channel events and TCP
proxy traffic into reviewed per-case join evidence before generating corpus
rows from a live manager harness run.

#### Scenario: Case events are joined

- **WHEN** a manager fixture V1 runtime directory contains `case_events.jsonl`
  and `traffic.jsonl`
- **THEN** the analyzer maps each read-only command to manager and client
  chunk or frame ranges when boundaries are reviewable
- **AND** the join report records the selected ranges, command id, target
  marker and expected marker

#### Scenario: Join is unresolved

- **WHEN** a command lacks events, proxy chunks or unambiguous boundaries
- **THEN** the join report records a precise unresolved reason
- **AND** the command remains non-accepted

#### Scenario: Corpus row is generated

- **WHEN** a command has a reviewed range
- **THEN** the corpus row records frame range, request/response sizes,
  dynamic fields, normalized hash, operation token candidate, response markers
  and replay/probe status
- **AND** raw payloads remain under ignored runtime paths

### Requirement: Manager fixture V1 pending rows are classified before promotion

The protocol lab SHALL classify every pending manager fixture V1 read-only row
from a reviewed cleanup run before accepting the row, changing its manifest
expectation or using it to unblock later action research.

#### Scenario: Pending row classification is published

- **WHEN** a manager fixture V1 cleanup report contains joined non-accepted rows
- **THEN** the protocol lab records a classification for each pending row
- **AND** the classification links the cleanup run id, case id, frame range,
  normalized hash, expected marker, observed marker evidence and replay/probe
  state

#### Scenario: Classification does not promote a row

- **WHEN** a pending row has joined frame evidence but no matching replay or
  direct-probe proof
- **THEN** the row remains non-accepted
- **AND** the classification records the next evidence needed for promotion

#### Scenario: Manifest correction is evidence-gated

- **WHEN** a pending row appears to use a too-strict or wrong expected marker
- **THEN** the protocol lab records a candidate manifest correction
- **AND** the correction is not treated as accepted protocol knowledge until
  replay or direct-probe evidence validates the corrected semantics

### Requirement: Manager fixture V1 pending probes require a clean runtime endpoint

The protocol lab SHALL prepare or explicitly gap a clean Windows-native
TestClient endpoint before attempting manager fixture V1 pending-row replay or
direct probes.

#### Scenario: Endpoint readiness is retained

- **WHEN** a pending-row probe pass starts for manager fixture V1
- **THEN** the protocol lab records the run id, TestClient port, proxy port,
  fixture route and endpoint readiness state
- **AND** the evidence identifies which PIDs are runner-owned for cleanup

#### Scenario: Runtime startup is unavailable

- **WHEN** a clean TestClient endpoint cannot be started or attached
- **THEN** the protocol lab records a compact provider/runtime gap
- **AND** no pending row is accepted from the unavailable runtime pass

#### Scenario: Cleanup ownership is preserved

- **WHEN** endpoint preparation exits successfully or fails
- **THEN** cleanup stops only TestClient, proxy and manager PIDs created or
  explicitly owned by the pending-row runtime route
- **AND** unrelated 1C sessions remain untouched

### Requirement: Pending manager fixture V1 rows require current-run probe proof

The protocol lab SHALL promote a pending manager fixture V1 read-only row only
when retained replay or direct-probe evidence matches the current cleanup run
identity and expected semantic response.

#### Scenario: Probe proof matches the cleanup row

- **WHEN** replay or direct-probe evidence is used to accept a pending row
- **THEN** the evidence records the cleanup run id, case id, manager frame
  range, normalized hash, response marker and dynamic-field adaptation
- **AND** the reporter can validate those fields against the joined corpus row

#### Scenario: Probe proof is mismatched

- **WHEN** replay transport succeeds but the expected marker, endpoint, frame
  range or normalized hash does not match the cleanup row
- **THEN** the row remains non-accepted
- **AND** the mismatch is retained as reviewed evidence

#### Scenario: Older probe evidence is supporting only

- **WHEN** older probe evidence exists for the same conceptual operation
- **THEN** it can be linked as supporting context
- **AND** it SHALL NOT promote the current cleanup row unless reconciled with
  the current run range and normalized hash

### Requirement: Missing-proof manager fixture V1 rows are probed with current-run identity

The protocol lab SHALL attempt focused replay or direct-probe proof for manager
fixture V1 pending rows that lack proof before promoting, correcting or using
the rows for V2 readiness.

#### Scenario: Missing-proof row is accepted

- **WHEN** a focused replay or direct probe is used to accept a missing-proof
  pending row
- **THEN** the retained summary records the current cleanup run id, case id,
  manager frame range, normalized hash, response marker and dynamic-field
  adaptation
- **AND** the reporter validates those fields against the cleanup corpus row

#### Scenario: Missing-proof row remains pending

- **WHEN** replay/direct-probe proof is absent, mismatched, ambiguous or from
  the wrong endpoint
- **THEN** the row remains non-accepted
- **AND** the retained summary records the exact blocker and next route

#### Scenario: Older evidence is supporting only

- **WHEN** older probe evidence exists for the same conceptual operation
- **THEN** it can be linked as supporting context
- **AND** it SHALL NOT promote the current cleanup row unless reconciled with
  the current run range and normalized hash

### Requirement: Broad manager fixture V1 pending windows are isolated before acceptance

The protocol lab SHALL isolate broad manager fixture V1 pending frame windows
or keep them non-accepted with an explicit isolation gap before publishing an
accepted protocol mapping for those rows.

#### Scenario: Broad window is isolated

- **WHEN** a pending row currently spans a broad manager frame range
- **THEN** the protocol lab produces a narrower reviewed range or focused
  rerun for that case id
- **AND** the isolated row records request size, response size, dynamic fields,
  normalized hash and response markers

#### Scenario: Isolation fails

- **WHEN** a broad pending row cannot be isolated from background or endpoint
  traffic
- **THEN** the row remains non-accepted
- **AND** the reviewed evidence records the blocker and owner route

#### Scenario: Target marker alone is insufficient

- **WHEN** a target marker appears inside a broad frame window
- **THEN** the marker alone SHALL NOT promote the row
- **AND** accepted promotion still requires matching replay or direct-probe
  proof for the reviewed range

### Requirement: Manager fixture V1 marker contract corrections are evidence-gated

The protocol lab SHALL change manager fixture V1 expected markers only when
current-run replay or direct-probe evidence proves the corrected semantic
contract.

#### Scenario: Marker correction is accepted

- **WHEN** a pending row's expected marker is corrected
- **THEN** the retained evidence records the previous marker, corrected marker,
  case id, manager frame range and normalized hash
- **AND** the regenerated report validates the corrected marker against the
  current cleanup row before accepting it

#### Scenario: Marker correction is candidate-only

- **WHEN** a candidate marker appears plausible but lacks current-run proof
- **THEN** the marker is retained as candidate evidence
- **AND** the row remains non-accepted

#### Scenario: Catalogs remain aligned

- **WHEN** marker expectations change in a manifest, JSON catalog or BSL source
- **THEN** the protocol lab verifies that the reviewed command catalogs remain
  aligned
- **AND** records any catalog drift as a blocker before publication

### Requirement: Manager fixture V1 pending-promotion work is republished as a readiness state

The protocol lab SHALL republish manager fixture V1 read-only cleanup evidence
after pending-row promotion attempts and state the resulting V2 readiness.

#### Scenario: Accepted and pending counts are regenerated

- **WHEN** retained pending-row probe, isolation and marker-contract evidence
  exists
- **THEN** the protocol lab regenerates the reviewed live-join report with all
  accepted and non-accepted summaries folded in
- **AND** the report records coherent accepted and pending counts for all 17
  command windows

#### Scenario: Accepted rows link proof

- **WHEN** a row is promoted to accepted
- **THEN** the final report links the replay or direct-probe evidence used for
  promotion
- **AND** that evidence matches case id, manager frame range and
  normalized hash

#### Scenario: V2 readiness is published

- **WHEN** the final manager fixture V1 pending-promotion report is published
- **THEN** protocol research docs state whether V2 safe-action acceptance is
  unblocked, blocked, or allowed only by explicit residual-risk decision
- **AND** any remaining pending rows retain precise blocker evidence

### Requirement: Manager fixture V1 cleanup acceptance is republished after probes

The protocol lab SHALL regenerate reviewed manager fixture V1 cleanup evidence
after pending-row classification and replay/direct-probe attempts, preserving
the accepted gate and documenting any residual pending rows.

#### Scenario: Accepted summaries are folded into the cleanup report

- **WHEN** retained replay/probe summaries match cleanup corpus rows
- **THEN** the regenerated live-join report marks those rows accepted
- **AND** each accepted row links the replay/probe evidence used for promotion

#### Scenario: Residual pending rows remain visible

- **WHEN** a row still lacks matching replay/probe proof or has a semantic
  mismatch
- **THEN** the regenerated report keeps the row non-accepted
- **AND** records the exact blocker and next route

#### Scenario: V2 readiness is stated

- **WHEN** the final manager fixture V1 cleanup report is published
- **THEN** protocol research docs state whether V2 safe-action planning is
  blocked, unblocked or allowed only with explicit residual risk

### Requirement: Manager fixture V1 live smoke gates full catalog expansion

The protocol lab SHALL publish a bounded non-dry-run manager fixture V1 smoke
before using the full V1 command catalog for broad read-only protocol corpus
research.

#### Scenario: Live smoke succeeds

- **WHEN** the bounded manager fixture V1 smoke runs against the client fixture
- **THEN** the reviewed evidence records the run id, executed command ids,
  runtime output paths, join report and corpus rows
- **AND** at least one row has a non-null reviewed range, request size,
  response size and normalized hash
- **AND** replay or direct Python-manager proof is attempted when supported

#### Scenario: Live smoke is provider-gapped

- **WHEN** the smoke cannot start because required runtime assets or provider
  capabilities are unavailable
- **THEN** the reviewed evidence records the provider gap, owner route,
  missing evidence type and residual risk
- **AND** no live protocol mapping is accepted from that run

#### Scenario: Full catalog expansion is considered

- **WHEN** the bounded smoke has no joined normalized row
- **THEN** the full V1 command catalog remains blocked
- **AND** the next blocker is recorded in reviewed evidence

### Requirement: Automated testing API inventory is reviewed before broad corpus expansion

The protocol lab SHALL keep a compact reviewed inventory of the 1C automated
testing API surface before expanding the manager fixture corpus beyond the
bounded V1 smoke.

#### Scenario: Inventory is generated

- **WHEN** the API inventory is generated from platform help or `help-mcp`
- **THEN** it records the source platform version, object names, aliases,
  members, parameters, return types when available and default safety class
- **AND** it writes a machine-readable JSON artifact under
  `docs/protocol-research/api-inventory/`
- **AND** it writes a compact reviewed summary with counts and known gaps

#### Scenario: Help source is incomplete

- **WHEN** a required automated-testing object or member cannot be resolved
- **THEN** the inventory records an explicit gap with owner route and residual
  risk
- **AND** the missing topic is not treated as unsupported protocol behavior

#### Scenario: Inventory is used for corpus planning

- **WHEN** a later corpus manifest is built from the inventory
- **THEN** inventory labels are treated as semantic planning support
- **AND** accepted protocol mappings still require wire evidence and
  replay/probe proof

### Requirement: V2 readiness documentation reflects V1 read-only closure

The protocol lab SHALL keep current project status documentation aligned with
the final manager fixture V1 read-only readiness state before V2 safe-action
work starts.

#### Scenario: V2 planning reads current status

- **WHEN** a V2 safe-action card uses project readiness documentation as input
- **THEN** the documentation states whether manager fixture V1 read-only
  coverage blocks, partially blocks or unblocks V2 planning
- **AND** the current accepted evidence paths are cited instead of relying only
  on older baseline pending counts

#### Scenario: Side-channel rows are cited

- **WHEN** readiness documentation mentions diagnostic rows accepted through
  typed manager side-channel contracts
- **THEN** those rows are labeled as side-channel contract evidence
- **AND** they are not described as direct TestClient wire marker claims

### Requirement: V1 readiness does not accept V2 action mappings by inference

The protocol lab SHALL treat V1 read-only closure as a prerequisite for V2
planning, not as proof of any safe-action protocol mapping.

#### Scenario: V2 action evidence is absent

- **WHEN** docs state that V1 read-only no longer blocks V2
- **THEN** the docs also state that V2 action rows still require their own
  pre-state, action, post-state, recovery, frame-range and replay or direct
  probe evidence before acceptance
- **AND** deferred or supporting V1 evidence is not promoted into V2 action
  protocol knowledge

### Requirement: V2 safe-action manifests are fail-closed

The protocol lab SHALL define every V2 safe-action candidate through a
complete manifest row before the action can be executed, captured or accepted
as protocol evidence.

#### Scenario: Manifest row is reviewed

- **WHEN** a V2 safe-action manifest row is added
- **THEN** the row records `action_id`, `target_id`, `target_marker`,
  `pre_state`, `action`, `post_state`, `recovery_expectation`,
  `mutates_business_data`, `allowed_action_family` and
  `expected_action_result_markers`
- **AND** `mutates_business_data` is `false`
- **AND** the row has enough expected markers to distinguish the action result
  from background refresh or unrelated UI traffic

#### Scenario: Manifest row is incomplete

- **WHEN** a V2 safe-action row lacks a target marker, pre-state, post-state,
  recovery expectation, safety flag or expected action result markers
- **THEN** the row is rejected before capture or manager-runner execution
- **AND** no protocol mapping is accepted from that row

### Requirement: Manager V2 safe-action catalog is fail-closed

The protocol lab SHALL define manager fixture V2 safe-action rows through a
reviewed catalog or manifest before any manager-runner execution.

#### Scenario: Safe-action catalog row is executable

- **WHEN** a manager V2 safe-action row includes action id, target id, target
  marker, pre-state, action, post-state, recovery expectation,
  `mutates_business_data=false`, allowlisted action family and expected result
  markers
- **THEN** the manager runner may treat the row as executable candidate input
- **AND** the row remains non-accepted protocol evidence until live proof and
  replay/probe or typed contract evidence are reviewed

#### Scenario: Unsafe catalog row is rejected

- **WHEN** a manager V2 safe-action row is incomplete, mutating, unsupported or
  outside the V2 allowlist
- **THEN** the manager runner rejects the row before execution
- **AND** the rejection records reason, owner and residual risk

### Requirement: Manager V2 runner executes only allowlisted safe actions

The protocol lab SHALL execute manager fixture V2 safe actions only when the
row passes the reviewed catalog and belongs to an allowlisted non-mutating
action family.

#### Scenario: Runner executes an allowlisted action

- **WHEN** the manager V2 runner receives a validated row for an allowlisted
  target and action family
- **THEN** the runner reads pre-state, executes the action and reads post-state
- **AND** the action is recorded as candidate evidence, not accepted protocol
  knowledge

#### Scenario: Runner rejects unsafe action

- **WHEN** the requested action is missing, disabled, mutating, outside the V2
  allowlist or cannot prove post-state
- **THEN** the runner fails closed before or during execution with a typed
  rejected or blocked result
- **AND** no business data write or external side effect is attempted

### Requirement: Manager V2 safe-action runs record phase boundaries

The protocol lab SHALL record manager fixture V2 safe-action phase events that
allow action, background and recovery traffic to be reviewed separately.

#### Scenario: Safe-action event sequence is complete

- **WHEN** a manager V2 safe-action row executes
- **THEN** `case_events.jsonl` records pre-read, action-start, action-end,
  post-read and recovery or recovery-read events with action id, target id,
  action family and result markers
- **AND** candidate frame-range correlation inputs are retained for the V2
  reporter

#### Scenario: Boundary is ambiguous

- **WHEN** a V2 action boundary cannot be joined to frames or chunk counters
  reliably
- **THEN** the row remains candidate, partial, timeout, rejected or blocked
- **AND** the ambiguity is visible in reviewed evidence

### Requirement: Manager V2 safe-action rows prove recovery

The protocol lab SHALL prove recovery or a documented known final state for
every executable manager fixture V2 safe-action row.

#### Scenario: Safe action recovers to baseline

- **WHEN** a manager V2 safe-action row completes
- **THEN** the runner executes the documented recovery path or records why no
  cleanup is required
- **AND** the post-recovery read shows the expected baseline or known-state
  markers

#### Scenario: Recovery proof is missing

- **WHEN** a V2 safe-action row lacks recovery markers, recovery frame range or
  known-state rationale
- **THEN** the row remains candidate, blocked, rejected, partial or timeout
- **AND** the row is not promoted as accepted safe-action evidence

#### Scenario: Action reruns after recovery

- **WHEN** the first focused candidate subset is recovered
- **THEN** the same action row can be run again with the same observable
  pre-state and result markers

### Requirement: Manager V2 safe-action evidence is published compactly

The protocol lab SHALL publish manager fixture V2 safe-action candidate
evidence as compact reviewed rows without committing raw runtime captures.

#### Scenario: Candidate evidence is retained

- **WHEN** a manager V2 safe-action run publishes reviewed evidence
- **THEN** the row records action id, target marker, action frame range,
  background ranges, recovery result, normalized hash fields and action result
  markers where available
- **AND** raw captures, platform logs and generated replay payloads remain
  under ignored runtime paths

#### Scenario: Accepted status requires proof

- **WHEN** a manager V2 safe-action row has joined action frames but lacks
  accepted replay/probe or typed contract proof
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** accepted mapping output excludes the row

#### Scenario: Focused proof can consume evidence

- **WHEN** candidate evidence is published for the supported runner subset
- **THEN** the first focused V2 safe-action proof card can cite the evidence
  path and decide whether rows are accepted or remain candidate

### Requirement: V2 action families are explicitly allowlisted

The protocol lab SHALL limit the first V2 safe-action layer to non-mutating
fixture-local UI actions.

#### Scenario: Candidate action is allowlisted

- **WHEN** a V2 candidate action belongs to focus or activate existing element,
  activate existing window/form, switch fixture page, select local table row,
  or expand/collapse menu or group without command execution
- **THEN** the action may be represented in the V2 manifest as a candidate
- **AND** it still remains unaccepted until later capture and replay or direct
  probe evidence proves the action request shape

#### Scenario: Candidate action is outside V2

- **WHEN** a candidate requires text input, checkbox or value toggle, business
  command click, object write, save, post, delete, fill, import, export or an
  external side effect
- **THEN** the candidate is excluded from V2 and routed to later mutation or
  recovery work
- **AND** the V2 runner fails closed instead of attempting the action

### Requirement: Agent instructions enforce the V2 safety boundary

The protocol lab SHALL keep local agent-facing instructions aligned with the
documented V2 safe-action manifest contract.

#### Scenario: Agent plans a V2 safe action

- **WHEN** an agent plans a V2 UI action capture, replay or manager-runner
  step
- **THEN** the agent verifies that the action is represented by a reviewed V2
  safe-action manifest row
- **AND** the row has `mutates_business_data=false`, an allowed action family,
  target marker, pre-state, post-state, recovery expectation and expected
  action result markers

#### Scenario: User requests a broad click or action

- **WHEN** a user requests a click, input, command execution, write or other
  broad UI action during V2 work
- **THEN** the agent classifies the request against the V2 manifest allowlist
- **AND** fails closed or routes the request to later mutation/recovery work
  when the request is not explicitly fixture-local and non-mutating

### Requirement: Mutating UI behavior is routed outside V2

The protocol lab SHALL keep text input, value toggles, business command clicks
and persisted data mutation out of V2 agent workflows.

#### Scenario: Action would mutate or require rollback

- **WHEN** an action could write object data, change persisted settings, save,
  post, delete, fill, import, export or require cleanup evidence
- **THEN** local agent instructions route the work to a later V3/V4 card
- **AND** V2 protocol research does not execute or accept the action

### Requirement: V2 safe-action tooling exposes a manager fixture scenario

The protocol lab SHALL provide a `manager-fixture-v2-safe-action` capture
scenario for safe non-mutating manager fixture actions.

#### Scenario: Safe-action scenario requires reviewed rows

- **WHEN** the V2 safe-action capture scenario starts
- **THEN** it requires a reviewed manifest row for every action it will
  capture or execute
- **AND** rows outside the V2 allowlist fail closed before capture begins

#### Scenario: Safe-action scenario records action phases

- **WHEN** the scenario captures a safe UI action
- **THEN** it records pre-read, action, post-read and recovery phase events
- **AND** bootstrap and background refresh traffic remain visible outside the
  action phase

### Requirement: V2 safe-action runtime output stays outside reviewed git

The protocol lab SHALL keep raw safe-action captures, process logs and
generated replay payloads under ignored runtime paths.

#### Scenario: Runtime output is separated from reviewed evidence

- **WHEN** the V2 safe-action scenario writes capture output
- **THEN** raw traffic and generated runtime files stay under
  `runtime/protocol-research/`
- **AND** reviewed git changes contain only compact manifests, summaries or
  evidence links

### Requirement: V2 safe-action tooling validates manifest rows before capture

The protocol lab SHALL validate V2 safe-action manifest rows before capture,
reporting or manager-runner execution.

#### Scenario: Complete row can proceed to capture

- **WHEN** a safe-action row includes the required target, state, recovery,
  allowlist and expected result marker fields
- **THEN** tooling may pass the row to the safe-action scenario
- **AND** the row remains non-accepted until evidence proves the action

#### Scenario: Incomplete row fails closed

- **WHEN** a safe-action row is missing a required manifest field
- **THEN** tooling rejects it before capture or execution
- **AND** the rejected row records a reason, provider owner and residual risk
  when it is retained for coverage review

### Requirement: V2 safe-action manifest excludes mutation families

The protocol lab SHALL reject text input, checkbox/value toggles, business
commands, object writes and external side effects from V2 safe-action rows.

#### Scenario: Mutation family is rejected

- **WHEN** a manifest row uses an action family outside the V2 allowlist
- **THEN** tooling fails closed before capture
- **AND** the row is routed to later mutation or recovery work instead of V2

### Requirement: V2 safe-action reporter publishes separated action evidence

The protocol lab SHALL publish V2 safe-action evidence with action,
background and recovery ranges separated.

#### Scenario: Reporter emits action-specific frame ranges

- **WHEN** a V2 safe-action capture is reported
- **THEN** each action row records `action_frame_range`,
  `background_frame_ranges` and `recovery_frame_range` when those ranges are
  present
- **AND** the action range is not treated as accepted proof by itself

#### Scenario: Reporter emits action result state

- **WHEN** a safe-action row has pre-state, post-state and recovery data
- **THEN** the report records `pre_state`, `post_state`, `recovery_result` and
  `action_result_markers`
- **AND** missing values keep the row non-accepted with an explicit reason

### Requirement: V2 safe-action reporter preserves V1 read-only reporting

The protocol lab SHALL keep V1 read-only report behavior stable while adding
V2 safe-action report output.

#### Scenario: V1 report path remains stable

- **WHEN** existing V1 read-only evidence is reported
- **THEN** V1 output remains compatible with the current evidence contract
- **AND** V2 action fields are added only to safe-action rows

### Requirement: V2 safe-action rows require replay/probe or typed contract proof for acceptance

The protocol lab SHALL promote a V2 safe-action row to accepted only when the
same non-mutating action has reviewed action evidence and accepted replay,
direct Python-manager probe or typed contract proof.

#### Scenario: Candidate action is not promoted by frame join alone

- **WHEN** a safe-action row has a joined `action_frame_range` but lacks
  accepted replay, probe or typed contract evidence
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** accepted-mapping output excludes the row

#### Scenario: Accepted action retains compact proof links

- **WHEN** a safe-action row is promoted to accepted
- **THEN** it retains normalized hash, dynamic fields, operation token,
  action result markers and compact proof evidence links
- **AND** raw replay or probe payloads remain outside reviewed git

### Requirement: V2 comparison output keeps non-accepted action rows visible

The protocol lab SHALL keep unresolved safe-action rows visible in comparison
output with explicit status and reason values.

#### Scenario: Non-accepted action remains visible

- **WHEN** comparison sees a `candidate`, `blocked`, `partial`, `timeout`,
  `rejected` or `unsupported` safe-action row
- **THEN** the row remains in comparison output
- **AND** the output records why the row is not accepted

### Requirement: Focused V2 safe-action subset is reviewed before live capture
The protocol lab SHALL select a reviewed focused subset before the first live
manager fixture V2 safe-action proof executes any action.

#### Scenario: Complete row is selected
- **WHEN** a manager fixture V2 safe-action row has an allowlisted action
  family, target marker, pre-state, post-state, recovery expectation,
  `mutates_business_data=false` and expected action result markers
- **THEN** the row may be included in the first focused proof subset
- **AND** the selection output records the row id, target id, target marker,
  action family and recovery expectation

#### Scenario: Unsafe row is excluded
- **WHEN** a candidate row is incomplete, mutating, button-like, a text input or
  value toggle, a business command or outside the V2 allowlist
- **THEN** the row is excluded from the focused proof subset
- **AND** the exclusion records reason, owner and residual risk when retained
  for review

#### Scenario: Subset stays narrow
- **WHEN** the first focused proof subset is prepared
- **THEN** it contains no more than two executable rows
- **AND** the preferred order is `switch_page` before `focus_element` when both
  rows are complete and safe

### Requirement: Focused V2 safe-action run records live phase evidence
The protocol lab SHALL capture the first focused manager fixture V2 safe-action
run with phase-aware evidence for reviewed subset rows only.

#### Scenario: Reviewed row is captured
- **WHEN** a row from the focused subset is executed by the
  `manager-fixture-v2-safe-action` scenario
- **THEN** the run records pre-read, action-start, action-end, post-read and
  recovery or recovery-read events with action id, target id, action family and
  result markers
- **AND** when phase timestamps and proxy traffic are both retained, compact
  evidence records separate action, background and recovery frame ranges
- **AND** raw captures, platform logs and generated replay payloads remain
  under ignored runtime paths

#### Scenario: Row cannot safely execute
- **WHEN** the selected row is unavailable, disabled, incomplete, mutating,
  outside the V2 allowlist or cannot prove post-state or recovery
- **THEN** the run fails closed for that row with typed status and reason
- **AND** no broader UI action or business-data mutation is attempted

#### Scenario: Recovery evidence is retained
- **WHEN** a focused safe-action row completes its action phase
- **THEN** the run records recovery evidence or documented known-state evidence
- **AND** the row remains unavailable for acceptance review when recovery
  evidence is missing

### Requirement: Focused V2 action frames are isolated before proof review
The protocol lab SHALL isolate action, background and recovery frame ranges for
the first focused V2 safe-action run before replay/probe or accepted-status
review.

#### Scenario: Action range is isolated
- **WHEN** the focused V2 reporter processes a live safe-action run
- **THEN** each reviewed row records an action frame range separately from
  bootstrap, background refresh and recovery ranges
- **AND** the row records request/response sizes, dynamic fields, normalized
  hash candidates and action result markers where available

#### Scenario: Join is ambiguous
- **WHEN** the action frame range cannot be isolated from background or
  recovery traffic
- **THEN** the row remains candidate, partial, timeout, rejected or blocked with
  an explicit reason
- **AND** accepted mapping output excludes the row

#### Scenario: Recovery range is separated
- **WHEN** the focused run includes recovery or recovery-read traffic
- **THEN** the recovery frame range is recorded separately from the action frame
  range
- **AND** recovery frames are not used as the action protocol request shape

### Requirement: Focused V2 safe-action proof attempts replay, probe or typed contract validation
The protocol lab SHALL attempt replay, direct Python-manager probe or typed
contract validation before the first focused V2 safe-action row is promoted to
accepted status.

#### Scenario: Proof succeeds
- **WHEN** a focused safe-action row has isolated action frames, recovery
  evidence and accepted replay, direct probe or typed contract proof for the
  same non-mutating action
- **THEN** the row may be marked accepted
- **AND** compact evidence records normalized hash, dynamic fields, operation
  token, request/response sizes and action result markers where available

#### Scenario: Proof is missing or fails
- **WHEN** a focused safe-action row lacks accepted replay, direct probe or
  typed contract proof
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** the row records the missing proof, failure reason and residual risk

#### Scenario: Raw proof payloads stay ignored
- **WHEN** replay or probe tooling writes request series, generated payloads,
  platform logs or raw runtime files
- **THEN** those files remain under ignored runtime or artifact paths
- **AND** reviewed git contains only compact proof summaries and evidence links

### Requirement: First focused V2 safe-action proof is published with explicit status
The protocol lab SHALL publish the first focused V2 safe-action proof with
compact evidence links and explicit accepted or non-accepted status.

#### Scenario: Accepted proof is published
- **WHEN** at least one focused safe-action row has reviewed action frames,
  recovery evidence and accepted replay, direct probe or typed contract proof
- **THEN** protocol docs and evidence indexes link the compact proof report and
  accepted mapping output
- **AND** the report records action id, target marker, normalized hash, dynamic
  fields, operation token, action result markers and proof evidence links where
  available

#### Scenario: Candidate proof is published
- **WHEN** the focused row has reviewed compact evidence but lacks accepted
  replay, direct probe or typed contract proof
- **THEN** protocol docs and evidence indexes publish the row as candidate or
  another explicit non-accepted status
- **AND** accepted mapping output excludes the row and records why it is not
  accepted

#### Scenario: V2 safety boundary remains visible
- **WHEN** the first focused proof is published
- **THEN** docs state that text input, checkbox/value toggles, business command
  clicks, object writes, save/post/delete/fill/import/export and external side
  effects remain outside V2
- **AND** downstream demo pilot or mutation cards are linked only as later work

### Requirement: V3 mutation state markers are local and observable
The protocol lab SHALL expose a resettable fixture-local mutation state model
for V3 scenarios.

#### Scenario: Fixture opens with local mutation markers
- **WHEN** TestClient opens the client fixture V3 surface
- **THEN** read-only inspection can observe the mutation baseline markers
- **AND** the markers describe only local UI state, not business objects or
  external services

### Requirement: V3 mutation targets declare deterministic expected values
The protocol lab SHALL declare stable initial values and expected mutated
values for each V3 mutation target family.

#### Scenario: Editable targets expose initial and expected values
- **WHEN** TestClient opens the client fixture V3 surface
- **THEN** read-only inspection can observe initial and expected value markers
  for string, number and date targets
- **AND** those markers are stable across reset and rerun cycles

#### Scenario: Checkbox targets expose initial and expected values
- **WHEN** TestClient opens the client fixture V3 surface
- **THEN** read-only inspection can observe initial and expected state markers
  for checkbox targets
- **AND** those markers are stable across reset and rerun cycles

#### Scenario: Mutation target markers are target-specific
- **WHEN** the fixture publishes V3 mutation markers
- **THEN** each editable and checkbox target has a target-specific value marker
  and expected-result marker
- **AND** the marker set can distinguish string, number, date and checkbox
  cases during evidence review

### Requirement: V3 mutation state updates are observable
The protocol lab SHALL publish target-specific post-state and recovery markers
for every V3 mutation case.

#### Scenario: Mutation updates local state deterministically
- **WHEN** a fixture-local mutation scenario changes an editable value, a
  checkbox, an inert action marker or a local counter
- **THEN** the relevant `PF_*` markers change in a deterministic way
- **AND** the update does not write business data

#### Scenario: Mutation exposes post-state and recovery markers
- **WHEN** a V3 mutation scenario completes
- **THEN** the fixture exposes a target-specific post-state marker
- **AND** the reset path exposes a recovery marker proving the baseline was
  restored

### Requirement: V3 mutation state can be reset to the baseline
The protocol lab SHALL restore the V1 baseline after a V3 mutation scenario is
completed or reset.

#### Scenario: Reset returns fixture to baseline
- **WHEN** `PF_RESET_STATE` or an equivalent reset hook is invoked after a
  mutation
- **THEN** the fixture returns to the baseline state that existed before the
  scenario
- **AND** the local value, checkbox, focus and counter markers no longer retain
  the prior mutation state
- **AND** no business data is created, edited, posted or deleted

### Requirement: V3 mutation handlers update only local fixture state
The protocol lab SHALL route V3 mutation inputs through local fixture handlers
that change only transient state.

#### Scenario: Editable value changes stay local
- **WHEN** TestClient enters a text, number or date value into a V3 mutation
  target
- **THEN** the corresponding local marker changes deterministically
- **AND** `PF_LAST_ACTION`, the action counter and the target-specific
  post-state marker reflect the mutation
- **AND** no business object, register or external side effect is written

#### Scenario: Checkbox toggles stay local
- **WHEN** TestClient toggles a V3 mutation checkbox
- **THEN** the checkbox state and related local markers change deterministically
- **AND** `PF_LAST_ACTION`, the action counter and the checkbox post-state
  marker reflect the toggle
- **AND** no persisted business data is changed

#### Scenario: Mutation handlers retain recovery markers
- **WHEN** a V3 mutation handler completes and the reset hook is invoked
- **THEN** the target-specific recovery marker proves that the baseline value
  or checkbox state was restored
- **AND** the same mutation can be run again with the same observable markers

### Requirement: V3 inert actions do not invoke business commands
The protocol lab SHALL treat inert V3 buttons as local marker updates only.

#### Scenario: Inert button click updates local action markers
- **WHEN** TestClient clicks a V3 inert button
- **THEN** only `PF_LAST_ACTION`, counters or other local markers change
- **AND** the click does not run a business command or external side effect

### Requirement: Unsupported mutation targets fail closed
The protocol lab SHALL reject V3 mutation targets that are not explicitly
allowlisted for local mutation handling.

#### Scenario: Unsupported target is rejected
- **WHEN** a mutation request targets a control that is outside the reviewed
  local mutation set
- **THEN** the request fails closed
- **AND** the fixture state remains unchanged

### Requirement: V3 mutation cases retain before/action/post/reset evidence
The protocol lab SHALL retain a recovery-proof sequence for each V3 mutation
case.

#### Scenario: Mutation proof includes the full recovery path
- **WHEN** a V3 mutation case is captured for review
- **THEN** the evidence bundle contains before, action, post and reset
  observations
- **AND** the bundle records the expected recovery path for the case

### Requirement: V3 mutation cases reset to the baseline after failure
The protocol lab SHALL restore the V1 baseline after a failed or completed V3
mutation case.

#### Scenario: Reset returns the fixture to baseline after failure
- **WHEN** a V3 mutation attempt fails before acceptance
- **THEN** the fixture can be reset to the same baseline state used before the
  attempt
- **AND** the remaining marker set matches the documented recovery expectation

### Requirement: V3 mutation evidence isolates action frames
The protocol lab SHALL keep the candidate action frame range separate from
bootstrap, background refresh and cleanup traffic.

#### Scenario: Evidence separates action and background traffic
- **WHEN** a V3 mutation proof is reviewed
- **THEN** the candidate action range is distinct from background and cleanup
  frames
- **AND** the reviewed evidence can explain any residual traffic that remains
  outside the action range

### Requirement: V3 mutation rows use a fail-closed manifest shape
The protocol lab SHALL require a machine-readable manifest row for every V3
mutation case before capture or publication.

#### Scenario: Incomplete row is rejected
- **WHEN** a mutation row is missing `target_marker`, `pre_state`, `action`,
  `post_state`, `recovery_expectation`, `mutates_business_data=false`,
  `mutation_family` or `expected_action_result_markers`
- **THEN** the row fails closed
- **AND** the fixture or runner does not accept it for capture

#### Scenario: Complete row is reviewable
- **WHEN** a mutation row provides all required manifest fields
- **THEN** the row can be reviewed against the V3 mutation contract
- **AND** the row can proceed to the next evidence step if the rest of the
  pipeline is ready

#### Scenario: Row names baseline, post-state and recovery markers
- **WHEN** a mutation row targets a string, number, date, checkbox or inert
  button case
- **THEN** the row names the target marker, initial value marker, expected
  mutated marker, post-state marker and recovery marker
- **AND** the row remains rejected until those markers are present in reviewed
  fixture evidence

### Requirement: V3 mutation evidence is published as compact reviewed links
The protocol lab SHALL publish V3 mutation proof as compact evidence links and
summaries rather than raw captures in git.

#### Scenario: Evidence publication retains compact links
- **WHEN** a V3 mutation proof is published
- **THEN** the reviewed evidence references compact bundle paths and summary
  artifacts
- **AND** raw traffic or generated replay payloads remain outside reviewed git
  changes

### Requirement: V4 dialog surfaces expose deterministic markers
The protocol lab SHALL expose warning, question and fixture-owned modal-form
surfaces through deterministic fixture-local `PF_*` markers before those
surfaces are captured or promoted.

#### Scenario: Fixture opens with V4 dialog baseline
- **WHEN** the V4 fixture surface is opened before any dialog scenario runs
- **THEN** read-only inspection can observe baseline markers for dialog family,
  lifecycle state, expected text, selected result and recovery state
- **AND** the baseline markers state that no dialog is currently active

#### Scenario: Dialog marker set names expected text
- **WHEN** a V4 warning, question or modal-form scenario is selected for
  implementation
- **THEN** the scenario declares stable expected text markers that can be
  compared in pre-state, result and recovery evidence

### Requirement: V4 dialog scenarios are classified before execution
The protocol lab SHALL classify every V4 dialog candidate before runtime
execution as fixture-local, mutation-like or special-recovery, with explicit
non-business safety constraints.

#### Scenario: Unsafe dialog candidate fails closed
- **WHEN** a V4 dialog candidate lacks a target marker, expected text marker,
  bounded lifetime, `mutates_business_data=false` or recovery expectation
- **THEN** the candidate is rejected before capture or manager-runner execution
- **AND** the rejection is routed to a later targeted card instead of broad V4
  delivery

### Requirement: V4 dialog scenarios produce deterministic results
The protocol lab SHALL provide fixture-local warning, question and modal-form
scenarios that expose deterministic text, lifecycle and selected-result
markers.

#### Scenario: Warning scenario records controlled text
- **WHEN** the V4 warning scenario is executed against the client fixture
- **THEN** the fixture exposes the expected warning text marker
- **AND** the result marker records that the warning was acknowledged or
  recovered through the documented path

#### Scenario: Question scenario records selected answer
- **WHEN** the V4 question scenario is answered through an allowlisted option
- **THEN** the fixture exposes the selected answer marker
- **AND** reset returns the question marker set to the baseline state

#### Scenario: Modal form opens and closes with markers
- **WHEN** a fixture-owned V4 modal form scenario runs
- **THEN** the open, close and result markers identify the modal lifecycle
- **AND** no OS, file, print or external-service dialog is involved

### Requirement: V4 expected errors are distinguishable from infrastructure failures
The protocol lab SHALL expose expected-error scenarios with controlled
diagnostic markers and SHALL keep infrastructure failures classified
separately.

#### Scenario: Expected error returns diagnostic marker
- **WHEN** a V4 expected-error scenario is executed
- **THEN** the resulting diagnostic text matches the expected error marker
- **AND** the scenario row is not treated as an infrastructure failure

#### Scenario: Unexpected error fails closed
- **WHEN** a V4 scenario returns an error that lacks the expected diagnostic
  marker
- **THEN** the row is classified as infrastructure failure, rejected or blocked
  according to the evidence contract
- **AND** no accepted protocol claim is published from that row

### Requirement: V4 wait scenarios are bounded and observable
The protocol lab SHALL limit V4 wait/progress scenarios to bounded
fixture-local durations and expose observable start, progress, completion,
cancel and recovery markers.

#### Scenario: Bounded wait completes
- **WHEN** a V4 bounded wait scenario starts
- **THEN** the fixture exposes wait-start and progress markers
- **AND** the scenario completes within the documented maximum duration with a
  completion marker

#### Scenario: Bounded wait is cancelled or retried
- **WHEN** a V4 wait scenario is cancelled or retried through the reviewed path
- **THEN** the fixture exposes the cancel or retry marker
- **AND** reset returns the wait marker set to the baseline state

### Requirement: V4 scenarios recover to the baseline
The protocol lab SHALL prove that every V4 warning, question, modal,
expected-error and bounded-wait scenario can return to the V1 baseline through
documented recovery markers.

#### Scenario: Dialog scenario recovers
- **WHEN** a V4 dialog or modal scenario completes, is cancelled or fails
- **THEN** the recovery path reads the V4 marker set after cleanup
- **AND** the marker set matches the documented baseline or a documented
  candidate-only residual state

#### Scenario: Wait scenario recovers after cancel or retry
- **WHEN** a V4 bounded wait scenario is cancelled, retried or times out
- **THEN** recovery evidence records the cleanup path and final wait markers
- **AND** the fixture can run the same scenario again after reset

### Requirement: V4 recovery evidence separates phase ranges
The protocol lab SHALL keep V4 dialog/action, background, expected-error and
recovery evidence ranges separate before any V4 row is promoted.

#### Scenario: Capture review labels V4 phases
- **WHEN** a V4 scenario publishes compact reviewed evidence
- **THEN** the report identifies pre-read, action-or-dialog, result,
  background and recovery phases where those phases exist
- **AND** unresolved or ambiguous ranges remain candidate, blocked or rejected
  rather than accepted

### Requirement: V4 expected errors require matching diagnostics
The protocol lab SHALL classify a V4 expected-error row as expected only when
the controlled diagnostic marker matches the reviewed scenario contract.

#### Scenario: Diagnostic mismatch fails closed
- **WHEN** a V4 expected-error row returns an unreviewed diagnostic or missing
  marker
- **THEN** the row is classified as infrastructure failure, rejected or blocked
- **AND** the recovery path must still restore the fixture baseline before
  another case runs

### Requirement: V4 corpus rows use a fail-closed manifest shape
The protocol lab SHALL define every V4 dialog, expected-error and bounded-wait
candidate through a reviewed manifest row before capture or evidence
publication.

#### Scenario: V4 manifest row is complete
- **WHEN** a V4 manifest row includes scenario family, target marker, expected
  text or diagnostic marker, pre-state, action, result expectation, recovery
  expectation, `mutates_business_data=false` and expected result markers
- **THEN** tooling or reviewers can route the row to the matching V4 scenario
  family
- **AND** the row remains candidate until replay/probe or typed contract proof
  satisfies the evidence gate

#### Scenario: V4 manifest row is incomplete
- **WHEN** a V4 manifest row lacks required common fields or required
  family-specific fields such as bounded wait duration or expected diagnostic
  marker
- **THEN** the row fails closed before capture or publication

### Requirement: V4 evidence separates expected errors from infrastructure failures
The protocol lab SHALL publish V4 expected-error evidence with result markers
that distinguish reviewed expected diagnostics from infrastructure failures.

#### Scenario: Expected diagnostic is published
- **WHEN** a V4 expected-error row produces the reviewed diagnostic marker
- **THEN** the compact evidence records the diagnostic marker, recovery result
  and non-business safety classification
- **AND** accepted status still depends on replay/probe or typed contract proof

#### Scenario: Infrastructure failure remains separate
- **WHEN** a V4 run fails without the reviewed expected diagnostic marker
- **THEN** the compact evidence records an infrastructure failure, rejected or
  blocked reason
- **AND** the row is not promoted as an expected-error protocol claim

### Requirement: V4 runtime artifacts stay outside reviewed git
The protocol lab SHALL keep raw V4 captures, platform logs and generated
replay payloads under ignored runtime paths while retaining compact reviewed
evidence links.

#### Scenario: V4 evidence is published compactly
- **WHEN** a V4 proof bundle is retained
- **THEN** reviewed Markdown or JSON summaries link frame ranges, markers,
  normalized hashes and recovery results
- **AND** raw capture payloads remain outside committed documentation

### Requirement: Demo button target selection is read-only and explicit
The protocol lab SHALL select a demo real-button pilot target through a
read-only target-selection record before any safety classification or runtime
action is attempted.

#### Scenario: Demo button target is selected
- **WHEN** a demo button is selected for the pilot
- **THEN** the selection record includes the demo form path, element path,
  visible caption or marker, enabled and visible state, target owner, source
  evidence route and planned evidence bundle path
- **AND** the selected target is not clicked by the selection step

#### Scenario: No eligible target is found
- **WHEN** read-only discovery cannot identify a concrete button without
  ambiguity
- **THEN** the selection result records `blocked`, `unsupported` or `deferred`
  with reason, owner route and residual risk
- **AND** downstream classification and capture steps do not invent a target

### Requirement: Rejected demo button candidates remain visible
The protocol lab SHALL preserve rejected or deferred demo button candidates in
compact planning evidence instead of silently omitting them.

#### Scenario: Demo button candidate is rejected
- **WHEN** a candidate appears to be a business command, write action, external
  side effect or otherwise unsafe target
- **THEN** the selection evidence records the candidate caption or marker,
  rejection reason, owner route and residual risk
- **AND** the candidate is not passed to runtime execution

### Requirement: Demo button classification fails closed before execution
The protocol lab SHALL classify a selected demo real-button target before any
runtime click or capture is attempted.

#### Scenario: Demo button is classified as capture-eligible
- **WHEN** the selected demo button has a complete manifest row with target
  marker, pre-state, concrete action, post-state, recovery expectation,
  expected action result markers, allowlisted action family and
  `mutates_business_data=false`
- **THEN** the classification evidence may mark the row as `safe_ui_action` or
  `inert_local_action` for the guarded capture step
- **AND** the evidence records the source facts that justify non-mutating
  behavior

#### Scenario: Demo button cannot be classified safely
- **WHEN** the selected target lacks required manifest fields, has unknown side
  effects or cannot justify `mutates_business_data=false`
- **THEN** the row is marked `blocked`, `unsupported` or routed to V3 mutation
  work before execution
- **AND** no runtime click is attempted by the classification step

### Requirement: Demo business buttons are routed to mutation work
The protocol lab SHALL route demo buttons that execute business commands or
require rollback to V3 or later mutation/recovery work rather than V2 capture.

#### Scenario: Button is a business mutation
- **WHEN** classification finds object writes, save, post, delete, fill,
  import, export, exchange, persisted settings or external side effects
- **THEN** the classification decision records a V3 routing reason, owner route
  and residual risk
- **AND** the guarded capture change receives no executable V2 row for that
  button

### Requirement: Demo button pilot capture executes only reviewed safe rows
The protocol lab SHALL execute a demo real-button pilot capture only when the
selected row has passed safety classification and still matches runtime
pre-state.

#### Scenario: Reviewed row is executed
- **WHEN** a selected demo button row is complete, non-mutating, allowlisted and
  runtime pre-state matches the manifest
- **THEN** the capture may execute the single reviewed action
- **AND** the run records pre-read, action-start, action-end, post-read and
  recovery or recovery-read phase evidence

#### Scenario: Capture gate fails
- **WHEN** the classification is missing, incomplete, unsafe, mutating or the
  live pre-state does not match the manifest
- **THEN** the capture records a blocked or rejected summary without clicking
  the button
- **AND** the row is routed to publication as non-accepted evidence

### Requirement: Demo button capture keeps raw runtime artifacts ignored
The protocol lab SHALL keep raw demo-button pilot runtime output outside
reviewed git while retaining compact evidence summaries.

#### Scenario: Runtime output is produced
- **WHEN** the guarded capture writes traffic logs, process logs, screenshots or
  generated replay payloads
- **THEN** raw output remains under ignored runtime or artifact paths
- **AND** reviewed evidence links only compact summaries, phase labels, frame
  ranges, markers and recovery status

### Requirement: Demo button pilot publication states final status
The protocol lab SHALL publish every demo real-button pilot result with an
explicit final status and compact evidence links.

#### Scenario: Demo button pilot is published
- **WHEN** the target selection, classification and capture or blocked result
  have been reviewed
- **THEN** publication records the selected target, safety classification,
  attempted or skipped action, recovery status, evidence paths, final status
  and residual risk
- **AND** raw runtime output remains outside reviewed git

#### Scenario: Accepted status is claimed
- **WHEN** the demo button pilot is published as accepted
- **THEN** the publication links same-action replay, direct Python-manager
  probe or typed contract proof for the non-mutating action
- **AND** accepted-mapping output includes only rows supported by that proof

#### Scenario: Proof is missing
- **WHEN** the pilot has target, classification or capture evidence but lacks
  accepted replay, direct probe or typed contract proof
- **THEN** publication marks the row candidate, blocked, rejected or another
  explicit non-accepted status
- **AND** accepted-mapping output excludes the row

### Requirement: Demo mutation outcomes route to V3
The protocol lab SHALL route demo button results that write data, execute
business commands or require rollback to V3 or later mutation/recovery work.

#### Scenario: Demo button requires mutation handling
- **WHEN** classification or capture shows the selected button is mutating,
  business-owned, rollback-dependent or outside the V2 allowlist
- **THEN** the publication records `routed_to_v3` or equivalent blocker status
  with owner route, evidence links and residual risk
- **AND** no accepted safe-action mapping is published for the row

### Requirement: Real demo mutation targets are selected before execution
The protocol lab SHALL select real demo mutation candidates through a reviewed
read-only target record before manifest validation or guarded execution.

#### Scenario: First row set is selected
- **WHEN** the real-demo mutation pilot chooses candidate rows
- **THEN** each selected row records `target_id`, form or object path, element
  path, visible caption or marker, operation family, expected mutation,
  recovery feasibility, evidence route, owner and residual risk
- **AND** the selected set remains small enough to review before execution

#### Scenario: Candidate is rejected or deferred
- **WHEN** a real demo form action cannot be reviewed safely, lacks a stable
  target marker or has unclear recovery feasibility
- **THEN** the target-selection evidence records the candidate as rejected,
  deferred or blocked with reason, owner route and residual risk
- **AND** no click or write is attempted for that candidate

### Requirement: Target selection does not create mutation proof
The protocol lab SHALL keep target selection separate from runtime execution,
frame evidence and accepted protocol mappings.

#### Scenario: Target selection completes
- **WHEN** the target-selection summary is published for downstream manifest
  review
- **THEN** the summary contains only read-only evidence and candidate metadata
- **AND** it does not claim action-frame ranges, replay status, direct
  Python-manager proof or accepted mapping output

### Requirement: Real demo mutation manifest rows are complete before execution
The protocol lab SHALL define every real demo mutation attempt through a
complete reviewed manifest row before guarded execution.

#### Scenario: Manifest row is executable
- **WHEN** a real demo mutation row is selected for guarded execution
- **THEN** the row records `target_id`, object or form path, element path,
  target marker, operation family, pre-state, action, expected post-state,
  recovery expectation, `mutates_business_data`, residual risk and proof route
- **AND** `mutates_business_data=true` is allowed only when the recovery or
  cleanup plan is explicit and reviewed

#### Scenario: Manifest row fails closed
- **WHEN** a real demo mutation row is incomplete, unsupported, lacks recovery,
  has ambiguous target state or includes unapproved external side effects
- **THEN** the row is rejected or blocked before guarded execution
- **AND** the retained row records reason, owner route and residual risk

### Requirement: Real demo mutation statuses are proof-gated
The protocol lab SHALL classify real demo mutation rows with explicit status
and proof route before publication.

#### Scenario: Row status is recorded
- **WHEN** a real demo mutation row is retained for corpus review
- **THEN** the row status is one of `accepted`, `candidate`, `rejected`,
  `blocked`, `partial` or `timeout`
- **AND** the row records whether evidence came from replay, direct
  Python-manager probe, typed contract proof, live capture only or blocked
  validation

#### Scenario: Accepted output is requested
- **WHEN** a real demo mutation row is proposed for accepted mapping output
- **THEN** the row has same-action replay, direct Python-manager probe or
  accepted typed contract proof for the same action
- **AND** live visual success or manifest completeness alone does not create
  accepted protocol knowledge

### Requirement: Real demo mutation execution is guarded by manifest and pre-state
The protocol lab SHALL execute real demo mutation rows only when a reviewed
manifest row matches the current runtime target and pre-state.

#### Scenario: Reviewed row executes
- **WHEN** a real demo mutation row is complete, recoverable, scoped to the
  disposable demo10413 lab and the active form, target marker and pre-state
  match the manifest
- **THEN** the guarded pilot may execute the reviewed action
- **AND** the run records pre-state, action-start, action-end, post-state and
  recovery or cleanup phase evidence

#### Scenario: Execution gate fails
- **WHEN** the manifest is missing, incomplete, unrecoverable, externally
  side-effecting or the live pre-state does not match the reviewed row
- **THEN** the guarded pilot records a blocked or rejected summary without
  executing the action
- **AND** no accepted mapping output is produced for that row

#### Scenario: Live runtime preflight fails
- **WHEN** the live runtime preflight for the selected runtime route fails
  before any 1C process is started or attached
- **THEN** the guarded pilot records a `runtime_gap` blocker with the retained
  preflight result before any mutation attempt
- **AND** no 1C process is started, no action executes and no accepted mapping
  output is produced

### Requirement: Real demo mutation recovery is retained for every executed row
The protocol lab SHALL retain cleanup, reset or documented residue evidence for
each real demo mutation row that executes.

#### Scenario: Mutation is recovered
- **WHEN** a real demo mutation action changes or creates demo data
- **THEN** the pilot runs the reviewed recovery or cleanup path
- **AND** final-state evidence records either baseline restoration, removal of
  `QA_MCP_*` data or acceptable residue with owner and residual risk

#### Scenario: Recovery cannot be proven
- **WHEN** recovery markers, cleanup proof or final-state evidence are missing
  after a mutation attempt
- **THEN** the row remains blocked, rejected, partial or candidate
- **AND** the row is not promoted as accepted mutation evidence

### Requirement: Real demo mutation action frames are isolated from background traffic
The protocol lab SHALL separate action, background/refresh and recovery frame
ranges before using real demo mutation rows as corpus evidence.

#### Scenario: Action frames are isolated
- **WHEN** a guarded real-demo mutation run has phase events and reviewable
  traffic
- **THEN** the compact evidence records action frame range, background or
  refresh ranges and recovery ranges separately for each attempted row
- **AND** refresh-only or recovery-only traffic is not treated as proof of the
  mutation action

#### Scenario: Frame boundary is ambiguous
- **WHEN** action frames cannot be joined to the manifest row, phase events or
  chunk counters reliably
- **THEN** the row remains `candidate`, `blocked`, `partial`, `timeout` or
  `rejected` with unresolved reason, owner route and residual risk
- **AND** the row is not accepted as protocol knowledge

### Requirement: Real demo mutation rows require proof before accepted status
The protocol lab SHALL require same-action replay, direct Python-manager probe
or accepted typed contract proof before a real demo mutation row is accepted.

#### Scenario: Row is accepted
- **WHEN** a real demo mutation row is published as accepted
- **THEN** it has separated action-frame evidence plus same-action replay,
  direct Python-manager probe or accepted typed contract proof for that action
- **AND** the row retains normalized hash, dynamic-field, operation-token,
  response-marker, recovery and evidence-path details when available

#### Scenario: Proof is missing
- **WHEN** a row has runtime action and recovery evidence but lacks accepted
  replay, direct probe or typed contract proof
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** accepted mapping output excludes the row

### Requirement: Real demo mutation corpus publication states final row status
The protocol lab SHALL publish real demo mutation pilot outcomes with explicit
row status, evidence links and residual risk.

#### Scenario: Real demo mutation pilot is published
- **WHEN** target selection, manifest review, guarded execution or blocked
  outcome and frame-isolation review have completed
- **THEN** publication records every selected or attempted row with target id,
  operation family, mutation flag, recovery status, frame-isolation status,
  proof route, final status, evidence paths and residual risk
- **AND** the API coverage case map and generated coverage report are
  refreshed when row statuses changed
- **AND** publication states whether the mutation scheme is proven well enough
  to plan the follow-up batch corpus card
- **AND** raw runtime output remains outside reviewed git

#### Scenario: Row is blocked or rejected
- **WHEN** a selected real-demo mutation row cannot execute, cannot recover,
  lacks frame evidence or violates the manifest contract
- **THEN** publication records the blocker or rejection reason, owner route and
  next actionable evidence need
- **AND** the row is not omitted from corpus coverage notes

### Requirement: Real demo mutation accepted output is proof-gated
The protocol lab SHALL keep accepted mutation output empty unless accepted
proof exists for the same real-demo action.

#### Scenario: Accepted row is published
- **WHEN** a real demo mutation row is added to accepted output
- **THEN** the publication links separated action-frame evidence plus
  same-action replay, direct Python-manager probe or accepted typed contract
  proof
- **AND** the row records recovery status and any residual demo data risk

#### Scenario: Accepted proof is missing
- **WHEN** the pilot has target, manifest, runtime or frame evidence but lacks
  accepted replay, direct probe or typed contract proof
- **THEN** accepted output remains empty for that row
- **AND** the row is published as candidate, blocked, rejected, partial or
  timeout with evidence paths and residual risk

### Requirement: Display-bound tools select an explicit backend
The protocol lab SHALL route display-bound MCP tools through an explicit
display backend that preserves local Linux behavior and can delegate to a
configured remote host agent in model-B remote-client mode.

#### Scenario: Local backend preserves Linux display behavior
- **WHEN** remote-client mode is not enabled
- **THEN** display-bound tools use the existing Linux XTEST, screenshot and
  OS-window primitives
- **AND** their public MCP parameters and result shapes remain compatible with
  the current local TestClient workflow

#### Scenario: Remote backend handles model-B display calls
- **WHEN** `QA_MCP_REMOTE_CLIENT=1` and `QA_MCP_HOST_AGENT` names a reachable
  host agent
- **THEN** display-bound tools route keyboard, mouse, screenshot and OS-window
  primitive requests to the remote agent
- **AND** higher-level locate and protocol orchestration remain in Python

### Requirement: Remote display backend fails closed with actionable diagnostics
The protocol lab SHALL return structured display-backend diagnostics instead of
running Linux display commands when model-B remote-client mode has no usable
host display agent.

#### Scenario: Remote mode lacks agent configuration
- **WHEN** a display-bound MCP tool is called with `QA_MCP_REMOTE_CLIENT=1` and
  no `QA_MCP_HOST_AGENT`
- **THEN** the tool returns `ok=false` with a stable backend error code
- **AND** the result explains that the Windows host-side input/screenshot agent
  must be installed or configured

#### Scenario: Unguarded display tool is normalized
- **WHEN** `open_external_processor` is called in model-B remote-client mode
- **THEN** it follows the same display backend dispatch and diagnostics as the
  other display-bound tools
- **AND** it does not crash by directly invoking Linux screenshot or XTEST
  helpers

### Requirement: Windows host agent exposes display primitives
The protocol lab SHALL provide a Windows host-side agent that exposes the
display primitives needed by model-B remote-client mode without requiring 1C
libraries or a 1C TestManager process.

#### Scenario: Agent reports version and health
- **WHEN** the container connects to the host agent
- **THEN** `GET /version` returns an agent version and binary hash
- **AND** `GET /health` reports whether the agent is running in an interactive
  desktop session that can attempt input and screenshot primitives

#### Scenario: Agent sends Unicode text
- **WHEN** the Python backend asks the agent to type Unicode text
- **THEN** the agent uses Win32 `SendInput` Unicode key events
- **AND** the result reports success or a structured foreground/input error

#### Scenario: Agent captures a PNG screenshot
- **WHEN** the Python backend asks the agent for a screenshot of the target
  client window
- **THEN** the agent returns a PNG image of the Windows-rendered 1C client
- **AND** the response includes target-window diagnostics sufficient to
  distinguish blank, hidden and missing-window captures

### Requirement: Host agent transport is host-scoped and token-protected
The protocol lab SHALL expose the Windows host agent over a host-scoped HTTP
port with token protection for primitive endpoints.

#### Scenario: Primitive endpoint lacks token
- **WHEN** a primitive request omits or mismatches the configured token
- **THEN** the agent rejects the request with a stable authentication error
- **AND** it does not inject input, click, enumerate windows or return
  screenshots for that request

#### Scenario: Agent listens on host-only address
- **WHEN** the agent starts with the default configuration
- **THEN** it binds to a loopback or host-only address intended for Docker
  Desktop `host.docker.internal` access
- **AND** documentation states how to override the bind address for the lab
  only when local policy permits it

### Requirement: Host agent install is an explicit Windows host step
The protocol lab SHALL provide a documented Windows host-side install command
that installs the host display agent into the interactive user session without
requiring the Linux container to copy or execute files on a cold host.

#### Scenario: Installer registers interactive startup
- **WHEN** the install command is run on the Windows host
- **THEN** it places the host agent executable in the documented location
- **AND** it registers an interactive logon Scheduled Task for the current
  user rather than a Session-0 service

#### Scenario: Installer configures access
- **WHEN** the install command completes successfully
- **THEN** it records the selected host-agent port and token configuration
- **AND** it configures or reports the firewall rule needed for Docker Desktop
  access through `host.docker.internal`

### Requirement: Remote backend verifies agent version and hash
The protocol lab SHALL verify the host agent version and binary hash before
using remote display primitives.

#### Scenario: Agent version matches expected version
- **WHEN** `/version` returns the expected version and hash
- **THEN** the remote display backend allows primitive calls
- **AND** the handshake result is available for diagnostics

#### Scenario: Agent is absent or mismatched
- **WHEN** the host agent cannot be reached or its version/hash differs from
  the expected value
- **THEN** remote display tools fail closed with a stable error code
- **AND** the error names the exact Windows install/update command
- **AND** v1 does not auto-replace the host binary

### Requirement: Model-B remote display subset is live-verified
The protocol lab SHALL retain compact live evidence that model-B remote-client
mode can recover the display-bound input/screenshot subset through the Windows
host agent.

#### Scenario: Genuine object attribute edit is proven
- **WHEN** `write_form_value_xtest` is executed through the remote display
  backend against the Windows-rendered 1C client
- **THEN** retained evidence shows a genuine Unicode input event reached the
  target managed-form field
- **AND** the proof records screenshot or read-only data assertion evidence for
  the resulting state

#### Scenario: Host screenshot is proven
- **WHEN** `capture_screenshot` is executed through the remote display backend
- **THEN** retained evidence includes a PNG or sanitized screenshot summary
  produced from the host-rendered 1C window
- **AND** the proof distinguishes the host screenshot route from the Linux X11
  route

### Requirement: Remaining display tools publish explicit statuses
The protocol lab SHALL publish a compact status table for each display-bound
tool recovered by the host agent and for any tool intentionally deferred or
blocked.

#### Scenario: Display tool status is published
- **WHEN** the model-B display verification bundle is created
- **THEN** it lists `capture_screenshot`, `send_keys`,
  `write_form_value_xtest`, `write_form_fields_by_label`,
  `set_table_date_cell`, `get_window_list` and `open_external_processor`
- **AND** each row records passed, blocked, deferred or not-applicable status
  with evidence path or residual risk

#### Scenario: Raw runtime output remains ignored
- **WHEN** live verification produces screenshots, logs or temporary payloads
- **THEN** raw output remains under ignored runtime or artifact paths unless a
  sanitized curated file is explicitly selected for review
- **AND** reviewed docs link only compact evidence summaries

### Requirement: TestClient launch prepares Linux runtime libraries

The protocol lab SHALL prepare the native Linux TestClient process environment
so a system `libgcc_s.so.1` can be preloaded before `1cv8` starts when the
operator has not opted out.

#### Scenario: System libgcc is autodetected for launch

- **WHEN** `launch_test_client` starts a Linux `1cv8` process and
  `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD` is unset
- **THEN** qa-mcp prepends the first existing supported system libgcc path to
  the child `LD_PRELOAD`
- **AND** any existing `LD_PRELOAD` entries remain after the qa-mcp entry
- **AND** the returned status identifies that a non-secret preload path was
  applied

#### Scenario: Operator disables or overrides preload

- **WHEN** `QA_MCP_TESTCLIENT_LIBGCC_PRELOAD` is set to an empty string
- **THEN** qa-mcp starts the child without adding a libgcc preload
- **AND** when the variable is set to a non-empty value, qa-mcp uses that value
  instead of autodetection

### Requirement: TestClient launch failures include bounded diagnostics

The protocol lab SHALL return enough bounded launch evidence to distinguish a
native process crash, a transient TPort and a post-listener startup failure
without copying full runtime logs into MCP responses.

#### Scenario: Launch times out after process stderr is written

- **WHEN** `launch_test_client` fails because the TestClient TPort never starts
  listening
- **THEN** qa-mcp tears down only the process and display resources it owns
- **AND** the raised diagnostic includes the port, timeout, output directory,
  process return code when available and bounded tail lines from launch logs
- **AND** sensitive values such as the infobase password are not included.

#### Scenario: TestClient exits after transient listener readiness

- **WHEN** TPort becomes connectable but the owned TestClient exits during the
  default 20-second bounded stability window
- **THEN** launch fails instead of returning an alive/listening success payload
- **AND** bounded password-redacted output identifies the post-listener failure
- **AND** owned client and display resources are cleaned.

#### Scenario: Launch preserves the cold-client manager session

- **WHEN** local readiness verifies a newly listening TPort
- **THEN** it does not read the TestClient protocol greeting
- **AND** the first descriptor or scenario tool can own the cold-client manager
  session.

#### Scenario: Launch target TPort is already occupied

- **WHEN** a local `launch_test_client` request targets a TPort that is already
  listening
- **THEN** launch fails before changing Apache or starting Xvfb or 1C
- **AND** the existing endpoint is not attributed to a new lifecycle PID.

#### Scenario: Caller disconnects during local readiness

- **WHEN** qa-mcp has started the local client and Xvfb but the MCP caller
  disconnects before readiness completes
- **THEN** an exact ownership marker already records their PID, start time and
  process group
- **AND** a later stateless cleanup can validate and terminate only those
  recorded resources.

#### Scenario: Stateless cleanup follows a stale client marker

- **WHEN** the primary client PID from an exact qa-mcp ownership marker has
  already exited but its recorded Xvfb is still alive
- **THEN** cleanup validates the Xvfb PID, start time, process group and command
  before terminating it
- **AND** it removes the ownership marker after all owned resources are absent
- **AND** an unowned, reused or mismatched process remains a refusal.

### Requirement: Running TestClient endpoints can be attached without ownership

The protocol lab SHALL expose an attach path for an already-listening
`/TESTCLIENT` endpoint that can create the same protocol session entry point as
a lifecycle-owned launch while preserving external process ownership.

#### Scenario: Listening endpoint is attached

- **WHEN** an operator provides a TestClient host and TPort that is already
  listening
- **THEN** qa-mcp returns an attached handle whose status records
  `attached=true` and `owns_process=false`
- **AND** the handle can create a `TestClientSession` for read-only protocol
  tools
- **AND** stopping the handle does not terminate the external TestClient
  process

#### Scenario: Missing endpoint fails closed

- **WHEN** an operator attempts to attach to a host and TPort that is not
  listening
- **THEN** qa-mcp returns a clear attach diagnostic
- **AND** no process cleanup is attempted because qa-mcp owns no external
  process

### Requirement: Attached TestClient endpoints drive replay-backed tools

The protocol lab SHALL let an already-listening `/TESTCLIENT` endpoint
attached through `attach_test_client` drive the same replay-backed
introspection, read and write/session tool paths as a qa-mcp-launched client
while preserving external process ownership.

#### Scenario: Attached endpoint returns a real form descriptor

- **WHEN** `attach_test_client` records a listening out-of-band TestClient
  endpoint
- **AND** `read_form_descriptor` is run against an existing form through that
  attached endpoint
- **THEN** qa-mcp uses the attached endpoint session route instead of an
  unrelated ad hoc session
- **AND** the result includes non-empty live descriptor evidence such as
  `opened`, `elements`, `element_count` or `fields`
- **AND** an attach/bootstrap failure is returned as a bounded diagnostic
  rather than `{opened:null, fields:{}}` with no failure phase

#### Scenario: Attached endpoint is available to write/session tools

- **WHEN** a replay-backed write or scenario tool is invoked after a
  successful attach
- **THEN** qa-mcp resolves the same attached endpoint context for the tool
  session factory unless the caller explicitly overrides `host` and `port`
- **AND** the tool result preserves the existing write/action safety result
  contract
- **AND** stopping or cleaning up the attached context does not terminate the
  external TestClient process

#### Scenario: Missing attached endpoint fails closed

- **WHEN** a tool is asked to use an attached endpoint that is no longer
  listening
- **THEN** qa-mcp returns a stable attach-session diagnostic that includes the
  host, port and failed phase
- **AND** no owned-process cleanup is attempted for the external TestClient

### Requirement: Bundled captures carry neutral descriptive identities
The bundled capture directories SHALL use **neutral, descriptive** names
(e.g. `demo-write`, `listform-read`, `cellread`) that carry **no card numbers or
capture dates**, in both the `_bundled/<version>/captures/` data tree and the
`capture=` default values exposed by the MCP tool schemas. The engine SHALL
resolve and replay the renamed captures unchanged; the descriptive meaning is
preserved (the card number + date move to git history + the board).

#### Scenario: Shipped capture identities carry no internal R&D trace
- **WHEN** the bundled captures and the tool `capture=` defaults are inspected
- **THEN** their names contain no `card N` token and no capture-date suffix
- **AND** each name still describes the capture's purpose (e.g. `demo-write`,
  `listform-read`)

#### Scenario: Renamed captures still resolve and replay
- **WHEN** a tool uses a renamed bundled capture as its default (or it is resolved
  via `resolve_capture_dir`)
- **THEN** the capture resolves from `_bundled/<version>/captures/<neutral-name>/`
  and the engine replays it with identical behavior to the pre-rename name
- **AND** the offline `pytest` suite stays green

### Requirement: Native write tools can open target forms by nav-link
The qa-mcp native write path SHALL support an explicit `open_link` parameter for field-write operations so a write can target an arbitrary managed form without replaying a fixture form as the foreground target.

#### Scenario: Open-link write targets a resolved form
- **WHEN** a caller invokes a native field-write tool with `open_link` and a field name
- **THEN** qa-mcp opens the nav-link target in the TestClient session before sending write frames
- **AND** the result identifies the requested `open_link`, the opened form or blocked-open reason, and the target field

#### Scenario: Fixture write remains compatible
- **WHEN** a caller omits `open_link`
- **THEN** qa-mcp uses the existing capture-backed fixture setup path
- **AND** existing fixture field writes keep their previous result shape and commit semantics

### Requirement: Open-link write evidence is explicit
New claims about config-agnostic write behavior SHALL include retained evidence that identifies the target form, field, write result and verification method without committing raw captures or local runtime logs.

#### Scenario: Live open-link write proof is retained
- **WHEN** a live TestClient proof is run for an open-link write
- **THEN** the evidence bundle records the target nav-link, field, command/tool call summary, result status and read-back or provider-gap outcome
- **AND** raw capture streams and platform logs remain under ignored runtime artifact paths

### Requirement: Native write scenarios can fill and save a record in one session
The qa-mcp write scenario tool SHALL execute field input steps and explicit save/command steps on one live native write session when the scenario is intended to create or persist a record.

#### Scenario: Multi-field create flow saves successfully
- **WHEN** a write scenario opens a create form, sets multiple fields and invokes a save command
- **THEN** qa-mcp keeps the same TestClient/write session for all fill and save steps
- **AND** the result reports each step status, the save command status and the persistence verification status

#### Scenario: Unsupported write step fails closed
- **WHEN** a write scenario contains a step that qa-mcp cannot execute safely
- **THEN** the scenario result marks that step as an error with the step kind and reason
- **AND** qa-mcp does not silently skip the step or report the scenario as passed

### Requirement: Create-flow persistence proof is retained
The qa-mcp create/write flow SHALL require read-back, list-read, live-data or explicit provider-gap evidence before a persisted record creation claim is accepted.

#### Scenario: Persistence verification is available
- **WHEN** the save command reports accepted
- **THEN** qa-mcp records a read-back, list-row or data-layer assertion summary showing the created record state
- **AND** cleanup evidence or cleanup residual risk is recorded for the created test data

### Requirement: Native write tools can set form-level date fields
The qa-mcp native write path SHALL provide a form-level date field operation for managed form `EditField` date attributes, separate from table date-cell calendar operations.

#### Scenario: Form-level date write succeeds
- **WHEN** a caller requests a `DD.MM.YYYY` value for a form-level date field on an opened or open-link form
- **THEN** qa-mcp validates the date format before live input
- **AND** the result reports `surface=form_field_date`, the target field, the requested date and the read-back or verification status

#### Scenario: Grid date-cell path remains separate
- **WHEN** a caller uses `set_table_date_cell`
- **THEN** qa-mcp continues to treat the target as a tabular date cell
- **AND** form-level date-field handling does not change the table-cell calendar result contract

### Requirement: Date write evidence identifies formatting behavior
Form-level date write evidence SHALL record the requested date and the observed read-back formatting so date-prefix acceptance, time suffixes or provider gaps are reviewable.

#### Scenario: Date read-back has a time suffix
- **WHEN** a date field read-back includes a time component after the requested date
- **THEN** qa-mcp may accept the write by date prefix
- **AND** the retained evidence records the full read-back string and the prefix comparison

### Requirement: Native write tools foreground bare-create links
The qa-mcp native write path SHALL foreground `e1cib/data/<metadata>` links
without a `?ref=` parameter before label-based write input begins.

#### Scenario: Bare-create link foregrounds for label input
- **WHEN** a caller invokes `write_form_fields_by_label` with
  `open_link="e1cib/data/Справочник.Валюты"`
- **THEN** qa-mcp uses a create-scoped foreground route that accepts the
  list-read replay tail as partial only after the create form renders
- **AND** the result identifies the foreground method and the opened form or a
  structured foreground failure reason

#### Scenario: Existing foreground modes remain isolated
- **WHEN** a caller provides a list link or a `?ref=` data link
- **THEN** qa-mcp keeps the existing list/record foreground replay behavior
- **AND** the create-form foreground route is not selected

### Requirement: Bare-create foreground proof is retained
New live claims about bare-create write foregrounding SHALL retain UI evidence
for the active form without committing raw captures or platform logs.

#### Scenario: Create foreground evidence names target forms
- **WHEN** live TestClient proof is run for bare-create foregrounding
- **THEN** retained evidence records the target nav-link, foreground method,
  active window or form tree, screenshot or fallback diagnostic and result
  status
- **AND** raw captures, screenshots and platform logs remain under ignored
  runtime or artifact paths unless curated explicitly

### Requirement: Open-link write scenarios set reference fields
The qa-mcp native write scenario path SHALL support an explicit reference field
step for an open-link managed form when the target field is addressed by visible
label and the requested value is a reference display value.

#### Scenario: Owner reference is selected on a create form
- **WHEN** a write scenario opens `e1cib/data/Справочник.ДоговорыКонтрагентов`
  and requests `Владелец=<Контрагент>`
- **THEN** qa-mcp targets the `Владелец` field as a reference field rather than
  plain text
- **AND** the step result records whether the field was targeted and whether
  the requested owner was selected

#### Scenario: Unsupported reference write fails closed
- **WHEN** qa-mcp cannot locate the reference field, open the chooser, find the
  requested value or disambiguate the selection
- **THEN** the reference step is reported as an error with a stable reason
- **AND** the scenario does not continue to a save command as if the owner had
  been set

### Requirement: Reference field evidence separates routing and selection
Live reference-write evidence SHALL distinguish field targeting, chooser
interaction and selected value verification.

#### Scenario: Reference evidence is retained
- **WHEN** live TestClient proof is run for an open-link reference write
- **THEN** retained evidence records the target nav-link, field label, requested
  reference value, selector result and active-form evidence
- **AND** raw screenshots, logs and local runtime details remain under ignored
  artifact paths unless a curated summary is explicitly selected for review

### Requirement: Create scenarios require persistence verification for save claims
The qa-mcp open-link create scenario path SHALL report a persisted-record claim
as accepted only when a read-back, list-read or data assertion verifies the
created record state.

#### Scenario: Saved contract is verified by data assertion
- **WHEN** a create scenario saves a `ДоговорыКонтрагентов` record
- **THEN** qa-mcp records a persistence verification summary containing the
  identifying fields, observed `Наименование`, observed `Основной` and
  assertion status
- **AND** a missing or failed assertion keeps the scenario from reporting the
  persistence claim as passed

#### Scenario: Provider gap remains explicit
- **WHEN** no read-back, list-read or live-data route is available for the saved
  record
- **THEN** qa-mcp reports a provider-gap or verification error with owner route
  and expected evidence type
- **AND** the scenario does not silently accept the save as verified

### Requirement: Mutation proof requires cleanup evidence
The qa-mcp create/write flow SHALL require cleanup evidence or explicit
unresolved-leftover diagnostics before accepting live mutation proof.

#### Scenario: Cleanup proof is retained after create
- **WHEN** a live create proof saves one or more demo records
- **THEN** retained evidence records created object identifiers, cleanup action,
  final-state check and unresolved leftovers
- **AND** cleanup artifacts remain under ignored runtime or artifact paths unless
  a curated summary is selected for review

#### Scenario: Missing cleanup blocks acceptance
- **WHEN** a save proof has no cleanup route and no explicit residual-risk
  record
- **THEN** qa-mcp reports the cleanup evidence as missing
- **AND** the mutation proof is not archive-ready

### Requirement: Short and single-word form labels are reliably localized

`locate_text`-backed label targeting SHALL locate short, single-word and reference field labels
(for example «Владелец», «Код», «Основной») on a live managed-form create surface, not only longer
multi-word labels. When the default subimage-search needle does not pass the confidence threshold,
the localizer SHALL apply a documented fallback (for example scale/threshold tuning per label length,
multiple point sizes, or an OCR fallback) before reporting the label as not located.

#### Scenario: Short owner label is located on the live create form

- **WHEN** `write_form_fields_by_label` targets the «Владелец» label on the demo10413
  `Catalog.ДоговорыКонтрагентов` create form
- **THEN** the label is located and reported `targeted: true`
- **AND** the longer labels «Номер договора» and «Дата договора» on the same form also locate
- **AND** retained evidence references the live screenshot for the run

#### Scenario: Offline short-label needle the prior default would miss

- **WHEN** an offline localization test renders a short single-word needle that the previous
  `max_score=0.2` single-pointsize search would reject
- **THEN** the hardened localizer locates it via its documented fallback
- **AND** the test records the chosen knob (scale, point size or OCR path)

### Requirement: Located reference/short-label writes reach their input field

When a reference/owner or short label is located on a live create form, the write SHALL reach that
field's input so the typed value lands in the intended field. (The residual of a very short label whose
input column is right-aligned to a much longer sibling is resolved by the two-pass input-column
geometry — see "Two-pass geometry clicks short labels into the right-aligned input column".)

#### Scenario: Owner reference value reaches its field on the live create form

- **WHEN** the owner label «Владелец» is written on the demo10413 `Catalog.ДоговорыКонтрагентов`
  create form
- **THEN** the reference value «Корнет ЗАО» lands in the «Владелец» field and is reported
  `selected: true`

### Requirement: Form-write results label their verification honestly

A field write SHALL report its verification level truthfully. Reference fields SHALL report an explicit
`selected` check (the requested value located on screen after input). An open-link field write SHALL
report `committed: true` only when a protocol value-read of the open form confirms the value
(`verification: value_readback`); when the read-back is unavailable it SHALL fall back to
`verification: screen_targeted` (label located + value typed) and SHALL NOT claim `committed`. The
prior false `committed == targeted` (on-screen targeting reported as a commit) SHALL NOT be emitted.

#### Scenario: Reference input reports an explicit selected check

- **WHEN** a reference field value is typed by the open-link writer
- **THEN** the result reports `selected: true` only when the value is located on screen after input
- **AND** reports `selected: false` with a reason otherwise

#### Scenario: Commit is claimed only when the value is read back

- **WHEN** an open-link field is written and the open-form value-read returns the requested value
- **THEN** the result reports `committed: true` with `verification: value_readback`
- **AND** when the value is not read back the result reports `committed: false` (no false positive)

### Requirement: Open-link owner/reference label is resolved from the live form

The open-link write route SHALL resolve a reference/owner field's on-screen label from the live form
(its `read_form_descriptor` descriptor and/or the requested field name), not from a hard-coded
fixture alias. No config-specific owner-label constant (such as «Владелец»→«Контрагент») SHALL remain
baked into the engine.

#### Scenario: demo10413 owner field targeted by its real label

- **WHEN** the open-link route writes the owner field on the demo10413
  `Catalog.ДоговорыКонтрагентов` create form
- **THEN** it targets the «Владелец» label that the live form actually shows
- **AND** it does not look for a «Контрагент» label that is absent on that form

#### Scenario: label is the requested field name, not a baked-in alias

- **WHEN** the open-link route resolves the on-screen label for a reference/owner field
- **THEN** it uses the requested field name (which is the live on-screen label on a create form)
- **AND** the retired vanessa-only «Владелец»→«Контрагент» alias no longer overrides it

#### Scenario: no fixture owner-label constant remains

- **WHEN** the source is inspected after the change
- **THEN** the `Владелец → Контрагент` alias entry no longer hard-codes a single config's label
- **AND** an offline test asserts owner-label resolution for both the demo10413 and vanessa forms

### Requirement: A date value commits on an open-link create form

The open-link date write SHALL commit a `DD.MM.YYYY` value into a managed-form date field on a create
form so that the value reads back from the field, rather than only opening the calendar picker and
leaving the field empty. The date write SHALL drive the field input (masked-input typing or a
deterministic calendar pick) without getting stuck on the calendar button.

#### Scenario: Дата договора reads back committed

- **WHEN** `write_form_date(open_link="e1cib/data/Справочник.ДоговорыКонтрагентов", field="ДатаДоговора",
  date="30.06.2026")` runs on the demo10413 create form
- **THEN** the field reads back the committed date (not an empty mask)
- **AND** the calendar picker is not left open
- **AND** the run retains a screenshot / read-back as evidence

#### Scenario: Date write does not stall on the calendar button

- **WHEN** the date write targets the date field
- **THEN** the value is entered into the field's text input
- **AND** clicking the field's calendar button is not the mechanism that determines the value

### Requirement: The owner-create proof is target-guarded to demo10413

The live owner-create proof SHALL resolve its target infobase and FAIL CLOSED unless that target is
the demo10413 file infobase (`/opt/ai-dev-suite-for-1c/demo10413/1cd`, env
`/opt/ai-dev-suite-for-1c/demo10413/.ai/qa-demo10413.env`). A run resolved against any other infobase
(in particular the stale `.ai1c/vanessa-qa-mcp.env` default → retired `vanessa_client`) SHALL be
rejected, not accepted. The stale default SHALL be fixed or flagged so a proof cannot silently run on
a retired infobase.

#### Scenario: Proof rejected on a non-demo10413 infobase

- **WHEN** the proof is launched with a resolved `target_infobase` that is not demo10413
- **THEN** the proof fails closed with a clear target-mismatch diagnostic
- **AND** no UI create or data assertion is recorded as passing

#### Scenario: Proof runs only on demo10413

- **WHEN** the proof resolves `target_infobase` = demo10413 1cd
- **THEN** it proceeds to the UI create and data assertions
- **AND** the live summary records the demo10413 target and env file

### Requirement: The proof asserts the real object-module behaviour

The proof SHALL create two `ДоговорыКонтрагентов` contracts for one owner from the UI and assert the
real object-module rules read back through the data layer: the auto-built
`Наименование == "Договор " + Формат(ДатаДоговора, "ДЛФ=D") + " №" + НомерДоговора`, the first
contract of the owner `Основной=Истина` and the second `Основной=Ложь`. Literal-equals-written
tautologies SHALL NOT count as the assertion.

#### Scenario: Auto-name and first-owner Основной are verified

- **WHEN** two contracts are created from the UI for one owner («Корнет ЗАО») with «Владелец»,
  «Номер договора» and «Дата договора» set and saved
- **THEN** each record's `Наименование` equals the auto-built value (not the literal Description)
- **AND** the first contract reads back `Основной=Истина` and the second `Основной=Ложь`
- **AND** the proof retains UI screenshot, scenario log and data-assertion evidence

#### Scenario: Cleanup returns the owner contract count to zero

- **WHEN** the proof completes
- **THEN** cleanup removes the created contracts and the owner's contract count returns to 0
- **AND** the demo10413 infobase is restored to its pre-apply baseline with no unresolved leftovers

### Requirement: Two-pass geometry clicks short labels into the right-aligned input column

`write_form_fields_by_label` SHALL derive the input column from the located labels rather than a fixed
per-label offset. It SHALL locate every field label first, record each label's right edge, then click
each non-date field into a SHARED input column computed from the RIGHTMOST located label edge (plus a
configurable gap), so a short label (for example «Владелец» or «Код») reaches the same right-aligned
input column as the longest label instead of under-reaching into a neighbour field. A date-mode field
SHALL keep clicking its own input mask (never the calendar button); when fewer than two labels locate,
the writer SHALL fall back to the legacy label-center + input-offset. Each result item SHALL report the
geometry it used (`input_column`, `date_mask` or `label_offset`).

#### Scenario: Short owner label reaches the right-aligned input column

- **WHEN** `write_form_fields_by_label` writes the short label «Владелец» alongside longer labels on the
  demo10413 `Catalog.ДоговорыКонтрагентов` create form
- **THEN** «Владелец» is clicked into the shared input column (the rightmost located label edge + gap),
  not its own center + a fixed offset
- **AND** the reference value «Корнет ЗАО» lands in the «Владелец» field
- **AND** the item reports `geometry: input_column`

#### Scenario: Offline two-pass shares one column across labels of different length

- **WHEN** an offline test writes two labels whose located right edges differ
- **THEN** both fields are clicked at the same x = max(right edge) + gap
- **AND** both items report `geometry: input_column`

### Requirement: Form-write commit is verified by a protocol value-read of the open form

A form-field write SHALL report `committed: true` only when the requested value is confirmed by a
protocol value-read of the open form, not merely because the label was targeted on screen. After
typing, `write_form_fields_by_label` SHALL value-read the still-open form on a fresh manager connection
(resolving the already-open form by caption/newest, without navigating so the typed-but-unsaved
form-model values are preserved) and set each field's `committed`/`readback_value` from that read-back.
The value SHALL be confirmed against the field's OWN read-back value (mapped from its on-screen label,
which differs from the descriptor field name — e.g. «Номер договора» → `НомерДоговора`), with a
whole-form value-equivalence check only as a fallback when the label does not map to a unique field.
Equivalence SHALL be equality or the read-back value STARTING WITH the requested value (so a date echoed
with a time suffix confirms), and SHALL NOT be a substring-anywhere match, so a failed field's value
cannot borrow an unrelated committed field's value. A field targeted on screen but not confirmed SHALL
be `committed: false`. Verification SHALL be claimed (`verified: true`) only when the read actually
retrieved values (`field_count > 0`); a form that resolves but yields no values is inconclusive
(`verified: false`), not an authoritative non-commit. The open-link writers (`write_form_value` /
`write_form_values`) SHALL derive `committed` from this read-back (`verification: value_readback`), not
from targeting alone. (Caveat: verification is by value presence, so a field whose committed value
equals a form DEFAULT — notably a date defaulting to today — can read back as committed even if
unchanged; write a non-default value to disambiguate.)

#### Scenario: Committed only when the value is read back

- **WHEN** `write_form_fields_by_label` types a value and the open form's value-read returns that value
- **THEN** the item reports `committed: true` with `readback_value` equal to the read-back value
- **AND** `all_committed` is true and the `readback` block reports `verified: true`

#### Scenario: Targeted-but-not-read-back is not reported committed

- **WHEN** a field label is targeted and typed but the value-read of the open form does not return the
  requested value
- **THEN** the item reports `targeted: true` with `committed: false`
- **AND** `all_committed` is false (no false-positive commit)

#### Scenario: A failed field does not borrow a committed field's value

- **WHEN** one field fails to commit but its requested value appears as a substring inside another,
  committed field's read-back value
- **THEN** the failed field is confirmed against its OWN read-back value and reports `committed: false`
- **AND** the substring coincidence does not produce a false-positive commit

#### Scenario: Live honest commit on the demo10413 create form

- **WHEN** the writer types Наименование/owner/date into the demo10413 `Catalog.ДоговорыКонтрагентов`
  create form and value-reads the open form
- **THEN** the fields read back from the form model are reported `committed: true` and the others
  `committed: false`, with retained evidence for the run

#### Scenario: The open-form value-read retries past the cold-client boundary

- **WHEN** the first value-read of the open form on a freshly launched client enumerates the element tree
  but echoes no values (`field_count: 0` with `element_count > 0`)
- **THEN** the read-back retries on a fresh connection until it reads at least one value or a bounded retry
  count is exhausted
- **AND** it reports the values (and `read_attempts`) once the client materialises them, or an honest empty
  read when it never does

### Requirement: OData data-layer tools are deprecated for a test-client-held base

The OData data-layer tools SHALL declare that they cannot verify a test-client-held infobase. The
`assert_data`, `assert_data_count`, `role_data_matrix` tools and the underlying `ODataClient` — a
file/server base opened by a «Клиент тестирования» is exclusively locked, so an out-of-process
OData/COM reader cannot open it. Each tool SHALL carry the deprecation in its description and return an
additive `deprecated: true` with guidance pointing to the same test client's protocol value-read. The
tools SHALL remain functional (valid only against a separately published, non-exclusive endpoint);
removal and the scenario/autofill/regression cleanup are a later change.

#### Scenario: OData tool result is annotated as deprecated

- **WHEN** an OData data-layer tool returns a result
- **THEN** the result additively carries `deprecated: true` and a `deprecation` message that references
  the exclusive test-client lock and points to the protocol value-read
- **AND** the tool's existing `ok`/values are unchanged (additive, non-breaking)

### Requirement: Dynamic-list reads force a refresh and poll until stable
Dynamic-list read primitives (`read_list_grid`, `read_list_row`, `read_list_column`, `search_list`) SHALL, before
reporting row results, force a list refresh and poll the row read until it is stable, so that a reported `0`-row result
denotes a genuinely empty list rather than a stale or not-yet-loaded dynamic list. The refresh SHALL prefer a protocol
replay of the list's «Обновить»/F5 command and MUST fall back to an OS-level `F5` keystroke into the focused list window
when the protocol command is not reachable. Polling SHALL re-read the row count until it is stable (two equal successive
reads) or non-zero, up to a bounded timeout. A shared helper SHALL provide this behavior to all four primitives so the
refresh-and-poll policy is applied uniformly.

#### Scenario: Freshly created record is returned after refresh
- **WHEN** a record is created and committed, then a dynamic-list read is issued for that catalog's list on a freshly
  launched TestClient with refresh enabled
- **THEN** the read forces a list refresh, polls until the row count is stable, and returns the persisted record
- **AND** the read does not report `0 rows` while the record is present in the list

#### Scenario: Genuinely empty list is unambiguous after refresh
- **WHEN** a dynamic-list read is issued against a list that contains no records
- **THEN** after the forced refresh and stable-poll the read reports `0 rows` as an empty result
- **AND** the result does not carry the legacy "EITHER empty OR cold-boundary" ambiguity for the refreshed path

#### Scenario: Read waits for an expected minimum row count
- **WHEN** a dynamic-list read is issued with `wait_for_rows`/`expected_min_rows` set to N
- **THEN** the read blocks until at least N rows are read or the bounded timeout elapses
- **AND** the returned result records whether the expected minimum was met within the timeout

### Requirement: Dynamic-list refresh is on by default and evidence-backed
Dynamic-list read primitives SHALL default to `refresh=True`, and SHALL expose an explicit opt-out for tests that must
assert a row is absent WITHOUT a refresh. The read result SHALL record the refresh action taken (protocol «Обновить»
command replay or `F5` fallback) and the poll outcome (stable row count or timeout) as retained evidence for the read,
so a currency-correct read is observable and auditable rather than implicit.

#### Scenario: Refresh default is applied and recorded
- **WHEN** a dynamic-list read is issued without an explicit `refresh` argument
- **THEN** the primitive applies the refresh-and-poll path and records the refresh method and poll outcome in the result

#### Scenario: Refresh opt-out is honored for absence assertions
- **WHEN** a dynamic-list read is issued with the refresh opt-out set
- **THEN** the primitive reads without forcing a refresh
- **AND** the result marks that no refresh was applied so an absence assertion is not masked by an implicit refresh

### Requirement: `measure_scenario` reports the scenario verdict from scenario status
`measure_scenario` SHALL derive `scenario_ok` from the `ScenarioResult.to_dict()` status returned by
`run_scenario`. The value SHALL be `true` only when the result is a dictionary whose `status` is exactly `"passed"`.
Missing `ok` keys, malformed payloads, failed statuses and errored statuses MUST NOT be treated as truthy pass results.

#### Scenario: Failed measured scenario is not reported as passed
- **WHEN** `measure_scenario` runs a feature and `run_scenario` returns a result dictionary with `status: "failed"`
- **THEN** the `measure_scenario` result contains `scenario_ok: false`
- **AND** the coverage/perf report keys remain present

#### Scenario: Passed measured scenario is reported as passed
- **WHEN** `measure_scenario` runs a feature and `run_scenario` returns a result dictionary with `status: "passed"`
- **THEN** the `measure_scenario` result contains `scenario_ok: true`

#### Scenario: Malformed measured scenario result is fail-closed
- **WHEN** `run_scenario` returns a payload that is not the expected result dictionary
- **THEN** `measure_scenario` does not convert that payload to a truthy pass verdict

### Requirement: JUnit reports use the scenario-level verdict
`junit_xml` SHALL derive each testcase outcome from the scenario-level `status` field, not only from step-level status
scans. A scenario whose status is not `"passed"` MUST emit a JUnit failure or error element even when its step list is
empty or lacks bad step details.

#### Scenario: Failed scenario without bad step details is not green
- **WHEN** `junit_xml` receives a scenario dictionary with `status: "failed"` and no failed step entries
- **THEN** the emitted testcase contains a `<failure>` element
- **AND** the suite failure count includes that testcase

#### Scenario: Errored scenario is emitted as a JUnit error
- **WHEN** `junit_xml` receives a scenario dictionary with an error verdict or error step detail
- **THEN** the emitted testcase contains an `<error>` element
- **AND** the suite error count includes that testcase

### Requirement: JUnit suite counters count each testcase once
`junit_xml` SHALL count each scenario testcase in at most one terminal bucket: passed, failure or error. A scenario that
contains both assertion-failed and error step details MUST NOT increment both `failures` and `errors` for the same
testcase. The suite counters SHALL satisfy `tests == passed + failures + errors + skipped`, with skipped currently zero
unless a skipped scenario status is added later.

#### Scenario: Mixed bad step details count once
- **WHEN** one scenario contains both `assert_failed` and `error` step details
- **THEN** the emitted JUnit suite counts that scenario exactly once
- **AND** the testcase has one terminal child element

#### Scenario: XML escaping remains valid
- **WHEN** scenario names, step names or messages contain Cyrillic text and XML-sensitive characters
- **THEN** the emitted JUnit XML is parseable and preserves the decoded text after XML parsing

### Requirement: Gherkin quoted arguments preserve embedded opposite quotes
The Gherkin transpiler SHALL parse single-quoted and double-quoted step arguments with matching delimiters and MUST
preserve the other quote character inside the captured value.

#### Scenario: Single-quoted input contains a double quote
- **WHEN** a feature step enters the value `'ООО "Ромашка"'`
- **THEN** the transpiled `input_text` step has `new_value == 'ООО "Ромашка"'`
- **AND** the step is not reported as unmapped.

#### Scenario: Double-quoted input contains a single quote
- **WHEN** a feature step enters the value `"owner's value"`
- **THEN** the transpiled step preserves the embedded single quote in the captured value.

### Requirement: Gherkin examples and tables preserve intended rows
The Gherkin parser SHALL expand each `Примеры:` or `Examples:` block from its own header and data rows, and SHALL treat
escaped `\|` sequences inside table cells as literal pipe characters rather than cell separators.

#### Scenario: Multiple examples blocks skip each header
- **WHEN** a scenario outline contains two examples blocks
- **THEN** expansion creates one scenario per data row only
- **AND** no scenario is generated from a repeated header row.

#### Scenario: Escaped pipe remains inside one table cell
- **WHEN** a DataTable row contains `a\|b` inside a cell
- **THEN** the parsed table cell value is `a|b`
- **AND** the value is not split into adjacent cells.

### Requirement: Unsupported Gherkin docstrings are explicit
The Gherkin parser SHALL not silently execute triple-quoted docstring content as ordinary steps. Unsupported docstring
blocks MUST produce an unmapped diagnostic that identifies the unsupported docstring input.

#### Scenario: Triple-quoted docstring is reported unsupported
- **WHEN** a scenario contains a `"""` docstring block
- **THEN** the transpile result includes an unmapped docstring diagnostic
- **AND** the docstring payload lines are not mapped as executable runner steps.

### Requirement: Data-layer match modes fail closed
The OData data assertion comparator SHALL reject unsupported match modes instead of treating them as equality, and SHALL
support numeric comparison for decimal values that differ only by locale decimal separator or insignificant trailing
zeros.

#### Scenario: Unknown match mode raises
- **WHEN** `match_value(actual, expected, mode="__bogus__")` is called
- **THEN** it raises `ValueError` naming the unsupported mode
- **AND** no equality fallback result is returned.

#### Scenario: Numeric mode compares decimal values
- **WHEN** `match_value("120,50", "120.5", mode="numeric")` is called
- **THEN** the comparison succeeds numerically.

### Requirement: Table date-cell input validates before UI interaction
The table date-cell writer SHALL validate a requested `DD.MM.YYYY` value with calendar range checks before activating
the table cell, locating the calendar button or clicking calendar coordinates.

#### Scenario: Invalid date blocks before activation
- **WHEN** `set_table_date_cell` is requested with `date="99.99.2026"`
- **THEN** the result reports `status: "blocked"` and `reason: "invalid_date"`
- **AND** no calendar activation, screenshot localization or mouse click is attempted.

#### Scenario: Valid date still reaches the picker
- **WHEN** `set_table_date_cell` is requested with a valid date such as `05.03.2026`
- **THEN** the validated day, month and year are passed to the calendar picker.

### Requirement: Calendar blocked paths do not open unreachable year dropdowns
The calendar picker SHALL evaluate unsupported backward-year navigation before opening the calendar dropdown, so a
blocked backward-year result does not leave an additional popup open.

#### Scenario: Backward year is blocked before dropdown click
- **WHEN** a table date-cell pick targets a year before the current calendar year
- **THEN** the result is `blocked`
- **AND** no dropdown-opening click is issued for the unsupported year selection.

### Requirement: Synthesized bootstrap random counters fit every generated frame
The synthesized bootstrap generator SHALL choose a default random `counter_base` whose derived counters fit the fixed
counter field for every generated bootstrap frame. The maximum random base MUST be computed from the bootstrap template
counter deltas rather than by assuming that any five-digit base is safe.

#### Scenario: Maximum default base renders all frames
- **WHEN** the default random generator selects the highest allowed base offset
- **THEN** frames 1 through 4 render their counters without raising a fixed-width counter `ValueError`
- **AND** frame 4's sequence is still the selected base plus its template delta.

#### Scenario: Explicit invalid base still fails loudly
- **WHEN** a caller passes an explicit `counter_base` whose derived frame counter exceeds the fixed-width field
- **THEN** bootstrap synthesis raises `ValueError`
- **AND** the invalid explicit value is not silently clamped.

### Requirement: Native write retargeting addresses UTF-16 field leaves

The qa-mcp native write path SHALL retarget write and read-back frames to the requested field leaf when an element path
is encoded as either latin1 or UTF-16LE. A write request for a Cyrillic-named field SHALL NOT send an expected write SET
frame that remains addressed to the captured template field.

#### Scenario: Cyrillic SET frame is retargeted

- **WHEN** a native write frame contains a UTF-16LE `EditField[<base>]` element leaf and the caller requests a Cyrillic
  target field
- **THEN** the emitted frame addresses `EditField[<target>]`
- **AND** the frame no longer addresses the captured base field for that SET operation

#### Scenario: Unexpected retarget miss fails closed

- **WHEN** a write or read-back frame is expected to contain the base field leaf but no latin1 or UTF-16LE leaf is found
- **THEN** qa-mcp reports a structured `retarget_failed` error before sending that frame
- **AND** it does not silently write to the template field

#### Scenario: Focus-change frames may omit the base leaf

- **WHEN** a commit or focus-change frame legitimately addresses a partner field instead of the written base field
- **THEN** qa-mcp may leave that frame unchanged
- **AND** the omission does not mask missing retargeting for the actual write SET frame

### Requirement: Native write committed status is based on normalized target-field read-back

The qa-mcp protocol-layer native write path SHALL report `committed: true` only when the target field's decoded
read-back value equals the normalized requested value, except for explicitly documented type formatting such as a date
read-back suffix. Generic prefix matches SHALL NOT prove a commit.

#### Scenario: Prefix of existing value is not committed

- **WHEN** a native write requests `123` and the target field reads back `123456`
- **THEN** qa-mcp reports `committed: false`
- **AND** it records the observed `readback_value`

#### Scenario: Cyrillic value reads back as committed

- **WHEN** a native write requests a Cyrillic value and the target field's protocol read-back contains the same value
- **THEN** qa-mcp decodes that value from the read-back frame
- **AND** reports `committed: true`

#### Scenario: Edge-length values read back as committed

- **WHEN** a native write requests a one-character value or a value longer than 40 bytes and the target field reads back
  that value
- **THEN** qa-mcp decodes the read-back instead of rejecting it by length
- **AND** reports `committed: true`

#### Scenario: Missing read-back is not a commit

- **WHEN** the target field value cannot be decoded from protocol read-back frames
- **THEN** qa-mcp reports `committed: false`
- **AND** it does not infer success from a prefix, sibling field, or old value

### Requirement: Create-form label locate retry is reachable for production foreground methods

The qa-mcp label-write path SHALL either run its bounded create-form activation retry for foreground methods produced
by the current code, or remove retry metadata that cannot be emitted. A first-screenshot render race on a create form
SHALL NOT be reported as a final label miss before the configured one-shot activation retry is attempted.

#### Scenario: First screenshot miss retries activation

- **WHEN** `write_form_fields_by_label` foregrounds a create form and the first screenshot cannot locate the requested
  label
- **THEN** qa-mcp performs one activation retry through the foreground resource or Ctrl+Tab
- **AND** captures another screenshot before deciding whether the label is missing
- **AND** result metadata names the `activation_retry` path when the retry was used

#### Scenario: Retry remains bounded

- **WHEN** the label is still missing after the retry
- **THEN** qa-mcp returns the normal `"label not located"` result
- **AND** it does not continue retrying indefinitely

#### Scenario: No dead foreground method guard remains

- **WHEN** the label-write source is inspected
- **THEN** retry behavior is keyed to actual foreground methods or the retry branch is absent
- **AND** no unreachable `create_splice`-only guard determines production behavior

### Requirement: Protocol receive uses frame tail markers before idle gaps

The Python manager SHALL read TestClient protocol responses until the protocol
tail marker is observed or a hard monotonic deadline expires, using idle timing
only as a fallback for responses without the known tail marker.

#### Scenario: Tail marker arrives after an idle gap

- **WHEN** a TestClient response is delivered in two socket chunks separated by
  more than the receive idle window and the second chunk contains the protocol
  tail marker
- **THEN** the receive layer returns one complete response buffer containing
  both chunks
- **AND** downstream value parsing can extract the response value from that
  buffer

#### Scenario: No tail marker is observed

- **WHEN** response bytes are received but the known tail marker is not present
  before the idle fallback or hard deadline
- **THEN** the receive layer returns the bytes collected so far without waiting
  indefinitely
- **AND** the deadline calculation uses monotonic time rather than wall-clock
  timestamps

### Requirement: Protocol receive implementation is shared

The Python manager SHALL use one shared receive implementation for the native
read session and native mutation session so frame-boundary semantics and timeout
handling stay consistent across read and mutation-facing protocol code.

#### Scenario: Existing receive callers drain responses

- **WHEN** `session.read_available` and `native_mutation._read_available` drain a
  protocol response
- **THEN** both call the same frame-aware helper
- **AND** neither implementation carries separate wall-clock idle-loop logic

### Requirement: Response parsers tolerate truncated envelopes

The Python manager SHALL treat truncated response envelopes as partial data
instead of raising parser exceptions from out-of-bounds byte indexing.

#### Scenario: Truncated value envelope is scanned

- **WHEN** a response blob ends at or immediately after a value marker without
  enough bytes for the expected value envelope
- **THEN** form-field extraction returns a partial result or `None` for the
  affected value
- **AND** no `IndexError` escapes the parser

#### Scenario: Truncated window caption envelope is scanned

- **WHEN** a response blob ends at or immediately after a window caption marker
- **THEN** window extraction returns a partial result or omits that caption
- **AND** no `IndexError` escapes the parser

### Requirement: Response parsers reject unsupported field-name encodings safely

The Python manager SHALL handle non-Latin field-name scans as unsupported
scanner input and return no value rather than raising a Unicode encoding error.

#### Scenario: Cyrillic field name is scanned

- **WHEN** a parser helper receives a Cyrillic field name for a scanner path that
  is limited to Latin-1 byte search
- **THEN** the helper returns `None`
- **AND** no `UnicodeEncodeError` escapes the parser

### Requirement: List-grid reads do not stop on adjacent duplicate rows

The Python manager SHALL preserve adjacent duplicate list-grid rows and SHALL
surface timeout or empty-row stops explicitly when a list-grid sweep ends early.

#### Scenario: Adjacent duplicate rows are read

- **WHEN** a list-grid contains two adjacent rows whose requested column values
  are equal
- **THEN** `read_list_grid` returns both rows
- **AND** the sweep does not treat equality with the previous row as end of list

#### Scenario: Row read times out

- **WHEN** a row read times out before the requested values can be confirmed
- **THEN** the list-grid result includes explicit truncation or stop-reason
  metadata
- **AND** callers can distinguish timeout truncation from a genuine empty row

### Requirement: Native write sessions clean up sockets on setup failure

The Python manager SHALL close sockets created during native write-session
startup if setup replay fails before the context manager is entered.

#### Scenario: Setup replay raises during enter

- **WHEN** `NativeWriteSession.__enter__` creates a socket and setup replay then
  raises an exception
- **THEN** the created socket is closed before the exception is re-raised
- **AND** the failed session does not leave an open socket handle behind

### Requirement: Native sends use a send-appropriate timeout and reason

The Python manager SHALL avoid sending outbound protocol frames under the short
receive-idle timeout and SHALL report send timeouts distinctly from protocol
response divergence.

#### Scenario: Outbound send is slow

- **WHEN** sending a multi-frame or multi-kilobyte protocol request exceeds the
  send timeout
- **THEN** the operation returns or raises a distinct send-timeout reason
- **AND** the failure is not reported as protocol divergence from the TestClient
  response

#### Scenario: Receive timeout follows send timeout setup

- **WHEN** a request is sent and the manager begins draining the response
- **THEN** receive draining uses the configured receive timeout behavior
- **AND** the send timeout does not permanently replace the receive timeout

### Requirement: TestClient teardown refuses unowned process groups

The Python manager SHALL refuse to terminate a process group for a pid that is
not recorded or recognizable as a qa-mcp-owned TestClient runtime process.

#### Scenario: Pid is not an owned TestClient process

- **WHEN** `stop_test_client(pid)` is called with a stale, recycled, or unrelated
  pid whose process identity is not an expected TestClient runtime component
- **THEN** teardown returns a structured refusal
- **AND** no process group kill is attempted for that pid

### Requirement: Native write replay operations use a shared replay session

The Python manager SHALL execute native write, list, dialog and window replay
operations through one shared replay-session engine for socket setup, setup
frame replay, operation frame replay, response observation and cleanup. The
shared engine MUST preserve each operation's existing public arguments, result
shape and verdict semantics.

#### Scenario: Replay operation uses the shared receive point

- **WHEN** a native replay operation drains TestClient protocol responses
- **THEN** the replay engine calls `read_protocol_available`
- **AND** no converted operation carries its own idle-gap receive loop

#### Scenario: Retarget failures keep structured verdicts

- **WHEN** a converted write operation cannot retarget a frame that must contain
  the requested field leaf
- **THEN** the operation returns the existing structured `retarget_failed`
  verdict
- **AND** the shared replay engine does not mask the retarget failure as a
  generic replay divergence

#### Scenario: Operation-specific commit verdict is preserved

- **WHEN** a converted write operation reads back the target field value
- **THEN** its verdict callback applies the same normalized equality rules used
  before the refactor
- **AND** generic prefix matches do not prove a commit unless the documented
  date/reference formatting exception applies

#### Scenario: Send timeout remains distinct from response divergence

- **WHEN** sending a converted replay frame exceeds the send timeout
- **THEN** the result or raised error preserves the existing send-timeout reason
- **AND** the receive timeout is restored for subsequent response draining

### Requirement: MCP server delegates protocol wire work to protocol modules

The MCP server SHALL keep raw TestClient socket access, frame rebinding,
foreground protocol flows and read-sweep wire mechanics in protocol-owned
modules rather than in `mcp_server.py`. The extraction MUST preserve observable
tool behavior.

#### Scenario: MCP server has no raw protocol socket dependency

- **WHEN** the source tree is inspected after extraction
- **THEN** `src/qa_mcp/mcp_server.py` contains no direct
  `socket.create_connection` usage
- **AND** it does not import `GuidRebinder` directly

#### Scenario: Foreground protocol behavior is preserved

- **WHEN** a tool opens or foregrounds a form through an extracted protocol
  helper
- **THEN** the same endpoint, capture bootstrap and activation retry behavior is
  used as before extraction
- **AND** result metadata still records activation retry when that path is used

#### Scenario: Read-sweep helpers remain protocol evidence preserving

- **WHEN** extracted descriptor, field, table-cell or window-list reads process
  TestClient responses
- **THEN** they keep the same response parsing and partial/truncated envelope
  behavior
- **AND** no new protocol claim is accepted without existing tests or retained
  evidence

### Requirement: Platform version selection is provided by a leaf module

The Python manager SHALL expose active platform-family selection and live
platform version detection from a cycle-free `qa_mcp.versioning` module that
protocol code can import at module load time. Existing regression imports MUST
remain compatible.

#### Scenario: Protocol modules import versioning without lazy cycle workaround

- **WHEN** protocol modules select bundled protocol assets
- **THEN** they import version helpers from `qa_mcp.versioning` at top level
- **AND** they do not carry lazy import comments whose only purpose is avoiding
  a `regression.versioning` cycle

#### Scenario: Regression versioning remains compatible

- **WHEN** existing callers import `active_version_key` from
  `qa_mcp.regression.versioning`
- **THEN** the import still succeeds
- **AND** it returns the same platform-family key as the leaf module

#### Scenario: Existing version policy is preserved

- **WHEN** `QA_MCP_PLATFORM_VERSION` is unset, a bare supported family, a full
  supported platform version or an unsupported value
- **THEN** version selection returns or rejects values exactly as it did before
  the move

### Requirement: Protocol cleanup removes only verified dead helpers

The Python manager SHALL remove dead protocol helpers only when current source
references and tests prove they are not on a live path. Helpers that remain live
MUST be preserved even if they appeared in an earlier review's dead-code list.

#### Scenario: Verified dead MCP helpers are absent

- **WHEN** cleanup is complete
- **THEN** source search finds no `_RESOLVE_SF_RE`, `_CreateForegroundHold` or
  `_OPEN_LINK_LABEL_ALIASES`
- **AND** the offline test suite still passes

#### Scenario: Live splice activation helper is preserved

- **WHEN** cleanup is complete
- **THEN** `_splice_window_activate_command` remains available to the label
  locate retry path
- **AND** the retry path tests or source checks prove it is still referenced

#### Scenario: Mutation helper module is removed only if no live path imports it

- **WHEN** `mutation.py` is considered for removal
- **THEN** source analysis proves `native_mutation` no longer imports it on a
  live path or the import has been replaced safely
- **AND** otherwise the module remains and the residual reason is recorded

### Requirement: Duplicate protocol utilities collapse only with equivalent behavior

The Python manager SHALL collapse duplicate protocol utilities only when the
replacement preserves behavior for existing callers and is covered by focused
tests or source checks.

#### Scenario: Duplicate helper is replaced by shared implementation

- **WHEN** a duplicate helper such as date normalization, GUID substitution,
  capture chunk loading or LEB128 decoding is removed
- **THEN** all former call sites use the shared implementation
- **AND** focused tests cover the previous behavior

### Requirement: Supported 8.5 capture lookup uses validated 8.3 protocol data

The Python protocol runtime SHALL resolve capture-backed operation data for the
supported `8.5` family through the validated `8.3` bundled capture set until an
8.5-specific bundle is populated. The active platform version MUST remain the
live 8.5 version for synthesized frames, full captured-replay frames and
diagnostics; only capture-data path selection falls back.

#### Scenario: 8.5 capture-backed read resolves to bundled 8.3 data

- **WHEN** `QA_MCP_PLATFORM_VERSION` or an explicit resolver argument selects
  platform family `8.5`
- **THEN** `resolve_capture_dir("nextrow")` resolves to the bundled `8.3`
  capture directory when no `8.5` capture exists
- **AND** the result is not reported as `capture-not-found` for the supported
  fallback case

#### Scenario: 8.5 full replay declares the live platform version

- **WHEN** a capture-backed full replay uses the validated 8.3 protocol-data
  fallback while `QA_MCP_PLATFORM_VERSION=8.5.1.1343`
- **THEN** the replay sends frames stamped with `8.5.1.1343`
- **AND** it does not declare the captured 8.3 platform version to the live 8.5
  TestClient session

#### Scenario: Direct 8.3 lookup remains unchanged

- **WHEN** platform family `8.3` is active
- **THEN** capture-backed operation lookup resolves to bundled `8.3` data
- **AND** no fallback warning or unsupported-family behavior is involved

#### Scenario: Undeclared platform family still fails closed

- **WHEN** platform family `9.0` or another undeclared family is selected
- **THEN** active version resolution rejects it before capture lookup
- **AND** the error names supported families and the capture refresh runbook

### Requirement: Protocol captures carry platform and configuration metadata

Curated protocol captures and manager-frame template sets SHALL expose a
sanitized metadata record that includes the captured platform build and
configuration identity when known. The metadata MUST NOT contain raw TCP
payloads, credentials, screenshots, infobase dumps, or customer data.

#### Scenario: Capture metadata is loaded

- **WHEN** qa-mcp loads metadata for a curated capture or template set
- **THEN** the metadata includes a schema id, capture id, platform build,
  configuration label fields, source/template paths, and notes
- **AND** the metadata can be serialized as reviewed text without exposing raw
  capture payloads or secrets

#### Scenario: Missing configuration metadata is explicit

- **WHEN** a legacy capture has no configuration tag
- **THEN** the selection metadata marks the configuration as unknown
- **AND** callers can report that no config-matched proof exists before relying
  on the capture for a real customer configuration

### Requirement: List-read capture selection prefers config-matched captures

The protocol runtime SHALL select list-read captures by requested platform build
and configuration metadata when those tags are supplied. If no exact
configuration match exists, the runtime MUST return an observable fallback
selection reason instead of silently treating a generic bundled capture as
config-matched proof.

#### Scenario: Exact config match is selected

- **WHEN** a list-read operation requests platform `8.3.27.2130` and
  configuration `Бухгалтерия 3.0`
- **AND** a capture metadata record matches both tags
- **THEN** the selector returns that capture
- **AND** the selection result records `match: "exact"`

#### Scenario: Generic fallback is visible

- **WHEN** no capture metadata record matches the requested configuration
- **THEN** the selector MAY fall back to the existing active bundled capture
- **AND** the selection result records that the capture is not config-matched
- **AND** the result names the requested platform/configuration tags that remain
  unproven

### Requirement: Manager-handshake drift is detected before list reads are trusted

Before using a selected capture for a live list-read contour, qa-mcp SHALL be
able to run a bounded manager-handshake preflight that verifies the client
ACK/GUID response after the captured or synthesized session-bootstrap frames.
If the ACK/GUID marker is absent or undecodable, the preflight MUST fail loudly
with a specific manager-handshake drift diagnostic.

#### Scenario: ACK GUID is observed

- **WHEN** the preflight sends manager frame 3 and the live client response
  contains the expected ACK/GUID marker
- **THEN** the preflight returns `ok: true`
- **AND** it records the observed ACK GUID, frame index, and selected capture
  metadata

#### Scenario: Manager handshake moved

- **WHEN** the preflight sends manager frame 3 and the response lacks the
  expected ACK/GUID marker
- **THEN** the preflight returns `ok: false`
- **AND** the error is `manager-handshake-moved`
- **AND** the diagnostic names the selected capture, requested platform/config
  tags, frame index, and refresh-capture action hint

#### Scenario: Handshake drift diagnostic is propagated

- **WHEN** a descriptor or list-read setup fails because the preflight reports
  `manager-handshake-moved`
- **THEN** the tool result reports the drift diagnostic as the specific cause
- **AND** it does not claim the list is empty or config-matched

### Requirement: Capture refresh procedure is reproducible and raw-data safe

The protocol lab SHALL provide a documented procedure and command-line helper
for re-recording the irreducible session bootstrap plus list-open/read templates
on a target platform/configuration. The procedure MUST retain only sanitized
metadata and bounded evidence in reviewed changes while keeping raw pcaps,
traffic logs, screenshots, platform logs, and infobase data in ignored runtime
paths.

#### Scenario: Refresh metadata is prepared

- **WHEN** an operator prepares a refresh for a target platform/configuration
- **THEN** the helper writes a sanitized metadata sidecar naming the target
  platform build, configuration label, capture id, raw runtime roots, and
  template output paths
- **AND** reviewed git changes contain only the sidecar/runbook/tool updates,
  not the raw capture streams

#### Scenario: Runtime proof is unavailable

- **WHEN** the target Windows [redacted third-party configuration] host is unavailable during delivery
- **THEN** the delivery records a qa-mcp provider gap for the positive-read proof
- **AND** no artifact claims that `read_list_grid` returned visible
  `Справочник.Валюты` rows on that host

### Requirement: Lifecycle-bound Windows display proof is retained safely

The protocol lab SHALL verify the remote lifecycle-window target contract through focused Python and Go tests plus Windows-native host-agent evidence. The proof SHALL cover an empty-title TestClient target, implicit lifecycle/client targeting for screenshot, key, text, click, and visible-list-cell routes, explicit-selector precedence, unrelated-foreground refusal, typed desktop-session diagnostics, and cleanup. Reviewed/card evidence MUST retain only sanitized booleans, reason codes, capability/version facts, and test outcomes; raw screenshots, HWNDs, PIDs, titles, credentials, host-agent logs, and infobase contents MUST remain ignored and uncommitted.

#### Scenario: Empty-title target and unrelated foreground are distinguished

- **WHEN** the Windows proof runs with an owned or attached TestClient target whose caption is empty and another application is foreground
- **THEN** lifecycle-bound screenshot and safe key delivery report the TestClient target as selected
- **AND** the retained summary records only target-matched and unrelated-foreground-untouched booleans.

#### Scenario: Display primitive matrix is evidenced

- **WHEN** the lifecycle-window verification bundle is completed
- **THEN** it records outcomes for `capture_screenshot`, `send_keys`, `type_text`, `click`, and visible-list-cell reads
- **AND** each row names its command/test route and passed, blocked, or not-applicable outcome.

#### Scenario: Session failures remain typed and bounded

- **WHEN** locked, disconnected, and non-interactive states are exercised through native tests or an accepted typed-probe fallback
- **THEN** the evidence records a distinct expected/observed reason-code match for each state
- **AND** contains no raw desktop or host-agent payload.

#### Scenario: Runtime artifacts stay ignored

- **WHEN** Windows verification produces screenshots, binaries, temporary payloads, or logs
- **THEN** those artifacts remain under ignored `.runtime/` paths and cleanup is audited
- **AND** only sanitized command outcomes are summarized in the card and delivery manifest.

### Requirement: Project target profiles configure every qa-mcp runtime layer

The protocol lab SHALL use the project target profile for runtime settings and
synthesized manager bootstrap version selection while preserving explicit
process-environment overrides.

#### Scenario: Project profile supplies qa-mcp runtime settings

- **WHEN** the MCP process has `QA_MCP_TARGET_ENV_FILE` pointing at a readable
  UTF-8 target profile
- **THEN** qa-mcp settings such as OData, platform, host and port are loaded
  from that profile
- **AND** synthesized manager bootstrap frames declare the target platform
  version from that profile
- **AND** an explicitly supplied process environment value takes precedence.

### Requirement: Doctor bearer defaults follow the active transport

The qa-mcp doctor SHALL select its default proxy bearer requirement from the
active MCP transport while retaining an explicit caller override.

#### Scenario: Doctor defaults follow the active transport

- **WHEN** `qa_mcp_doctor` is called without an explicit bearer requirement
- **THEN** stdio skips the bearer check and HTTP transport requires it.

### Requirement: Descriptor runtime failures are explicit and actionable

Descriptor tools SHALL distinguish manager protocol drift and a persistently
empty cold form from invalid caller arguments or ambiguous success.

#### Scenario: Descriptor encounters manager ACK drift

- **WHEN** a descriptor protocol call cannot find the client ACK GUID after
  manager frame 3
- **THEN** the tool returns `manager-handshake-moved` with a bounded action hint
- **AND** it does not classify the runtime failure as `invalid-arguments`.

#### Scenario: Heavy configuration returns an empty first descriptor

- **WHEN** `read_form_descriptor(open_link=...)` receives no opened form,
  fields or elements from a cold client
- **THEN** navigation polls for its SecondaryFrame and ManagedForm using the
  configured bounded warmup attempts and delay inside the same manager session
- **AND** a persistent empty result returns `descriptor-empty` instead of an
  ambiguous success payload.
