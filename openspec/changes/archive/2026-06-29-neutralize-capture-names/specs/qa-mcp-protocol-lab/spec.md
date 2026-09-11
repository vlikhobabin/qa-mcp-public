## ADDED Requirements

### Requirement: Bundled captures carry neutral descriptive identities
The bundled capture directories SHALL use **neutral, descriptive** names
(e.g. `demo-write`, `listform-read`, `cellread`) that carry **no card numbers or
capture dates**, in both the `_bundled/<version>/captures/` data tree and the
`capture=` default values exposed by the MCP tool schemas. The engine SHALL
resolve and replay the renamed captures unchanged; the descriptive meaning is
preserved (the card number + date move to git history + the board).

#### Scenario: Shipped capture identities carry no internal R&D trace
- **WHEN** the bundled captures and the tool `capture=` defaults are inspected
- **THEN** their names contain no `card N` token and no capture-date suffix
- **AND** each name still describes the capture's purpose (e.g. `demo-write`,
  `listform-read`)

#### Scenario: Renamed captures still resolve and replay
- **WHEN** a tool uses a renamed bundled capture as its default (or it is resolved
  via `resolve_capture_dir`)
- **THEN** the capture resolves from `_bundled/<version>/captures/<neutral-name>/`
  and the engine replays it with identical behavior to the pre-rename name
- **AND** the offline `pytest` suite stays green
