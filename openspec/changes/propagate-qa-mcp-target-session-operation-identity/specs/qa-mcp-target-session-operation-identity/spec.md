## ADDED Requirements

### Requirement: Common execution enforces target and session equality
The shared MCP/scenario operation boundary MUST compare application target,
session target, attachment identity, generation and supplied routing fields
before invoking a concrete executor.

#### Scenario: Current identity matches
- **WHEN** target, session, attachment and generation agree
- **THEN** the selected local or Windows executor receives the operation.

#### Scenario: Identity is stale or foreign
- **WHEN** any target, session, generation, endpoint or display identity differs
- **THEN** execution returns a typed blocked result
- **AND** the concrete executor is not called.

### Requirement: Every verdict carries bounded provenance
Project-bound success, blocked, ambiguous and failure results SHALL carry the
application target and current session, and artifact references SHALL also
carry operation, binding and evidence-policy provenance.

#### Scenario: Executor returns any verdict class
- **WHEN** a project-bound MCP or scenario operation completes
- **THEN** its serialized result contains the same target/session identity
  without credentials or physical connection values.

### Requirement: Artifact paths follow evidence policy
Artifact serialization MUST remove physical paths for `sanitized` policy and
MUST retain them only for explicitly approved `full_local` policy.

#### Scenario: Sanitized artifact is returned
- **WHEN** an executor returns an artifact with a local path
- **THEN** reviewed serialization retains its id/hash/provenance but omits the
  path.

### Requirement: Downstream executors remain compatible
The identity gate SHALL preserve the public `QAExecutor` request/target/session
contract used by downstream fake executors.

#### Scenario: Fake executor contract is exercised
- **WHEN** a downstream executor returns its existing `OperationResult`
- **THEN** common routing stamps provenance without requiring provider imports.
