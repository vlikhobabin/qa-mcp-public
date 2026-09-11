## ADDED Requirements

### Requirement: Discoverable public repository guide
README SHALL link public architecture, source/package installation, HTTP bearer
authentication, Windows bridge, development, support, security and
upstream-first contribution guidance that matches the current source.

#### Scenario: New contributor follows README
- **WHEN** a contributor opens README in a fresh source snapshot
- **THEN** every required topic is present or linked through an existing local
  document and no internal lab is required for offline development

### Requirement: Standard public project policies
The repository SHALL provide SECURITY, CONTRIBUTING, GOVERNANCE, SUPPORT and
CODE_OF_CONDUCT documents with role-based contacts and Apache-2.0-compatible
contribution terms.

#### Scenario: Security issue route
- **WHEN** a reporter reads SECURITY
- **THEN** the reporter is directed to private vulnerability reporting and is
  warned not to disclose secrets publicly

#### Scenario: Generic core contribution
- **WHEN** a downstream product finds a generic core defect
- **THEN** CONTRIBUTING directs the correction upstream first and keeps
  private product integration outside this repository

### Requirement: Honest pre-release and historical boundaries
Public documentation MUST NOT claim OSS-08 release publication or OSS-09
cutover is complete, and retained research/planning/staging material SHALL be
clearly distinguished from active public install guidance.

#### Scenario: Release terminology is checked
- **WHEN** the offline docs audit scans active public entry points
- **THEN** no private portal is presented as required public input and no
  stable-release/cutover completion claim is accepted

### Requirement: Public local links remain valid
The repository SHALL resolve every relative Markdown link in the declared
active public documentation surface within the source snapshot; URI schemes
and anchors are checked without network access.

#### Scenario: Local file link is broken
- **WHEN** an active public document references a missing relative file
- **THEN** the docs audit returns non-zero with the source path and target only
