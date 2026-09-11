# qa-mcp project target composition

## Purpose

Define how one validated provider runtime-target resolution is frozen into an
application/server instance and reported by readiness without granting
lifecycle authority or changing ordinary unbound standalone behavior.

## Requirements

### Requirement: Application composition freezes one optional resolution
Each qa-mcp application instance SHALL carry either one immutable resolved
project target or explicit unbound state for its lifetime.

#### Scenario: Two server instances are composed
- **WHEN** bound and unbound servers are created in one process
- **THEN** each observes only its own target/settings state.

### Requirement: Startup fails closed on configured binding errors
Configured project binding errors MUST prevent project-mode server composition,
while absent binding MUST preserve standalone operation.

#### Scenario: Configured profile is invalid
- **WHEN** startup resolves a partial, malformed or mismatched handoff
- **THEN** composition fails with its typed runtime-target error
- **AND** no fallback target or lifecycle resource is selected.

#### Scenario: Binding is absent
- **WHEN** startup has no project handoff variables
- **THEN** the ordinary standalone server is composed unchanged.

### Requirement: Doctor reports secret-safe target readiness
The ordered doctor chain SHALL report bound/unbound/invalid target readiness
without physical path, connection or credential values.

#### Scenario: Bound readiness is inspected
- **WHEN** doctor runs for a resolved target
- **THEN** it reports logical identity, policy and observation status before
  later lifecycle checks.

### Requirement: Readiness is non-mutating
Composition and readiness MUST NOT start TestClient, Xvfb, Apache management,
host-agent lifecycle or protocol traffic.

#### Scenario: Cross-platform adapter preflight runs
- **WHEN** Linux and Windows profile readiness is evaluated
- **THEN** before/after process and listener inventory is unchanged.
