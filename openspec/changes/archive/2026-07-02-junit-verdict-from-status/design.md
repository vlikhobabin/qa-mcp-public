## Context

`junit_xml` consumes the same report dictionaries that `run_scenario` and `_RESULTS_LOG` produce:

```text
{scenario, status, duration_sec, started_at, steps}
```

The current implementation scans step statuses to count failures and errors. That loses the scenario-level verdict in
two ways:

- `status: "failed"` with no bad steps becomes a passing testcase.
- a testcase with both `assert_failed` and `error` steps increments both `failures` and `errors`.

## Decision

Derive the testcase class from scenario status first:

- `status == "passed"` -> no failure/error element;
- `status == "error"` -> `<error>`;
- any other non-passed status -> `<failure>`.

Step details remain diagnostic context. When an errored step exists, it may upgrade a failed scenario's JUnit element to
`<error>` so exceptions remain visible to CI. A single testcase still increments only one counter.

The invariant is:

```text
tests == passed + failures + errors + skipped
```

`skipped` is currently zero because qa-mcp scenario results do not expose a skipped scenario status.

## Verification Strategy

Offline unit tests will parse the emitted XML and assert:

- a failed scenario with no bad steps emits one `<failure>`;
- a scenario containing both `assert_failed` and `error` step details is counted once, as an error;
- the tests/failures/errors counts match the actual testcase children;
- Cyrillic scenario/step names and messages are escaped by `ElementTree` and round-trip through XML parsing.

## Runtime And Safety

No live TestClient or 1C runtime is involved. `write_test_report` keeps its existing file-writing behavior and uses the
updated pure `junit_xml` function.

## Open Questions

None.
