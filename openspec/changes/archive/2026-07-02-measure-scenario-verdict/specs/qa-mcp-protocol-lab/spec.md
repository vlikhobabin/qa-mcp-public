## ADDED Requirements

### Requirement: `measure_scenario` reports the scenario verdict from scenario status
`measure_scenario` SHALL derive `scenario_ok` from the `ScenarioResult.to_dict()` status returned by
`run_scenario`. The value SHALL be `true` only when the result is a dictionary whose `status` is exactly `"passed"`.
Missing `ok` keys, malformed payloads, failed statuses and errored statuses MUST NOT be treated as truthy pass results.

#### Scenario: Failed measured scenario is not reported as passed
- **WHEN** `measure_scenario` runs a feature and `run_scenario` returns a result dictionary with `status: "failed"`
- **THEN** the `measure_scenario` result contains `scenario_ok: false`
- **AND** the coverage/perf report keys remain present

#### Scenario: Passed measured scenario is reported as passed
- **WHEN** `measure_scenario` runs a feature and `run_scenario` returns a result dictionary with `status: "passed"`
- **THEN** the `measure_scenario` result contains `scenario_ok: true`

#### Scenario: Malformed measured scenario result is fail-closed
- **WHEN** `run_scenario` returns a payload that is not the expected result dictionary
- **THEN** `measure_scenario` does not convert that payload to a truthy pass verdict
