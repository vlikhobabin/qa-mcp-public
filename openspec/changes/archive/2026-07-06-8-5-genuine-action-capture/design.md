## Context

P2 (card 115) re-captures the full 8.5 corpus. Before that scale-up, the capture
*path* must be proven on 8.5 with a single action, because two things are unknown:
(1) whether the Vanessa TestManager — the 8.3 genuine-action driver — runs on 8.5,
and (2) whether the native `tcpdump`-on-`lo` path is needed instead. This change
resolves that and yields the first 8.5 `traffic.jsonl`.

## Decisions

- **One action, apples-to-apples with 8.3.** Capture the same action the 8.3
  corpus recorded so P2's 8.5↔8.3 diff (the "do we need code?" question) compares
  like with like.
- **Path preference: Vanessa-on-8.5 first, native fallback.** Reusing the Vanessa
  TestManager keeps the driver identical to 8.3; the native `tcpdump` path is the
  fallback if Vanessa does not run on 8.5.
- **Checkpoint boundary.** This change carries the live capture risk and is the
  planned `$opsx-deliver` pause point — the contour change lands first, this runs
  after operator review.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason / residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient runtime | open `lTestClient` fixture form on 8.5 | live form open under Xvfb | rendered fixture-form screenshot | `docs/protocol-research/evidence/<8-5-capture-run>/` | planned | qa-mcp | needs the capture driver decision (task 1) |
| Protocol capture | drive one action → clean pcap → `traffic.jsonl` | tcpdump/driver run + `pcap_to_traffic.py` | sample 8.5 `traffic.jsonl` that parses | `docs/protocol-research/evidence/<8-5-capture-run>/` | planned | qa-mcp | Vanessa-on-8.5 unknown; native fallback risk |
| Capture-path decision | Vanessa-on-8.5 vs native | recorded decision | decision note for P2 | this change's evidence + memory | planned | qa-mcp | — |

No `src/` code changes (capture is tooling/runtime). The 8.3 contour, the
offline suite and the bundled 8.3 assets are unaffected.
