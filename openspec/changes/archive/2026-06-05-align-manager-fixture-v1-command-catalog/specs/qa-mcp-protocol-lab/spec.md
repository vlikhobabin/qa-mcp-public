## ADDED Requirements

### Requirement: Manager fixture V1 command catalog is synchronized

The protocol lab SHALL keep the manager fixture V1 read-only command catalog
consistent across BSL source, capture-runner manifests and reviewed evidence.

#### Scenario: Manifest is generated from reviewed command ids

- **WHEN** the capture runner writes `manager_harness_manifest.json`
- **THEN** every command id in the manifest matches the reviewed V1 command
  catalog
- **AND** the manifest records the selected smoke subset separately from the
  full catalog when only part of the catalog is executed

#### Scenario: BSL catalog matches tooling catalog

- **WHEN** the manager harness source defines V1 read-only commands
- **THEN** its command ids, command kinds, target markers and expected markers
  match the reviewed catalog used by protocol tooling
- **AND** catalog drift is reported by offline verification before live capture
