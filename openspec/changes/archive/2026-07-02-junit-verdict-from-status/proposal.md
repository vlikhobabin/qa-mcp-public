## Why

The JUnit writer currently derives testcase outcome from step scans, not from the scenario result status. That can
render a `status: "failed"` scenario as passing when the bad step detail is absent, and it can count one testcase as
both a failure and an error when both step statuses appear.

## What Changes

- Make `junit_xml` derive each testcase verdict from the scenario-level `status`.
- Count each scenario exactly once: passed, failure or error.
- Use step details only to choose the diagnostic message/body for the emitted `<failure>` or `<error>` element.
- Add offline tests for failed-with-no-bad-steps, mixed assert/error steps and the suite-count invariant.
- Preserve Cyrillic/XML escaping behavior covered by existing reporting tests.

This change touches **Python manager reporting code** and **offline tests** only. It does not require live 1C runtime,
Vanessa MCP, EDT/meta snapshots or protocol capture refresh.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: JUnit scenario reports must reflect the scenario-level verdict honestly and maintain coherent
  suite counters.

## Impact

- `src/qa_mcp/scenario/reporting.py` — JUnit outcome and counter derivation.
- `tests/test_reporting.py` — offline regression coverage for scenario-status verdicts and count invariants.
- No MCP tool signature change; `write_test_report` continues to emit `junit.xml` in the same location.
