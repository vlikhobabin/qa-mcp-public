## ADDED Requirements

### Requirement: Exact Apache-2.0 license binding
The repository SHALL bind the operator-approved license exactly as SPDX
`Apache-2.0` through the canonical license text, NOTICE and package metadata,
and MUST reject a missing, different or additional license choice.

#### Scenario: Exact license is consistent
- **WHEN** the public policy gate reads LICENSE, NOTICE, package metadata and
  the machine-readable publication policy
- **THEN** each license choice is exactly `Apache-2.0` and the canonical Apache
  License 2.0 text is present

### Requirement: Public-safe publication and contact boundary
The repository SHALL define one audited-snapshot history strategy, SHALL keep
excluded internal ancestors outside the public import, and SHALL expose only
role-based public issue and private vulnerability-reporting routes.

#### Scenario: Excluded history is not promoted
- **WHEN** selected-history review finds personal metadata or private lab
  identifiers in pre-snapshot ancestors
- **THEN** the gate reports bounded excluded-history counts and does not admit
  those ancestors into publishable history

#### Scenario: Public contacts contain no personal data
- **WHEN** policy contacts are validated
- **THEN** no personal email, credential, private endpoint or named machine is
  present and security reports use the repository's private reporting route

### Requirement: Published I2 remains a mandatory fail-closed prerequisite
The public policy SHALL preserve the exact published OSS-07-I2 matrix, freeze,
helper, verifier and capability spec and MUST require the unchanged control and
all 23 hostile mutations to return their reviewed outcomes.

#### Scenario: I2 control and mutations pass
- **WHEN** the repository-readiness gate executes the published I2 verifier
  with `--run-mutations`
- **THEN** the control returns zero with `46/14/5/D14` and all 23 hostile cases
  fail with their named classes

#### Scenario: I1 material is proposed
- **WHEN** a path or byte from the failed OSS-07-I1 payload is introduced
- **THEN** publication fails closed and no restoration, copy or reconstruction
  is admitted
