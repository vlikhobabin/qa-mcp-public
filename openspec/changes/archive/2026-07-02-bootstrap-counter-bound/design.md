## Context

`src/qa_mcp/protocol/bootstrap_synth.py::synthesize_bootstrap` renders synthesized session-bootstrap frames from an
in-repo template. When no explicit `counter_base` is provided, it currently chooses any five-digit value. Frame 4 is
rendered from the same base plus a fixed delta, so the highest random bases can overflow the fixed five-digit field.

This is a pure Python synthesis issue. It does not create new protocol claims, capture sources, dynamic fields or live
runtime cleanup behavior.

## Goals / Non-Goals

**Goals:**

- Choose a random default `counter_base` that leaves room for every synthesized bootstrap frame counter.
- Derive the allowed range from template metadata instead of hard-coding a known delta.
- Preserve explicit invalid-base failures for caller-provided values.
- Verify the upper boundary offline.

**Non-Goals:**

- No changes to captured templates, frame offsets, platform-version injection or ticket GUID rendering.
- No live TestClient bootstrap run.
- No protocol evidence index update because this is a generator range guard, not new wire knowledge.

## Decisions

- Compute the maximum needed counter delta from the frame set that uses the synthesized counter. This keeps the random
  range tied to template shape if later frames are added.
- Keep `_render_counter` as the final authority for invalid explicit values. The default generator avoids invalid
  values, while explicit caller mistakes still raise clearly.
- Add a boundary test that monkeypatches randomness to return the maximum allowed offset and verifies all generated
  frames, including frame 4, render within the fixed-width field.

## Risks / Trade-offs

- The random base search space shrinks by only the maximum bootstrap delta, which is negligible for uniqueness and
  removes the non-deterministic overflow.
- If future template metadata changes without updating the frame list, the boundary test should fail before runtime.
