# qa-mcp Runtime Target Adapter

## Purpose

Define the provider-owned, secret-safe resolution of a frozen project target
handoff against one ignored local qa-mcp profile, without runtime side effects.

## Requirements

### Requirement: Complete handoff resolves one exact target
qa-mcp SHALL reconcile the complete frozen project handoff with exactly one
ignored provider profile before returning a runtime-target resolution.

#### Scenario: File target matches
- **WHEN** target id, file kind, fingerprint, principal, receipt, binding
  reference and positive generation match
- **THEN** resolution returns one immutable target binding.

#### Scenario: Client-server target matches
- **WHEN** the same closed fields match for a client-server target
- **THEN** resolution preserves that declared kind without selecting a fallback.

### Requirement: Partial or mismatched handoff fails closed
Any incomplete, malformed, stale or mismatched configured handoff MUST produce
a typed secret-safe error and no resolution.

#### Scenario: Observation differs from handoff
- **WHEN** any identity, principal, receipt or generation value differs
- **THEN** resolution fails with a bounded mismatch code and field
- **AND** no physical connection or credential is returned.

#### Scenario: Handoff is absent
- **WHEN** none of the project binding variables are configured
- **THEN** the adapter returns unbound mode without claiming project readiness.

### Requirement: Evidence retention is provider-owned
The adapter MUST accept only `sanitized` or explicitly approved `full_local`
policy and MUST confine its evidence root to the configured allowlist.

#### Scenario: Full local lacks approval
- **WHEN** `full_local` is declared without non-production approval
- **THEN** resolution fails before filesystem or runtime mutation.

#### Scenario: Local path is unsafe
- **WHEN** the profile/env/evidence path is missing, non-regular, symlinked or
  escapes its allowed root
- **THEN** resolution fails closed without following the unsafe path.
