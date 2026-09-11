## MODIFIED Requirements

### Requirement: Remote TestClient launch selects the exact QA platform build

The remote launch contract SHALL carry the exact non-empty four-component QA
platform version to the Windows host-agent, which SHALL resolve 1cv8 only from
that catalog version and SHALL NOT silently select a newer installed build.

#### Scenario: Requested platform is installed

- **WHEN** the provider requests `8.3.27.2130` and the station also contains a
  newer platform build
- **THEN** the host-agent launches 1cv8 from the `8.3.27.2130` catalog directory
- **AND** reports that resolved version in bounded launch metadata.

#### Scenario: Requested platform is invalid or absent

- **WHEN** `platform_version` is empty, is not exactly four numeric components,
  or that exact catalog version has no resolved 1cv8
- **THEN** launch fails before process creation with
  `invalid-platform-version` or `platform-version-not-found`
- **AND** it does not fall back to a different installed build.
