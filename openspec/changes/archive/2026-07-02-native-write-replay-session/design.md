## Context

`native_write.py` currently repeats the same protocol replay shape across many
operations: open a socket, drain the initial response, build a `GuidRebinder`,
replay setup frames, retarget operation frames, observe responses and decide a
verdict. CR-03 added fail-closed retarget/read-back behavior and CR-04 added the
shared frame-aware receive helper. This change centralizes orchestration without
changing operation-specific templates or verdict semantics.

## Goals / Non-Goals

**Goals:**

- Provide one `ReplaySession` that owns connection setup, initial drain, setup
  replay, block replay and response collection.
- Represent each operation with a small `ReplayOp` spec: template, setup range,
  operation range, frame retarget function and verdict function.
- Preserve all existing result keys, error verdicts and send/receive timeout
  behavior.
- Keep `read_protocol_available` as the only TestClient receive implementation
  used by replay paths.

**Non-Goals:**

- Do not change protocol templates, capture fixtures or business-operation
  semantics.
- Do not introduce live 1C runtime requirements for the offline refactor gate.
- Do not remove dead code unrelated to replay orchestration; that is the final
  cleanup change.

## Decisions

- Put the replay engine in `src/qa_mcp/protocol/replay.py`.
  `native_write.py` remains the public operation facade until later extraction
  makes smaller modules worthwhile. This keeps import churn limited for the first
  change.
- Keep template dataclasses close to their existing derivation code until the
  engine is green. A follow-up within this change may move pure template helpers
  to `write_templates.py` if tests stay straightforward.
- `ReplaySession` takes the already-resolved endpoint, capture bootstrap,
  timeout values and optional send timeout. It does not read global environment.
- The engine returns response chunks and leaves commit/read-back interpretation
  to operation verdict callbacks. This avoids normalizing away important
  operation-specific result details.
- Setup replay and operation replay use the same send/observe path, including
  `ProtocolSendTimeout` handling and `GuidRebinder.observe_response`.

## Risks / Trade-offs

- Broad mechanical edits can hide behavior drift -> migrate one operation family
  at a time and keep focused offline tests around each converted result shape.
- Centralizing response collection can accidentally change timing -> call
  `read_protocol_available` directly and assert no idle-gap receive loop remains.
- Splitting too many modules at once can make review harder -> prefer a small
  engine plus minimal facade changes for this first slice.

## Migration Plan

1. Add `ReplaySession` and `ReplayOp` behind existing public functions.
2. Convert operations in small groups, keeping existing signatures and result
   dictionaries.
3. Run focused native write/protocol tests after each group.
4. Run full offline pytest and source checks before archive.
5. Rollback is file-level: revert the engine and converted operation calls.

## Open Questions

- none
