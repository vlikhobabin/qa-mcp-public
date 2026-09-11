# Live Python-Manager Probe Attempt (Warehouse toggle)

First live attempt to drive the warehouse `НеИспользовать` write from the
**Python manager** instead of the Vanessa manager, replaying the captured
manager command sequence through the recording proxy against a freshly launched
TestClient (no Vanessa manager in the loop).

Orchestration: launch TestClient (`/TESTCLIENT` on `vanessa_client`) + proxy
(15382 → 15381), then `replay_probe.py` replays the
`mut-warehouse-donotuse-20260610` manager frames with
`--adapt-frame4-guid --adapt-ui-path-guids --adapt-managed-form-guid
--adapt-binary-guid-through 861 --stop-on-no-response`.

## Result: harness works, flow diverges at frame 2

| Step | Outcome |
| --- | --- |
| connect through proxy | ok |
| `initial_read` | **exact_match** (5 B) — fresh client initial frame matches the captured one |
| manager frame 1 → response | **exact_match** (210 B) — first exchange reproduced byte-for-byte |
| manager frame 2 | no response → stopped (`--stop-on-no-response`) |

The **live Python-manager probe harness works end to end** (connect, handshake,
send, receive through the proxy) and the **first command exchange reproduces
byte-exactly against a fresh TestClient**. The full 861-frame navigation→write
flow then diverges at frame 2.

No mutation was executed (1 command exchanged, far before any write); demo data
was untouched; no accepted mapping is produced. `TestedFormButton.Click` stays
`candidate`.

## Why it diverges and what it needs

The captured sequence was driven by Vanessa via high-level steps; its 861
manager frames carry per-session UI-path GUIDs (`SecondaryFrame`,
`ManagedForm`) assigned by the client at runtime during navigation. The
read-corpus adaptation flags in `replay_probe.py` are tuned for the short
read-bootstrap and do not yet learn-and-substitute the navigation GUIDs of this
mutation flow past the first frames.

Concrete next step (one of):

1. Extend the replay adaptation to **learn live `SecondaryFrame`/`ManagedForm`
   GUIDs from each response and substitute them into subsequent commands**
   across the full nav→write flow (generalize `adapt_ui_path_guids`); or
2. Add **native navigation + write operations** to the Python manager
   (`qa_mcp.protocol`) that reach the warehouse card from the initial state and
   then send the decoded write template
   (`render_write_frame`), rather than replaying 861 captured frames verbatim.

Both are unblocked by the decoded write template and the `fully_stable`
normalizer; the harness and the first-frame byte-exact reproduction prove the
live path is viable.

Raw probe streams stay under ignored `runtime/protocol-research/captures/`.
