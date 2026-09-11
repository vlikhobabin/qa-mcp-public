## MODIFIED Requirements

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
