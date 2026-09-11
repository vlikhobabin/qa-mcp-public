## ADDED Requirements

### Requirement: JUnit reports use the scenario-level verdict
`junit_xml` SHALL derive each testcase outcome from the scenario-level `status` field, not only from step-level status
scans. A scenario whose status is not `"passed"` MUST emit a JUnit failure or error element even when its step list is
empty or lacks bad step details.

#### Scenario: Failed scenario without bad step details is not green
- **WHEN** `junit_xml` receives a scenario dictionary with `status: "failed"` and no failed step entries
- **THEN** the emitted testcase contains a `<failure>` element
- **AND** the suite failure count includes that testcase

#### Scenario: Errored scenario is emitted as a JUnit error
- **WHEN** `junit_xml` receives a scenario dictionary with an error verdict or error step detail
- **THEN** the emitted testcase contains an `<error>` element
- **AND** the suite error count includes that testcase

### Requirement: JUnit suite counters count each testcase once
`junit_xml` SHALL count each scenario testcase in at most one terminal bucket: passed, failure or error. A scenario that
contains both assertion-failed and error step details MUST NOT increment both `failures` and `errors` for the same
testcase. The suite counters SHALL satisfy `tests == passed + failures + errors + skipped`, with skipped currently zero
unless a skipped scenario status is added later.

#### Scenario: Mixed bad step details count once
- **WHEN** one scenario contains both `assert_failed` and `error` step details
- **THEN** the emitted JUnit suite counts that scenario exactly once
- **AND** the testcase has one terminal child element

#### Scenario: XML escaping remains valid
- **WHEN** scenario names, step names or messages contain Cyrillic text and XML-sensitive characters
- **THEN** the emitted JUnit XML is parseable and preserves the decoded text after XML parsing
