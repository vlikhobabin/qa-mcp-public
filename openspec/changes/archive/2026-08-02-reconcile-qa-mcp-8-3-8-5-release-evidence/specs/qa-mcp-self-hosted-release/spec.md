## ADDED Requirements

### Requirement: Multi-version release evidence preserves live platform identity

A qa-mcp release that declares both supported platform baselines SHALL retain a
release-equivalent Agent/MCP HTTP attach/read result for `8.3.27.2130` and
`8.5.1.1343`. Each result MUST identify its delivery model, canonical `/mcp`
endpoint, full live platform version, attach outcome, read outcome, and cleanup
or retained-runtime disposition. An 8.5 result MAY use the validated 8.3
protocol-data set, but it MUST continue to declare the live 8.5 full version.

#### Scenario: Both supported baselines have release-equivalent proof

- **WHEN** a release is reviewed as supporting 1C `8.3.27.2130` and
  `8.5.1.1343`
- **THEN** retained evidence contains one Agent/MCP HTTP attach/read result for
  each full platform build
- **AND** each result names Windows model-B or Linux host-platform model-A and
  uses the canonical `/mcp` endpoint

#### Scenario: 8.5 validates with 8.3 protocol data

- **WHEN** the 8.5 release smoke resolves capture-backed operations through the
  validated `_bundled/8.3` protocol-data set
- **THEN** synthesized and replayed session frames continue to declare the live
  full version `8.5.1.1343`
- **AND** the delivery does not require `_bundled/8.5` to be populated while the
  validate-first smoke remains green

#### Scenario: Validate-first smoke exposes protocol drift

- **WHEN** the 8.5 release smoke fails because a protocol capability is red
- **THEN** the release evidence records the failed capability and sanitized
  outcome
- **AND** support work is routed to a separate protocol/capture change before
  any 8.5-specific corpus is bundled

### Requirement: Active delivery guidance distinguishes platform and protocol-data versions

Active qa-mcp delivery guidance SHALL document `8.3.27.2130` and
`8.5.1.1343` as supported baseline builds, SHALL state that same-family builds
require validate-first evidence, and SHALL distinguish the full live platform
version passed through `QA_MCP_PLATFORM_VERSION` / `PLATFORM_ROOT` from the
protocol-data family selected at runtime.

#### Scenario: Operator selects a supported full platform build

- **WHEN** an operator follows active delivery guidance for 8.3 or 8.5
- **THEN** the guidance passes the selected full `x.y.z.w` build into the
  shipped runtime
- **AND** it explains that another build in the same family may work only after
  validate-first verification

#### Scenario: Operator follows the 8.5 fallback policy

- **WHEN** an operator deploys against `8.5.1.1343`
- **THEN** active guidance states that the validated 8.3 protocol-data set is
  reused while the live platform identity remains 8.5
- **AND** it instructs recapture or `_bundled/8.5` population only after a red
  capability is identified

### Requirement: Streamable HTTP request validation preserves the ASGI receive lifecycle

The self-hosted HTTP runtime SHALL validate and replay a JSON-RPC request body
once, and SHALL forward subsequent receive events from the original ASGI
channel so the Streamable HTTP transport can deliver its response and observe
client disconnects.

#### Scenario: Downstream receives the validated body and real disconnect

- **WHEN** a valid UTF-8 JSON-RPC body passes through the request gate
- **THEN** the first downstream receive returns that validated body exactly once
- **AND** a later downstream receive obtains the real `http.disconnect` event
  instead of an unbounded sequence of synthetic empty request bodies

### Requirement: Container cleanup discovers ownership markers under runtime home

Stateless TestClient cleanup in an installed or container runtime SHALL resolve
its ownership-marker root from the explicit
`QA_MCP_TESTCLIENT_OWNERSHIP_ROOT` override when present, otherwise from the
writable `QA_MCP_HOME`, before falling back to the source-checkout default.

#### Scenario: Container launch and cleanup share the same ownership root

- **WHEN** a container sets `QA_MCP_HOME=/work`, launches an owned TestClient,
  and does not set an explicit ownership-root override
- **THEN** launch writes and cleanup discovers the ownership marker below
  `/work/runtime/protocol-research/testclient-lifecycle`
- **AND** cleanup still validates the recorded PID identity before stopping the
  owned TestClient and Xvfb

#### Scenario: Explicit ownership root wins

- **WHEN** both `QA_MCP_HOME` and `QA_MCP_TESTCLIENT_OWNERSHIP_ROOT` are set
- **THEN** stateless cleanup searches the explicit ownership root
