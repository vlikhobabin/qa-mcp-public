## ADDED Requirements

### Requirement: List reads retry an empty form descriptor from a cold client

`read_list_grid` / `read_list_column` table resolution SHALL treat a live form descriptor with
no opened form AND no elements as a cold client whose form has not rendered yet (distinct from a
genuinely empty catalog, which still exposes a `Table` element) and SHALL retry the descriptor
read a bounded number of times (configurable via `QA_MCP_DESCRIPTOR_WARMUP_ATTEMPTS` and
`QA_MCP_DESCRIPTOR_WARMUP_DELAY_SEC`) before failing. When all attempts still return an empty
descriptor, the `list-table-unresolved` diagnostic SHALL report `descriptor_empty: true`, the
`warmup_attempts` count, and a reason indicating the client may still be warming up. The retry
SHALL be bounded (no unbounded loop).

#### Scenario: A cold-client empty descriptor is retried and then resolves

- **WHEN** the first live descriptor read returns an empty descriptor (no opened form, 0 elements)
  and a subsequent read within the bounded attempts returns the rendered form with a table
- **THEN** the table resolves normally and the result records how many warm-up retries were needed

#### Scenario: Exhausted retries report a warming-up diagnostic without looping forever

- **WHEN** every attempt (up to the configured bound) returns an empty descriptor
- **THEN** resolution stops after the bounded number of attempts and returns a
  `list-table-unresolved` diagnostic carrying `descriptor_empty: true`, the `warmup_attempts`
  count, and a "client may still be warming up" reason
