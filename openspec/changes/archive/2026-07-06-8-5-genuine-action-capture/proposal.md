## Why

With the 8.5 lab contour standing (change `8-5-fixture-lab-contour`), the P2
re-capture needs a **working capture path on 8.5**. On 8.3 the genuine corpus was
recorded with the `genuine-action-capture-recipe`: a `tcpdump -i lo` over the
client TPort range while a driver (the Vanessa TestManager, or a native driver)
opens the fixture form and performs an action, then `pcap_to_traffic.py` converts
the pcap to `traffic.jsonl`. That recipe must be re-established on 8.5 — and it is
unknown whether the Vanessa TestManager runs on 8.5 or whether the native path is
required. This change makes that determination and proves the pipeline by
producing the **first genuine 8.5 `traffic.jsonl`**.

## What Changes

- **Decide the 8.5 capture path:** test whether the Vanessa TestManager runs on
  8.5 (reuse the genuine-action recipe), else fall back to the native path
  (`tcpdump -i lo` over the client TPort range + a native driver) — and record
  which path the 8.5 contour uses.
- **Open the `lTestClient` fixture form** on the 8.5 client and drive one genuine
  action against it (the action the 8.3 corpus also captured, so the 8.5↔8.3 diff
  in P2 is apples-to-apples).
- **Capture a clean pcap** of that single action and convert it via
  `tools/protocol-research/pcap_to_traffic.py` to a `traffic.jsonl`.
- **Output:** one sample 8.5 `traffic.jsonl` (+ the rendered fixture-form
  screenshot) proving the capture pipeline works on 8.5 — the substrate P2 then
  scales to the full corpus (handshake + frame templates + the 13 action/foreground
  captures).

## Capabilities

### New Capabilities
<!-- none — this extends the existing protocol-lab capability -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: the genuine-action capture pipeline (drive a fixture-form
  action → clean pcap → `traffic.jsonl`) is **proven on the 8.5 contour**, with
  the chosen capture path recorded, producing the first 8.5 traffic sample for the
  P2 re-capture.

## Impact

- Tooling/runtime: `tools/protocol-research/` (`capture_session.sh`,
  `pcap_to_traffic.py`, the native driver probes); the 8.5 lab IB
  `/opt/1c-dev/vanessa_client_85/`; optionally a Vanessa TestManager on 8.5.
- Evidence: a sample 8.5 `traffic.jsonl` + the rendered fixture-form screenshot
  under `docs/protocol-research/evidence/` (gitignored runtime evidence).
- No package `src/` code changes (capture is tooling/runtime); the 8.3 contour and
  the offline suite are unaffected.
- **Card-size note:** this change carries the live capture risk (Vanessa-on-8.5
  compatibility, `tcpdump` on `lo`, fixture-form open). It is the planned
  `$opsx-deliver` checkpoint boundary — the contour change lands first and this
  capture change runs after operator review.
