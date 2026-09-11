# Python-Manager Mutation Probe — ACCEPTED (Warehouse toggle)

The Python manager (no Vanessa manager in the loop) drove the real warehouse
`НеИспользовать` write end to end against a live TestClient, and its write
exchange matches the Vanessa reference after normalization. This is the first
**accepted** mutation protocol mapping in qa-mcp.

## What was run

`adaptive_replay_probe.py` replays the captured 861 manager command frames of
`mut-warehouse-donotuse-20260610` to a freshly launched TestClient through the
recording proxy. It **learns the live per-session GUIDs by first-appearance
order** and substitutes them (ASCII, UTF-16LE and little-endian UUID forms) into
every subsequent command — generalizing the per-kind `adapt_ui_path_guids`.

## Result: full flow, zero divergence

| Metric | Value |
| --- | --- |
| manager frames replayed | 861 / 861 |
| exchanges with a live response | **861 / 861** |
| diverged at | **none** (`diverged_at_send_index: null`) |
| live GUIDs learned and rebound | 9 |
| probe frames captured | 1723 (861 manager + 862 client) — same shape as the reference |

The earlier `replay_probe.py` attempt stopped at frame 2 (read-flow adaptation
did not rebind the navigation GUIDs). The generalized learn-and-substitute
adapter carries the whole navigation → write → recovery flow.

## Acceptance: write exchange matches the reference

`compare_probe_reference.py --mode probe-ordinal --phase action_write` selects
the reference's action-write frames by ordinal, pulls the same positions from
the Python-manager probe capture, normalizes both and compares
(`python_manager_acceptance.json`):

| Direction | Reference hash | Probe hash | Match |
| --- | --- | --- | --- |
| `manager_to_client` | `ad7752e69dae9f8b1d7b…` | `ad7752e69dae9f8b1d7b…` | ✅ |
| `client_to_manager` | `37f5e98fc0b288cd37bf…` | `37f5e98fc0b288cd37bf…` | ✅ |

Verdict: **`accepted`**. The Python-manager-driven write exchange is
byte-identical to the Vanessa-driven reference after dynamic-field normalization.

## Proof chain (full)

1. Real DB-confirmed mutation + recovery via Vanessa (`Нет`→`Да`→`Нет`).
2. Action-write frames isolated by phase timeline.
3. Two reference captures `fully_stable` (byte-identical normalized hash).
4. Python-manager probe replays the full 861-frame flow live, zero divergence.
5. Probe action-write normalized hash matches the reference → `accepted`.

`TestedFormButton.Click` is promoted to `accepted_reviewed` in
`mutation-evidence-map.json`; the scope tracker now shows 1/9 mutation members
confirmed (the project's first `accepted_reviewed` member).

## Honest scope

Acceptance rests on the wire-level normalized-hash match of the write exchange
(direct Python-manager probe), which is the project's accepted criterion. The
probe replays captured command frames with live GUID rebinding; native
manager-side navigation operations (reaching the card from the initial state
without replaying 861 frames) remain the follow-up (plan step 2), now de-risked
by this end-to-end success.

Raw probe streams stay under ignored `runtime/protocol-research/captures/`.
