## ADDED Requirements

### Requirement: Disposable preflight failures are typed and privacy-safe
The investigation receipt SHALL distinguish `snapshot_read_failure`,
`metadata_set_authority_failure`, `task_token_mismatch`, and
`evidence_write_failure` from a successful disposable proof. It MUST retain
only typed statuses, booleans, bounded counts, canonical hashes, and bounded
exit-code mappings; it MUST NOT retain raw paths, exception text, credentials,
timestamps, UI data, screenshots, or 1C configuration content.

#### Scenario: A preflight boundary fails
- **WHEN** the exact worker or its receipt boundary fails before a successful
  disposable result
- **THEN** the retained outcome identifies exactly one typed failure class
- **AND** no raw diagnostic value is serialized

### Requirement: Session controls use one exact disposable owner/worker chain
The investigation SHALL invoke the same structurally verified session owner
and child worker as a session-0 control and through one exact
`InteractiveToken`/`Limited` session-1 task on exact-owned disposable files.
Every invoked script that reads a probe MUST snapshot `LastAccessTimeUtc`
before any read, restore it through `finally` as the sole final probe
operation, and perform no later probe read. The outer runner MUST NOT read a
handed-off probe.

#### Scenario: Session 0 and session 1 prove the selected worker
- **WHEN** the disposable matrix runs on `historical-user@192.0.2.201`
- **THEN** both sessions report the exact expected token identity and a typed
  disposable outcome from the same owner and worker hashes
- **AND** the exact task, stage, and stage-bound process counts return to zero

### Requirement: Real-target restoration remains session-0 owned
Any successor that consumes this investigation SHALL keep first snapshot and
sole final metadata restoration for the real target in the session-0 outer
broker. Session 1 MUST receive only exact-owned staged inputs and privacy-safe
expected hashes and MUST NOT open, read, write, or restore the real 1C
configuration unless a separate reviewed authority change explicitly replaces
this decision.

#### Scenario: A successor prepares another bounded confirmation
- **WHEN** S4-R1 is reconsidered after this investigation
- **THEN** its session-1 scripts contain no real-configuration file operation
- **AND** the session-0 owner restores metadata in `finally` with no later
  real-target read

### Requirement: Investigation evidence is non-admitting and preserves lineage
The investigation MUST NOT start 1C or invoke S3, S4, S5, or S7. It SHALL
preserve the blocked S4-R1 payload, the four immutable S4-R2 hashes, protected
S7/fixture/OSS-07/OSS-08 bytes, unrelated staged state, and zero UI action.

#### Scenario: Investigation handoff is prepared for review
- **WHEN** the card-owned payload and retained evidence are reconciled
- **THEN** preservation hashes match their pre-investigation values
- **AND** the manifest contains only investigation-owned committable paths
- **AND** the result explicitly grants no S4-R1 live admission
