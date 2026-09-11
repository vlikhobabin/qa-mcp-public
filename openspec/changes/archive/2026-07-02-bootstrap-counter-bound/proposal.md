## Why

The synthesized bootstrap can choose a random five-digit counter base that overflows when later bootstrap frames add
their fixed counter deltas. That creates a rare non-deterministic session startup crash unrelated to the live
TestClient.

## What Changes

- Bound the random `counter_base` by the maximum rendered bootstrap counter delta, rather than by the raw five-digit
  maximum.
- Keep explicit caller-provided `counter_base` validation unchanged so invalid bases still fail loudly.
- Add an offline boundary regression test proving the maximum random base can render all synthesized bootstrap frames.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: synthesized bootstrap generation must never randomly select a counter base that cannot render
  every generated bootstrap frame into the fixed-width counter field.

## Impact

- Touches Python protocol manager code under `src/qa_mcp/protocol/bootstrap_synth.py`.
- Adds offline tests under `tests/test_bootstrap_synth.py`.
- Does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots or new protocol capture evidence.
