# qa-mcp-positive-operation-boundary-public-integration Specification

## Purpose
Define the pure bound-operation route, evidence-scope and positive-result
integration shared by the real qa-mcp FastMCP and ScenarioRunner public paths.

## Requirements
### Requirement: Bound positive operations use pure route admission
The shared public entrypoint SHALL route a bound schema-declared operation only
after exact application target, session, attachment, binding generation and
supplied endpoint/display values match. Malformed, foreign or asymmetric state
MUST return a fixed blocked result before Local or Windows adapter invocation.
Declared unbound and non-schema compatibility SHALL remain unchanged, and R8
SHALL add no lifecycle authority.

#### Scenario: Invalid route state has no adapter side effect
- **WHEN** each target, session, attachment, generation, host, port or display component is missing, malformed, foreign or asymmetric
- **THEN** the public result is blocked with trusted binding provenance and zero Local and Windows calls
- **AND** exact current-bound controls execute once while declared unbound and pre-session lifecycle compatibility are not widened or removed

### Requirement: Evidence scope is operation-local and ordered
The application SHALL admit route and provenance before opening one current
ledger scope, invoke the selected adapter at most once inside it, normalize the
result at most once and close the scope in `finally`. Serialization, fallback
and executor data MUST NOT open another scope, retry an adapter or change route
or disclosure authority.

#### Scenario: Every result and exception closes its own scope
- **WHEN** concurrent operations return success, blocked, ambiguous or failure, or an adapter/result edge raises
- **THEN** each admitted operation closes only its own evidence scope and returns a total typed result
- **AND** stale, foreign or executor-created receipts cannot disclose a path or affect another operation

Real default local and Windows-host screenshot handlers SHALL register only their
validated current production. Shared execution SHALL consume current records,
never register raw executor paths. This SHALL hold through registered MCP and
shared scenario entrypoints without schema bypass or custom positive executors.

#### Scenario: Actual default screenshot factories
- **WHEN** actual default factories capture using substituted external backends under sanitized and full_local policy
- **THEN** actual current bytes determine the artifact digest and scope, sanitized exposes no raw path/image, and full_local returns the exact readable own path
- **AND** deliberately unbound standalone/direct screenshots retain their useful legacy evidence

#### Scenario: Overlapping same-ledger and opposite-policy operations
- **WHEN** same-ledger operations produce identical bytes and IDs at distinct paths, or separate applications overlap under both opposite policy combinations
- **THEN** each outcome maps to its own production and each success/failure closes only its own records
- **AND** immediate foreign file/record snapshots remain identical while the sibling operation is still paused
- **AND** the scope carrier is restored after success/failure, including in the original registered callback context

### Requirement: Real MCP and ScenarioRunner share provenance and taxonomy
FastMCP and ScenarioRunner SHALL use the same shared entrypoint for the same
admitted bound request and executor outcome,
trusted provenance and `success`/`blocked`/`ambiguous`/`failure` taxonomy.
Executor provenance, request replacement and serialization callbacks MUST NOT
replace trusted public identity.

#### Scenario: Four verdicts are identical across public paths
- **WHEN** Local and Windows adapters return each verdict for the same admitted request through real FastMCP and ScenarioRunner
- **THEN** both public paths carry identical operation, target, session, binding, fingerprint, generation and evidence-policy provenance
- **AND** executor-controlled provenance or exceptional fields produce the same bounded typed failure without input fragments

### Requirement: Declared positive outcomes are identical through both paths
Both public paths SHALL omit undeclared keys without inspection and SHALL
return the complete fixed `invalid-executor-result` for every declared class,
type, subclass or domain mismatch defined by R7. Every emitted result MUST stay
within R7's structural, scalar, node and 65,536-byte envelope.

#### Scenario: Public mismatch and bound matrices are complete
- **WHEN** the finite class catalog, artifact order, depth/item/node/string and final-byte below/exact/above controls execute through both paths
- **THEN** exact valid cells preserve or canonicalize, undeclared keys omit without access and every declared mismatch has the same complete fixed outcome
- **AND** all results serialize without escaping an exception or exceeding the envelope

### Requirement: Multi-session active-window assertions precede public projection
For bound `read_active_window` steps, `ScenarioRunner.run` MUST evaluate the
requested expected-window predicate at the trusted internal read seam before
public projection, then use its admitted boolean for `StepResult` assertion/status.
It MUST preserve the shared operation's route admission, selected executor,
provenance and non-success verdict behavior without retry or native fallback.

#### Scenario: Real default handler supports matching and mismatching assertions
- **WHEN** an admitted local or Windows-host default handler returns actual `ActiveWindowContext` through the shared MCP operation or `ScenarioRunner.run`
- **THEN** the safe observation agrees across those paths
- **AND** a requested actual window match passes while mismatch/missing/ambiguous fails, using one native read and no echoed raw window data.

#### Scenario: Bound assertion serialization remains private
- **WHEN** the trusted read or expected predicate contains private strings or the read fails
- **THEN** serialized operation and `StepResult` preview/error fields omit raw UI, reference, expected-string, credential and physical-path fragments
- **AND** successful matching does not require searching the normalized public preview.

#### Scenario: Declared compatibility remains deliberate
- **WHEN** an intentionally unbound direct or multi-session read uses its established contract
- **THEN** its useful legacy DTO/assertion behavior remains available
- **AND** this change does not claim default single-session BDD delivery or widen live authority.

### Requirement: Both public paths execute the exact URL matrix
FastMCP and ScenarioRunner SHALL each execute
`5 × (3 hostile + 1 control) = 20` documentation URL cells, for an exact total
of 40 public-path cells. At depths 1–4 credential assignment, `user@` and
`user:pass@` hostiles MUST reject without the original or any decoded fragment,
and the paired benign control MUST emit the exact canonical URL. At depth 5 all
four non-fixed inputs MUST reject without fragments.

#### Scenario: Forty URL cells have one oracle
- **WHEN** all four cells at encoding depths 1 through 5 execute through each real public path
- **THEN** every hostile and every depth-5 input yields complete fixed `invalid-executor-result` with no original or decoded fragment
- **AND** each depth-1 through depth-4 control yields the exact same canonical documentation URL through both paths

### Requirement: R8 remains bounded and offline
R8 SHALL add at most 300 production lines, consume only A5's exact published
authorization, and add no lifecycle, protocol, authority or wire behavior.
Delivery SHALL retain test-first Linux evidence and exact-source Windows
offline integration evidence with owned cleanup.

#### Scenario: Delivery reaches review
- **WHEN** R8 is ready for independent review
- **THEN** focused and full non-live coverage, compilation, strict OpenSpec, LOC, scope and whitespace gates pass
- **AND** Windows evidence identifies the exact source, offline matrix and post-run cleanup without claiming live 1C or protocol proof
