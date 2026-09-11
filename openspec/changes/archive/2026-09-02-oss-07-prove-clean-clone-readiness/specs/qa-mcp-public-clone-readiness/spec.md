## ADDED Requirements

### Requirement: Isolated Git-visible source snapshot
The verifier SHALL construct an owned temporary snapshot from exactly the
Git-visible reviewed paths, SHALL exclude repository metadata and ignored/local
state, SHALL exclude absolute or external symlinks, and SHALL remove only that
owned temporary directory on exit.

#### Scenario: Ignored credential or runtime state exists
- **WHEN** the working repository contains ignored auth, env, capture or runtime
  evidence files
- **THEN** none is copied into the isolated snapshot or used by its checks

### Requirement: Public package builds without private inputs
The isolated snapshot SHALL build sdist and wheel from the public lock/source,
and built metadata SHALL declare Apache-2.0 and include required legal files and
runtime package data.

#### Scenario: Offline source build succeeds
- **WHEN** the snapshot runs the documented offline build with public cached
  dependencies
- **THEN** sdist and wheel are created, inspect cleanly and require no private
  endpoint, credential or repository-local service

#### Scenario: Snapshot install and focused gates succeed
- **WHEN** the isolated snapshot runs locked offline dependency sync
- **THEN** package import, focused readiness tests, disclosure audit,
  provenance, docs and the I2 23-mutation oracle all execute inside that
  snapshot without resolving an external workspace symlink

### Requirement: Complete offline readiness floor
Before review and publication, delivery SHALL pass locked dependency sync,
complete non-live pytest, package build, policy/disclosure audit, provenance
check, I2 23-mutation oracle, public docs/link checks, strict OpenSpec and
tracked/untracked whitespace checks.

#### Scenario: Every mandatory check passes
- **WHEN** the exact reviewed payload runs the complete declared command set
- **THEN** every command returns zero with a concise outcome and any raw output
  is retained only under ignored ChangeRail runtime evidence

#### Scenario: One mandatory check fails
- **WHEN** any mandatory command returns non-zero or lacks retained outcome
- **THEN** review handoff and publication fail closed
