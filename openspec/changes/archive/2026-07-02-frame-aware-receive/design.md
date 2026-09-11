## Context

`src/qa_mcp/protocol/session.py` and
`src/qa_mcp/protocol/native_mutation.py` both implement socket draining as
"read until the connection is idle". The protocol stream already has the tail
marker defined in `frames.py`, so an idle pause inside a large response should
not be treated as a frame boundary. The duplicate implementations also differ
on clock source: one uses wall-clock time and the other uses monotonic time.

## Goals / Non-Goals

**Goals:**
- Provide one shared receive helper for TestClient protocol sockets.
- Prefer the protocol tail marker for response completion.
- Keep a hard deadline and idle fallback so older or tail-less frames still
  return bounded data.
- Preserve existing caller behavior apart from more complete reads.
- Cover the behavior with fake-socket tests, including a response split by more
  than the old idle window.

**Non-Goals:**
- No new protocol command families.
- No change to request encoding or frame construction.
- No live capture promotion or raw capture artifacts in git.

## Decisions

- **Shared helper:** add the receive implementation in the protocol package and
  have both existing callers delegate to it. This removes the divergence between
  wall-clock and monotonic timing without changing higher-level call sites.
- **Tail marker first:** accumulate chunks until `frames.TAIL_MARKER` appears in
  the buffer. Tail detection works across chunk boundaries because it searches
  the accumulated bytes, not just the latest chunk.
- **Bounded fallback:** keep an idle timeout only after at least one chunk is
  read and no tail marker is observed. A hard monotonic deadline remains the
  final bound for broken or tail-less streams.
- **Parser proof:** use a fake socket that yields chunk one, raises
  `socket.timeout` long enough to exceed the historical idle window, then yields
  chunk two with the tail. The resulting bytes must still parse through an
  existing value extractor.

## Risks / Trade-offs

- [Risk] Some responses may contain the tail marker bytes as data before the
  actual frame tail. Mitigation: retain the existing hard deadline and keep the
  change localized; add follow-up evidence if a corpus row proves embedded-tail
  ambiguity.
- [Risk] Tail-less responses could wait longer than before. Mitigation: the idle
  fallback remains and tests should cover tail-less completion.
- [Risk] Live cold-client behavior can still fail for non-transport causes.
  Mitigation: final verification records live read proof separately from the
  offline framing unit proof.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Protocol transport | `session.read_available`, `native_mutation._read_available`, shared receive helper | fake socket split response with tail in second chunk | offline unit test proving one complete frame and parser extraction | `tests/` plus `.artifacts/openspec/frame-aware-receive/2026-07-02/` if retained | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: embedded-tail payload ambiguity remains theoretical until corpus evidence says otherwise |
| QA/TestClient live read | `read_form_descriptor` / `read_list_grid` on Linux `vanessa_client` | optional live read pass after offline tests | live read command summary or provider-gap/runtime-gap diagnostic | `.artifacts/openspec/frame-aware-receive/2026-07-02/live-read/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Medium: lab contention or platform startup can block live evidence; offline receive contract remains covered |
| Runtime cleanup | no new process ownership or launch behavior | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | receive-only change does not launch or stop 1C processes | No residual risk; cleanup behavior is unchanged |
