## ADDED Requirements

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
