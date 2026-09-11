## Why

A real demo button must be classified before execution because visual
appearance does not prove that it is a safe UI action. The pilot must reject
or route unsafe behavior before any click reaches a live infobase.

## What Changes

- Classify the selected demo button as safe UI action, inert local action,
  business mutation, unsupported or blocked before execution.
- Build or reject a reviewed manifest row with target marker, pre-state,
  post-state, recovery expectation, action result markers, allowed family and
  `mutates_business_data=false`.
- Route business command clicks, writes, save/post/delete/fill/import/export
  and external side effects to V3 or later mutation/recovery work.
- Produce a compact classification decision for the guarded capture change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Demo real-button pilots must pass a fail-closed
  safety classification before capture or execution.

## Impact

- Protocol planning evidence under
  `.artifacts/openspec/classify-demo-button-safety-contract/<run-id>/`.
- May use read-only runtime context, Vanessa form analysis, metadata or EDT
  context to classify command semantics.
- Does not execute the button; no raw capture, replay payload or accepted
  mapping output is produced by this change.
