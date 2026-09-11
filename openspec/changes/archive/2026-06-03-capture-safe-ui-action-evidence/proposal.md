## Why

After the safe-action scope and row contract exist, the lab needs short
Windows-native captures for non-mutating UI state transitions. The first live
action evidence should prove what was attempted and what stayed unchanged,
without accepting unsupported action families by inference.

## What Changes

- Run short Vanessa attach-running captures for selected non-mutating actions:
  focus/activate element, activate window, switch tab/page and expand menus
  when available in the current lab.
- Retain compact evidence rows with pre-state, action, post-state, frame
  ranges, normalized hashes, dynamic fields, operation tokens, response
  markers, action result markers and replay/probe status.
- Preserve raw captures, case events and platform logs under ignored
  `runtime/protocol-research/` paths.
- Record unsupported, pending, partial, timeout, rejected or unavailable
  outcomes explicitly for any candidate action that cannot be captured safely.
- This change touches runtime lab evidence and protocol research docs. It
  requires live 1C runtime through the Windows Vanessa/TestClient lab.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require reviewed compact evidence for safe
  non-mutating UI action captures and keep unsupported actions visible.

## Impact

- Windows lab paths from `openspec/config.yaml`.
- `tools/protocol-research/protocol_corpus_runner.py` or action capture
  wrappers created by the prior change.
- Compact reviewed evidence under `docs/protocol-research/evidence/`.
- Ignored raw output under `runtime/protocol-research/`.
- Runtime cleanup must stop only owned PIDs and must not terminate unrelated
  1C sessions.
