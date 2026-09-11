# CR-04 — Transport & framing robustness

## Status
4.done

## Order Index
4

## Owner
unassigned

## OpenSpec Stage
archived

## Change Set
- `frame-aware-receive` - `openspec/changes/archive/2026-07-02-frame-aware-receive/`
- `parser-truncation-guards` - `openspec/changes/archive/2026-07-02-parser-truncation-guards/`
- `socket-timeout-hygiene` - `openspec/changes/archive/2026-07-02-socket-timeout-hygiene/`

## Source
- Multi-agent code review 2026-07-02, findings C4, M5, m1, m3, m5, m6, m7, S7.
- Full report: `docs/code-review-2026-07-02.md`.

## Summary
The receive/transport layer infers frame boundaries from **idle timing** rather
than the protocol's own tail marker, so a client pause mid-response splits or
misattributes frames — the root fragility behind many "cold/warm client"
symptoms and behind truncation-triggered `IndexError`s in the parsers. This card
hardens the transport: real frame delimiting, guarded parsers, no socket/timeout
leaks, and a process-ownership guard on teardown. Some fixes are offline-testable
with a fake socket; full validation benefits from a live read pass.

## Problems (verified against code)

### C4 — Frame boundaries are timing-inferred, not protocol-delimited
`src/qa_mcp/protocol/session.py:50-69` (`read_available`) and
`src/qa_mcp/protocol/native_mutation.py:296-313` (`_read_available`): a "response"
is whatever arrives before an idle gap (0.15–0.6 s). The protocol **has** a tail
marker `66 53 b2 a6` (`frames.py:13`) but receive never uses it. If the client
pauses > the idle window mid-response (large form render, data load, model-B
cross-machine latency), the response is split and the tail is attributed to the
*next* frame. Per-response parsers (`read_field_value_near`,
`read_table_cell_value`, `extract_table_cell_value`) then miss values → spurious
`committed: false` / `None` cells.

### M5 — `read_list_grid_replay` truncates on adjacent-duplicate rows
`src/qa_mcp/protocol/native_write.py:1626-1627`: end-of-list is
`if all(v is None ...) or rowvals == prev: break`. Two adjacent rows with
identical values in the requested columns (common for a single non-unique column)
stop the sweep and silently drop the rest; a single all-timed-out row (see C4)
also reads as end-of-list. `row_count` gives no hint the stop was premature.

### m1 — `IndexError` on truncated value envelopes in the parsers
`src/qa_mcp/protocol/responses.py:231` (`_value_after_leaf`) and `:428-430`
(`_window_caption_after`): a blob ending exactly at the marker raises
`IndexError`, propagating out of `extract_form_field_values` /
`extract_testclient_windows` — the whole read tool errors instead of returning a
partial result. Truncated tails are exactly what C4 produces.

### m3 — `UnicodeEncodeError` on Cyrillic field names in responses parsers
`src/qa_mcp/protocol/responses.py:170`, `:204`: `field.encode("latin1")` raises
on a Cyrillic name (exposed via `assert_form_value` / `_read_field_value`). The
sibling `read_field_value_near` handles this with try/except.

### m5 / m6 / m7 — socket/timeout hygiene
- **m5:** `native_write.py:410-426` — `NativeWriteSession.__enter__` creates the
  socket first; an exception during the setup replay propagates out of
  `__enter__`, so `__exit__` never runs and the socket lingers until GC.
- **m6:** every exchange leaves the socket timeout at the tiny read idle value
  (0.15–0.25 s); a subsequent `sendall` of a multi-KB frame then runs under that
  timeout, and a legitimately slow send raises `socket.timeout` that
  `close_window` / `write_form_value` / `activate_window` misreport as protocol
  "divergence" (`native_write.py:2204-2207, 2500-2502`).
- **m7:** `session.read_available` computes its deadline on
  `datetime.now().timestamp()` (wall-clock); an NTP step mid-read distorts the
  window. The twin `native_mutation._read_available` already uses
  `time.monotonic()`.

### S7 — `stop_test_client(pid)` kills an arbitrary process group
`src/qa_mcp/protocol/lifecycle.py:620-635`: the stateless teardown `killpg`s
whatever process group owns the passed pid, with no ownership check (stale/recycled
pids included) — can take down an unrelated process tree owned by the server's user.

## Recommended remediation
- **C4:** make `read_available` frame-aware — read until the tail marker
  `66 53 b2 a6` is seen (or a hard deadline), instead of stopping on the first
  idle gap. Keep the idle gap only as a fallback for frames without a tail. Unify
  the two `read_available` implementations into one (fixes m7 for free by keeping
  the `monotonic()` version). This receive point should become the single home
  the future `ReplaySession` (CR-08) reuses — coordinate so CR-08 preserves it.
- **M5:** stop the sweep only on the all-`None` (empty) row or an explicit
  end-of-list marker, not on `rowvals == prev`; if a duplicate-based heuristic is
  kept, gate it behind "row read timed out" vs "row genuinely equal", and surface
  a `truncated: true` / `stop_reason` field so callers can tell.
- **m1/m3:** bounds-check before indexing in `responses.py` (return a partial/None
  instead of `IndexError`); wrap `field.encode("latin1")` in try/except and treat
  a non-latin1 field as "not addressable via this scanner" (return None), matching
  `read_field_value_near`.
- **m5:** wrap the setup replay in `__enter__` in try/except that closes the
  socket before re-raising.
- **m6:** restore a sane socket timeout before each `sendall` (or use a dedicated
  send timeout), and classify `socket.timeout` distinctly from protocol
  divergence in the error mapping.
- **S7:** before `killpg`, verify the pid is a qa-mcp-owned client — e.g.
  `/proc/<pid>/comm` matches `1cv8*` / `Xvfb`, or the pid matches a recorded
  owned-process handle; otherwise return a structured refusal.

## Acceptance
- A `FakeSocket` that delivers a response in two chunks with a > idle-window gap
  **between** them (tail marker in the second chunk) is read as **one** complete
  frame; the value parser extracts the value correctly — new test.
- `read_list_grid` over a list with two adjacent equal rows returns **all** rows
  (not truncated at the duplicate); when a row read times out the result carries
  an explicit `truncated`/`stop_reason`, not a silent short list — new test.
- Feeding truncated blobs to `extract_form_field_values` /
  `extract_testclient_windows` returns a partial/None result, never `IndexError`;
  a Cyrillic field name to the responses parsers returns None, never
  `UnicodeEncodeError` — new tests.
- `NativeWriteSession.__enter__` raising mid-setup leaves **no** open socket
  (assert via a fake socket whose `sendall`/`recv` raises) — new test.
- A slow-send simulation does not surface as "divergence"; `socket.timeout` maps
  to a distinct, truthful reason — new test.
- The two `read_available` implementations are one function using `monotonic()`.
- `stop_test_client` refuses a pid whose `/proc/<pid>/comm` is not an owned client
  — new test.
- `uv run pytest -q` green; a live read pass (`read_form_descriptor` /
  `read_list_grid` on the lab) still returns the same values (record in `## Result`).

## Change 1: `frame-aware-receive`

### Why
Idle-gap receive logic splits slow but valid TestClient responses before their
protocol tail marker arrives.

### Goal
Make native protocol receive frame-aware, shared and monotonic-timed.

### Scope
- Add a shared receive helper for native protocol sockets.
- Read until `TAIL_MARKER` or a hard monotonic deadline, with idle fallback only
  for tail-less buffers.
- Route both existing receive implementations through the helper.
- Add fake-socket tests for delayed-tail and tail-less responses.

### Acceptance
- A response split by more than the old idle window and completed by the tail
  marker is returned as one buffer.
- Existing value parsing extracts from that delayed-tail buffer.
- `session.read_available` and `native_mutation._read_available` share one
  implementation and do not use wall-clock deadlines.

### Depends On
- none

### Related
- `openspec/changes/frame-aware-receive/`

### Notes For `$openspec-ff-change`
- Capability: `qa-mcp-protocol-lab`.
- Verification matrix is recorded in `design.md` and `tasks.md`.

## Change 2: `parser-truncation-guards`

### Why
Truncated response envelopes and non-Latin field names can crash parser helpers,
and duplicate list rows can be silently dropped.

### Goal
Make parser and list-grid reads fail closed with partial results, `None` or
explicit stop metadata instead of exceptions or silent truncation.

### Scope
- Bounds-check value and window-caption parser indexing.
- Treat unsupported non-Latin field scanner input as no match.
- Remove adjacent duplicate rows as a list-grid end condition.
- Add truncation/stop metadata for timeout or empty-row stops.
- Add focused offline parser/list-grid tests.

### Acceptance
- Truncated blobs never raise `IndexError`.
- Cyrillic field-name scanner input never raises `UnicodeEncodeError`.
- Adjacent duplicate list rows are preserved.
- Timeout/empty-row list stops are distinguishable.

### Depends On
- `frame-aware-receive`

### Related
- `openspec/changes/parser-truncation-guards/`

### Notes For `$openspec-ff-change`
- Capability: `qa-mcp-protocol-lab`.
- Verification matrix is recorded in `design.md` and `tasks.md`.

## Change 3: `socket-timeout-hygiene`

### Why
Setup failures can leak sockets, send operations can inherit tiny read timeouts,
and pid teardown can target unrelated process groups.

### Goal
Harden native session lifecycle, send timeout classification and TestClient
process ownership checks.

### Scope
- Close setup-created sockets when `NativeWriteSession.__enter__` fails.
- Apply send-appropriate timeouts before outbound frames and restore receive
  behavior for response draining.
- Classify send `socket.timeout` distinctly from protocol divergence.
- Refuse `stop_test_client(pid)` for unowned or unrecognized processes.
- Add focused fake-socket and process-ownership tests.

### Acceptance
- Setup failure leaves no open fake socket.
- Slow sends do not surface as divergence.
- Unrelated or stale pids are refused before `killpg`.

### Depends On
- `parser-truncation-guards`

### Related
- `openspec/changes/socket-timeout-hygiene/`

### Notes For `$openspec-ff-change`
- Capability: `qa-mcp-protocol-lab`.
- Verification matrix is recorded in `design.md` and `tasks.md`.

## Verify
- `openspec validate frame-aware-receive --strict` - passed 2026-07-02.
- `openspec validate parser-truncation-guards --strict` - passed 2026-07-02.
- `openspec validate socket-timeout-hygiene --strict` - passed 2026-07-02.
- `uv run pytest -q tests/test_protocol_session.py` - 6 passed.
- `uv run pytest -q tests/test_form_value_parser.py tests/test_native_write.py` - 80 passed.
- `uv run pytest -q tests/test_native_write.py tests/test_lifecycle.py` - 85 passed.
- `uv run pytest -q` - 624 passed.
- `openspec validate qa-mcp-protocol-lab --strict` - passed 2026-07-02.
- `openspec validate --all` - 11 passed, 0 failed.
- `git diff --check -- openspec/changes/socket-timeout-hygiene openspec/specs/qa-mcp-protocol-lab/spec.md src tests` - passed.
- Live read regression on Linux `vanessa_client` passed 6/6 for the receive and parser/list-grid changes:
  `.artifacts/openspec/frame-aware-receive/2026-07-02/live-read/20260702T062256Z/report.json`,
  `.artifacts/openspec/parser-truncation-guards/2026-07-02/live-read/20260702T063006Z/report.json`.

## Related
- `docs/code-review-2026-07-02.md` (C4, M5, m1, m3, m5, m6, m7, S7)
- **CR-08** (ReplaySession) must preserve the frame-aware receive introduced here.

## Result
Delivered. Native protocol receive now waits for frame tail markers through a
shared monotonic helper, response parsers tolerate truncated/unsupported scanner
input, list-grid reads preserve adjacent duplicate rows with explicit stop
metadata, native write setup/sends have safer timeout cleanup, and stateless
TestClient teardown refuses unrecognized process groups.

## Next
- None.

## Log
- 2026-07-02 card created from the code-review report (C4, M5, m1, m3, m5, m6, m7, S7).
- 2026-07-02 `$opsx-ff` created and validated `frame-aware-receive`,
  `parser-truncation-guards` and `socket-timeout-hygiene`.
- 2026-07-02 `$opsx-do` started; card moved to in-progress.
- 2026-07-02 `$opsx-do` implemented, verified, synced and archived all three
  changes; card moved to done.
- 2026-07-02 `$opsx-pub` created initial publish commit `2a80dae`.
