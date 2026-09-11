# Python Manager Package Smoke Environment Gap

- Recorded at: `2026-06-03`
- Change: `promote-readonly-testclient-session-api`
- Expected evidence: compact read-only package smoke under
  `docs/protocol-research/evidence/python-manager-package-smoke/<run-id>/`
- Status: `not_run`

## Reason

The delivery verified the package session API offline with fake-socket and
fixture-style checks. `scripts\check-protocol-lab.ps1` reported the Vanessa
target environment as valid, but also reported that no manager or TestClient
process was started during this run.

## Residual Risk

Live socket timing and platform-specific TestClient behavior still need a
fresh retained read-only smoke before relying on this package API as runtime
evidence. The API remains read-only and does not perform clicks, text input,
command execution or business-data writes.
