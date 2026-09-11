## ADDED Requirements

### Requirement: Disposable Windows UI proof remains bound to one owned TestClient lifecycle

The remote qa-mcp launch and UI operations SHALL use the owned lifecycle target
returned for the restored disposable infobase. The first protocol/UI operation
MUST NOT be preceded by a consuming generic TCP readiness connection.

#### Scenario: Restored S50 infobase yields a usable lifecycle target

- **WHEN** `launch_test_client` starts the restored S50 disposable infobase on
  the authorized Windows host
- **THEN** it returns a live owned PID, TPort and lifecycle handle
- **AND** the first lifecycle-bound UI operation can open
  `Справочник.S50ProofItems` without targeting a stale or unrelated window.

#### Scenario: Catalog item is created and read back

- **WHEN** the lifecycle-bound qa-mcp UI path opens the S50 catalog and creates
  one uniquely named disposable item
- **THEN** the same lifecycle shows that name in the visible list or visible
  cells
- **AND** screenshot evidence is retained only under ignored runtime state.
