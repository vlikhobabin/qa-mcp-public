# qa-mcp-hidden-direct-execute-main-window-investigation Specification

## Purpose

Define the privacy-safe exact-source investigation and exclusive continuation
decision required when hidden direct-execute certification cannot establish a
stable main-window and marker observation boundary.

## Requirements

### Requirement: Investigation preserves published and blocked production bytes
The investigation SHALL add no production caller or public authority and MUST
keep published S1-R1 through S6 plus blocked S7 production files byte-identical
through every diagnostic and decision step.

#### Scenario: Investigation scope is checked
- **WHEN** the diagnostic candidate is compared with the published S6 and
  blocked S7 manifests
- **THEN** only declared test-only, documentation and ignored evidence paths
  differ
- **AND** any predecessor or S7 production drift blocks the investigation.

### Requirement: Exact S3 and S4 timelines distinguish the causal boundary
The investigation SHALL compare exact authorized S3 and S4 runs using the same
platform, target, principal and lifecycle foundation and SHALL observe bounded
process/job/desktop/window stages through terminal exit or main-window
admission.

#### Scenario: S4 main window remains absent
- **WHEN** the tracked EPF does not produce the admitted S4 main identity within
  the bounded observation window
- **THEN** evidence distinguishes child liveness/exit, listener state, desktop
  identity, top-level structural inventory and any startup/prompt boundary
- **AND** a transient enumeration error or retry never becomes success.

#### Scenario: S3 control is compared
- **WHEN** the real S3 TestClient control and S4 `/Execute` diagnostic complete
- **THEN** their exact argv/environment identities and bounded stage timelines
  are compared
- **AND** unrelated target substitution or visible-session success cannot
  satisfy the hidden comparison.

### Requirement: Diagnostic evidence is privacy-safe and repeatable
Every retained diagnostic receipt MUST contain only hashes, bounded counts,
booleans, allowlisted structural classes, process/exit stages and monotonic
offsets, and MUST exclude credentials, raw paths, captions, UI text,
screenshots and protocol payloads.

#### Scenario: Root-cause classification is repeated
- **WHEN** two fresh S4 diagnostics and one uninstrumented confirmation run
- **THEN** they support the same causal boundary or the result remains
  `NOT-VERIFIABLE`
- **AND** raw runtime output remains ignored and outside portable evidence.

### Requirement: Decision controls the only continuation path
The investigation MUST publish exactly one evidence-backed decision: an
evidence/runbook correction that preserves published bytes, a bounded linked
replacement/authorization scope, or `NOT-VERIFIABLE` with an exact resume
condition.

#### Scenario: Decision requires production or predecessor change
- **WHEN** the causal fix would change S7 production scope or a certified S1-S6
  file
- **THEN** S7 remains blocked
- **AND** the decision names a separate bounded successor and fresh review gate
  rather than patching the current card.

### Requirement: Every diagnostic cleans only exact-owned runtime state
Each live run SHALL remove its current task, stage, PID/job/desktop/TPort state
and restore the exact pre-run configuration while preserving unrelated
protected tasks, listeners, Docker and boot identity.

#### Scenario: Diagnostic terminates or fails
- **WHEN** a diagnostic passes, times out or fails at any observation stage
- **THEN** exact-owned cleanup is attempted and inventoried
- **AND** incomplete cleanup blocks archive and review.
