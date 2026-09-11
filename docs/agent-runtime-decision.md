# `agent_runtime` capabilities — decision record (card 98 change 4)

**Status:** DECISION (no immediate code). **Date:** 2026-06-20. Folds card 77 into card 98 change 4.

## What `agent_runtime` is

`agent_runtime` = the capabilities a **test manager** exposes to scenario authors — session lifecycle and
manager-side config/control — as distinct from the **UI-action** protocol members (Click / Activate /
ExecuteChoice / SetEditText …) that the capture-free engine decodes and replays. The UI-action members are
in-scope for protocol decoding (and the bulk are shipped as MCP tools); the `agent_runtime` members are the
manager's *own* API surface. Some are manager-local; some touch the wire (handshake, file-dialog seeding,
UI-action recording).

**Coverage accounting:** the protocol-inventory coverage % does NOT count these members — they are not UI-action
commands to decode. But a "100% Vanessa replacement" must offer equivalents *when a scenario needs them*.

## The 11 `agent_runtime` members — local vs wire + qa_mcp status

| Member | Local / wire | qa_mcp status | Build priority |
| --- | --- | --- | --- |
| `TestedApplication.Connect` | **wire** (TCP + handshake) | ✅ DONE — `session.open_and_bootstrap` (synthesized handshake) | have it |
| `TestedApplication.Disconnect` | **wire** (teardown) | ✅ DONE — socket close / `stop_test_client` | have it |
| `SetMaxActionExecutionTime` | manager-local timeout | partial — replay has read/idle timeouts; no per-action setter | low — add a knob when needed |
| `StartUILogRecording` | **wire** (client records UI actions) | none | low — only if a scenario records user-action journals |
| `FinishUILogRecording` | **wire** (returns recorded-actions XML) | none | low — pairs with Start |
| `PauseUILogRecording` | **wire** | none | low |
| `ResumeUILogRecording` | **wire** | none | low |
| `CancelUILogRecording` | **wire** | none | low |
| `ClearAccumulatedPerformanceIndicators` | client perf reset | none | low — perf metrics, nice-to-have |
| `SetFileDialogResult` | **wire** (pre-seeds a client file-dialog result) | none | **medium** — file-dialog tests block without it |
| `ClearFileDialogResult` | **wire** (clears the seeded result) | none | medium — pairs with Set |

(The 3 remaining `read_only` uncovered — `WaitForCondition`, `TestedFormField/Decoration.GetObject` — are a
separate concern: `WaitForCondition` polls a manager-side predicate (qa_mcp has `wait_for_form_value`); the
`GetObject` pair are typed child accessors covered by the existing find/get-by-name paths. Not tracked here.)

## What qa_mcp already provides around this surface (2026-06-20)

The card-98 change-2 tool-surface parity added the **read/state** side that scenario authors reach for —
`get_state`, `get_test_results`, `infobase_info`, `get_window_list`, `get_window_list_testclient` — plus
`launch_test_client` / `stop_test_client` / `test_client_status` for the Connect/Disconnect lifecycle. These are
distinct from the 11 control/config members above (which remain build-on-demand).

## Decision

- The 11 `agent_runtime` members are an **accepted non-scope of protocol-decoding coverage** and a **deferred
  scope of the Vanessa replacement** (Python-manager features).
- `Connect` / `Disconnect` are implemented (handshake synthesis + teardown).
- The rest are built **on demand** — when a real scenario needs file-dialog seeding (medium), UI-action
  recording, perf metrics, or a per-action timeout — **not** for a coverage number.
- **First likely build-out:** `SetFileDialogResult` / `ClearFileDialogResult` (medium) when a file-dialog test
  appears (otherwise such a test blocks on the native OS file dialog).

## How to build one when needed

Follow the engine's productize pattern: decode the member's wire command from a genuine-manager capture
(`SetFileDialogResult` pre-seeds the result before the action that opens the dialog), add a
`derive_<member>` + `<member>` replay (block-retarget or full-stream + GuidRebinder), an MCP tool, a unit test,
and a `<member>_probe.py` / `run_<member>_test.sh` live-verify — then reference this record. Manager-local
members (per-action timeout) are just an engine knob, no capture.
