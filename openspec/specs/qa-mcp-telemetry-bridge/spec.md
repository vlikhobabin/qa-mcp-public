# qa-mcp Telemetry Bridge Specification

## Purpose

Define qa-mcp runtime behavior for emitting bounded semantic QA bridge
observations into active suite traces.

## Requirements

### Requirement: QA outcomes emit trace bridge observations
qa-mcp SHALL append a `qa_telemetry_bridge` observation to the active suite
trace when scenario, report, screenshot or verification-summary surfaces
produce a semantic QA outcome and trace context is available.

#### Scenario: Scenario outcome is appended
- **WHEN** `run_scenario` or `run_step` produces a scenario result while a suite
  trace context is configured
- **THEN** qa-mcp appends an evidence event whose payload contains
  `qa_bridge_observation.kind` equal to `qa_telemetry_bridge`
- **AND** the observation includes `provider_id=qa-mcp`, owner path, subject,
  status, duration when known, and a retained evidence path or summary when
  available

#### Scenario: Report outcome is appended
- **WHEN** `write_test_report` writes JUnit or Allure outputs while a suite
  trace context is configured
- **THEN** qa-mcp appends a `qa_telemetry_bridge` observation for the report
  write
- **AND** the observation references the retained report directory or files
  rather than embedding report contents

#### Scenario: Screenshot outcome is appended
- **WHEN** `capture_screenshot` returns a retained screenshot path while a suite
  trace context is configured
- **THEN** qa-mcp appends a `qa_telemetry_bridge` observation for the screenshot
  surface
- **AND** the observation stores the retained path and metadata only, not the
  image bytes

### Requirement: Trace context absence is safe
qa-mcp SHALL preserve current tool behavior when no active suite trace context
is present.

#### Scenario: Missing context is a no-op
- **WHEN** a scenario, report, screenshot or verification-summary surface runs
  without `AI1C_MCP_PROXY_WORKSPACE`, trace id or proxy trace context file
- **THEN** the tool returns its normal result
- **AND** qa-mcp does not raise an error or attempt to create a new trace

#### Scenario: Invalid context is bounded
- **WHEN** the configured trace context file is unreadable or malformed
- **THEN** qa-mcp does not expose a traceback through the MCP result
- **AND** any diagnostic is bounded to the file path and error class

### Requirement: Bridge evidence remains bounded
qa-mcp SHALL normalize QA bridge observations through a bounded allowlist and
MUST NOT embed raw screenshots, live data, UI trees, credentials or customer
payloads.

#### Scenario: Raw payload fields are rejected
- **WHEN** a QA outcome includes screenshots, report contents, UI data or other
  large/raw fields
- **THEN** the emitted observation includes only retained paths, counts, status,
  duration, subject, owner metadata and sanitized summaries
- **AND** raw binary/image or live-data content is absent from the trace payload

#### Scenario: Failure details are summarized
- **WHEN** a QA outcome has a failure or degraded status
- **THEN** the emitted observation includes a bounded error class or summary
- **AND** the summary is truncated before it can carry raw customer payloads
