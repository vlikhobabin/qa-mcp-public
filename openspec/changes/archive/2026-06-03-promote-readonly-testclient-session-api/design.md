## Context

The exploratory `TestClientSession` can already connect to a running
`/TESTCLIENT`, send captured/generated manager frames and summarize read-only
responses. Package promotion should make that behavior reusable while keeping
the safety boundary clear: direct session code can read active window/form
state, but it must not expose action or mutation commands.

## Goals / Non-Goals

**Goals:**

- Move live session lifecycle, `send_and_read`, initial UI exchange and
  read-only query methods into package code.
- Return typed result objects or dictionaries that preserve evidence status,
  source capture/template paths and output directory policy.
- Support existing query families: `initial-ui`, `active-window-context`,
  `active-form-context`, `form-summary` and `form-element-details`.
- Provide offline tests for socket exchange and response parsing.
- Provide a Windows-native optional live smoke command and retained compact
  evidence path when the lab TestClient is available.

**Non-Goals:**

- Do not start or stop unrelated 1C sessions.
- Do not add write/action APIs.
- Do not require a live TestClient for every developer test run.
- Do not mark incomplete-hash query families as accepted.

## Decisions

### Session API Is Explicitly Read-Only

Package methods should use names that make the read-only boundary visible.
Action-capable methods should not be introduced in this change. Any future
action surface belongs to the safe-action card and requires recovery evidence.

### Live Runtime Evidence Is A Delivery Gate When Available

Offline tests are mandatory. A live read-only smoke should be planned against
the configured TestClient port when the lab runtime is available. If the live
environment is unavailable during `$opsx-do`, the delivery must record a
provider/environment gap instead of hiding the missing evidence.

### Raw Output Remains Runtime-Scoped

Session output directories may contain raw sent/received payloads. Those paths
remain under `runtime/protocol-research/` or another ignored location. Any
committed evidence must be a compact summary under `docs/protocol-research/`.

## Risks / Trade-offs

- Live smoke can be environment-sensitive. Mitigation: keep offline tests as
  the primary gate and record environment gaps explicitly.
- Socket read timing can be flaky. Mitigation: keep configurable timeouts and
  deterministic fake-socket tests.
- Query APIs can imply accepted coverage for incomplete families. Mitigation:
  include evidence status in result metadata and tests.

## Migration Plan

Promote session code after frame primitives. Keep `python_manager_probe.py`
and other tools callable through their existing CLI while they import the
package session API.
