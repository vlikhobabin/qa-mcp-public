# Python Protocol Package

`qa_mcp.protocol` is the package boundary for reusable direct TestClient
protocol code. It is promoted from `tools/protocol-research` only after the
behavior is covered by compact evidence and offline tests.

## Read-Only Contract

The package exposes read-only operation descriptors before exposing wider
runtime APIs. Descriptors keep the evidence state visible:

- `active-window-context` - accepted mapping.
- `active-form-context` - accepted mapping.
- `initial-ui` - bootstrap context, partial as a standalone mapping.
- `form-summary` - supported probe path, partial as a standalone mapping.
- `form-element-details` - useful direct probe path, still
  `incomplete_hash`.
- `typed-input-field-readonly` - useful direct probe path, still
  `incomplete_hash`.

Accepted descriptors link compact accepted-mapping evidence under
`docs/protocol-research/evidence/accepted-mappings/`. Unresolved descriptors
carry a concrete reason so package callers do not treat direct probe success
as accepted wire evidence.

The 2026-06-03 read-only element hash resolution keeps both element rows
non-accepted. `form-element-details` now has extracted reviewed request-hash
evidence from `20260602-172319`, but the current repeated comparison inputs
still lack request bytes and hashes. `typed-input-field-readonly` has the same
missing-frame limitation plus an operation-join caveat because it shares the
element-detail request shape. The published resolution is under
`docs/protocol-research/evidence/readonly-element-hash-resolution/`.

The package remains read-only. Clicks, text input, command execution and other
state-changing UI actions belong to later safe-action cards with separate
recovery evidence.

The `20260603-134132` safe-action classification did not promote an
`activate_window` descriptor. That row remains `pending` because reviewed
action-frame evidence, a normalized hash and replay or direct Python-manager
proof are not available.

## Frame And Template Primitives

`qa_mcp.protocol` owns deterministic byte-level helpers for:

- TestManager/TestClient direction constants;
- tail-marker stripping and payload summaries;
- UTF-8 manager header parsing and ACK GUID extraction;
- manager header GUID adaptation;
- captured bootstrap loading from `traffic.jsonl`;
- manager-frame template rendering with replacement metadata.

These primitives are offline-testable. They do not open sockets, start 1C
processes or require ignored runtime captures unless an operator explicitly
supplies a local capture path.

## Read-Only Session API

`TestClientSession` is the package entrypoint for direct TCP communication
with an already running `/TESTCLIENT` listener. The session owns only its
socket and closes only that socket during cleanup.

Package query methods are intentionally read-only:

- `get_initial_ui_context`
- `get_active_window_context`
- `get_active_form_context`
- `get_form_summary`
- `get_form_element_details`

Query results include the descriptor evidence status. Current accepted results
are limited to active window and active form context. Form summary and element
details remain useful probe paths, but their result metadata stays partial or
`incomplete_hash` until repeated reviewed request-hash evidence is accepted.

## Research Tool Wrappers

`tools/protocol-research/python_manager_client.py` is now a compatibility
facade over `qa_mcp.protocol`. Research scripts can keep importing the old
module name while package code owns the reusable primitives and read-only
session API.

`python_manager_probe.py` remains the Windows-native probe CLI. It supports the
package-backed read-only query ids:

- `initial-ui`
- `active-window-context`
- `active-form-context`
- `form-summary`
- `form-element-details`

The CLI still writes raw sent/received payloads only to the requested output
directory, which should be under ignored `runtime/protocol-research/` unless a
later card creates compact reviewed evidence.
