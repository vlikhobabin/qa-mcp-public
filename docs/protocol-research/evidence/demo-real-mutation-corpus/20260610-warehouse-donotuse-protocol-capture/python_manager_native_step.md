# Step 2 — Package-Native Mutation Driver (foundation + honest open item)

Goal: move the capability into `qa_mcp.protocol` and **construct** the write via
`render_write_frame` instead of raw-replaying it, toward native navigation+write.

## Delivered

- `src/qa_mcp/protocol/native_mutation.py`: `GuidRebinder` (learn live session
  GUIDs by first-appearance order; substitute ASCII / UTF-16LE / LE-byte forms)
  + `run_native_mutation_flow` (navigate by rebound-replay, **render** the
  action-write frames with `render_write_frame`). Unit-tested, no runtime.
- `tools/protocol-research/native_mutation_probe.py`: live CLI; locates the 14
  write frames in the manager stream by payload identity (ordinals 271–284).

## Write rendering is correct (offline-verified)

The package-rendered write frames were proven **byte-identical to the accepted
adaptive-replay frames**:

- `render_write_frame` leaves **zero** stale captured GUIDs in any encoding
  (ASCII, UTF-16LE, LE bytes) for all 14 frames;
- `render_write_frame(...)` equals `rebinder.apply(captured)` for all 14 frames
  with a given GUID map.

So the write construction path is sound.

## Live result: full flow driven, but write exchange did not match

Two live package-native runs (fresh nonce, then preserved nonce) each:

- drove the full **861/861** frames with the client answering every frame, zero
  hang (`diverged_at_send_index: null`);
- rendered all **14** write frames;
- produced `manager_to_client` action-write frames that **normalize-match** the
  reference (the sent commands are right);
- but the **client responded with uniform 665-byte frames** (vs the reference's
  varied responses), so `compare_probe_reference --mode probe-ordinal` returned
  `mismatch` (`client_to_manager` hash differs, structural mismatch).

This is **not** explained by the write frames — they are byte-identical to the
accepted adaptive replay. The earlier adaptive replay (same navigation logic, a
different live session) **did** match the reference (`accepted`). So the native
runs' divergence is a **cross-session reproduction issue**: replaying captured
navigation frames with learn-by-first-appearance GUID alignment is sensitive to
per-session response ordering/state, and these two sessions went down a
different path before the write context was correct.

## Honest status and what it motivates

- `TestedFormButton.Click` remains **`accepted_reviewed`** on the adaptive replay
  (which reproduced the reference write exchange live). The acceptance stands;
  what is not yet reliable is *re-reproducing* it across fresh sessions.
- The package foundation (driver, rebinder, correct write rendering) is in place.
- The flaky part is **replay-based navigation**. This directly motivates the
  real step-2 endpoint: **native semantic navigation** — package operations that
  reach the card deterministically from the initial state (open list, select
  row, open card) and then send the rendered write — instead of replaying 861
  captured navigation frames. That removes the cross-session alignment fragility.
  Decoding the navigation command semantics (catalog name, row value, button)
  is the next decode target.

Raw probe streams stay under ignored `runtime/protocol-research/captures/`.
