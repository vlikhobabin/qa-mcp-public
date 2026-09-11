## ADDED Requirements

### Requirement: Private fenced samples bind one inventory to exact liveness
The host-agent SHALL keep a private fenced sample that evaluates exact child
and listener process state, exact job membership and exact response-TPort
ownership before and after exactly one inventory call. The sample SHALL refuse
unknown, exited or changed liveness and SHALL expose only closed private status
values.

#### Scenario: Stable live sample admits one inventory
- **WHEN** child and listener are live, both are exact job members, the listener owns the exact response TPort and the pre/post snapshots match
- **THEN** the fenced sample invokes inventory exactly once and returns its bounded successful result

#### Scenario: Hostile liveness refuses without retry
- **WHEN** either process is exited or unknown, job membership is false, TPort ownership is false, handle close fails or the post snapshot changes
- **THEN** the fenced sample refuses with a closed status and performs no retry, fallback or action

### Requirement: Both worker inventory boundaries use the connected fence
The host-agent SHALL replace exactly the two direct inventory calls inside
`observeHiddenDirectInWorker` with the private Windows fenced wrapper. No
direct inventory bypass SHALL remain in that function and its fail-closed,
polling, passive-UIA and admission outcomes SHALL remain unchanged.

#### Scenario: First and second boundaries execute the fence
- **WHEN** the worker reaches its first and second inventory boundaries
- **THEN** each boundary executes one wrapper and one inventory call with exact pre/post fence counts

#### Scenario: Inventory and main-window outcomes remain bounded
- **WHEN** inventory errors, is empty or non-empty, or the expected main is absent, exact or changes before readmission
- **THEN** existing worker refusal/admission and zero-action behavior remains unchanged apart from retaining the private bounded diagnostic

### Requirement: Pre-receipt diagnostic ownership is bounded and private
The host-agent SHALL retain one private pre-receipt diagnostic with a fixed
schema and allowlisted stage, status and failure values. Validation SHALL
reject malformed or contradictory diagnostics and serialization SHALL exclude
raw errors, endpoints, desktops, handles, PIDs, ports, UI values and other
dynamic identities.

#### Scenario: Boundary failure retains a safe diagnostic
- **WHEN** either fenced inventory boundary refuses before an observation receipt exists
- **THEN** the private diagnostic records only the allowlisted boundary and closed failure status

#### Scenario: Malformed or hostile content is rejected
- **WHEN** a diagnostic has an unknown schema/token, contradictory success/failure state or hostile dynamic text
- **THEN** validation refuses it and no hostile content is retained or serialized

### Requirement: Transferred observer preserves exact job and TPort ownership
The host-agent SHALL validate the transferred observer against the exact
request/response acknowledgement and invoke one private callback while the
worker-local job handle remains held. The callback SHALL neither transfer nor
close ownership and SHALL not expand process/job/TPort authority.

#### Scenario: Acknowledged observer runs while ownership is held
- **WHEN** the worker has published and acknowledged the exact lifecycle response
- **THEN** the callback observes the exact response job and TPort while the local job handle and listener remain live, then normal cleanup resumes

#### Scenario: Invalid transferred observer refuses
- **WHEN** request/response identity, worker, child, listener, job or TPort ownership is missing or inconsistent
- **THEN** validation refuses before the callback can run

### Requirement: Publication evidence proves bounded offline composition
The delivery SHALL retain clean-HEAD RED and same-tree GREEN evidence for the
four seam families and exact two call sites. GREEN SHALL bind the exact
seven-path staged tree, the I5 source/LOC ceilings and the offline hostile and
cross-build floor without launching Windows or 1C.

#### Scenario: Exact staged tree passes publication gates
- **WHEN** only the seven owned Go paths plus card-owned OpenSpec/spec/evidence paths are explicitly staged and every Go hunk maps to an authorized predicate
- **THEN** focused/full Go test and vet, Linux tests, Windows amd64/386 test cross-builds, strict OpenSpec, staged-tree compile, scope, diff and whitespace checks all pass

#### Scenario: Scope or hostile gate fails closed
- **WHEN** an extra path, unowned hunk, line ceiling breach, direct bypass, missing diagnostic connection, compile failure or hostile failure is detected
- **THEN** delivery stops before review or publication
