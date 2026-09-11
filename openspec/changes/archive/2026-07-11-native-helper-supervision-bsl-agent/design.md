## Context

bsl-mcp delivered `ai1c.bsl-agent-workstation-supervision.v1` in `config/bsl-agent-workstation-contract.v1.json`: `bsl-agent.exe workstation serve`, fixed CLI/env precedence, loopback protocol `ai1c.bsl-agent-workstation-http.v1`, `/health`, `/v1/status`, `/v1/diagnostics`, `/v1/resync`, and owned-process stop with a ten-second graceful window. qa-mcp must consume this contract without modifying bsl-mcp.

## Goals / Non-Goals

**Goals:**
- supervise one configured local helper, probe readiness, restart after exit with backoff, and stop only that owned process;
- expose bounded lifecycle/version/restart state in host-agent health and `qa_mcp_doctor`;
- proxy authenticated diagnostics and resync to the loopback-only service;
- preserve the unconfigured host-agent path.

**Non-Goals:**
- Windows build/package or analyzer workspace implementation;
- representative large-config sizing;
- BSL source mutation, live 1C runtime, or TestClient protocol changes.

## Decisions

1. **Consume the published v1 contract literally.** The supervisor renders only the fixed command and allowlisted flags, accepts only loopback listen addresses, probes the published endpoints, and records the protocol/version returned by the helper.
2. **Own one process generation at a time.** The supervisor configures a new process group, waits for exit, increments restart count only for replacement launches, applies configured backoff, and kills only the owned process/group after the graceful stop window.
3. **Keep proxy routes narrow.** `/bsl/diagnostics` and `/bsl/resync` are protected by the existing host-agent token/origin policy, target only the configured loopback base URL, use fixed upstream paths/methods, bound bodies/responses, and do not accept an arbitrary URL or executable.
4. **Treat helper state as optional health detail.** Disabled is healthy for solo/non-W-B installs. Configured-but-not-ready is a distinct doctor failure; state/version/restart count never includes workspace or syntax-helper paths.
5. **Use fake helper processes offline.** Go tests launch an owned local helper fixture, observe readiness, kill/restart, route diagnostics, and stop it. Replacement launch is bounded by the configured backoff plus 100 ms process-reaping/scheduler tolerance, kept below two backoff intervals; readiness is checked separately. Pytest covers doctor interpretation. Real Windows control-event and local bsl-agent behavior remain provider gaps.

## Risks / Trade-offs

- Windows console-control semantics differ from Linux -> isolate platform signaling and retain a Windows provider gap.
- Rapid crash loops can consume resources -> bounded configurable backoff and a single owned generation.
- Proxying analyzer output can expose source-derived diagnostics -> bound response size and retain no raw response in central evidence.

## Migration Plan

Unconfigured installs report `bsl_agent.configured=false` and spawn nothing. W-B installs add the binary/workspace and optional contract paths. Removing the binary/workspace configuration returns to the prior host-agent behavior.

## Open Questions

None. Decision-freeze #5 and the delivered bsl-mcp v1 contract are not reopened.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | n/a_reason | residual_risk | provider_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | host-agent consumption of the workstation BSL supervision contract | fake helper launch/health/diagnostics/resync/crash/bounded replacement launch/stop suite plus contract-shape test | source_preflight, bsl_diagnostics, scenario_log | `.artifacts/openspec/native-helper-supervision-bsl-agent/2026-07-11-cycle2/offline-verification.txt` | required |  |  | `/opt/ai-dev-suite-for-1c/qa-mcp` |
| Delivery or runtime apply | real Windows helper process and local analyzer round-trip | supervised Windows launch, control-event stop, crash restart and diagnostic request | runtime_apply_log, bsl_diagnostics, scenario_log | `.artifacts/openspec/native-helper-supervision-bsl-agent/2026-07-11/windows-stand/` | blocked |  | Windows process-control and real workspace diagnostics remain unproved offline | `/opt/ai-dev-suite-for-1c/qa-mcp` |

### Provider Gaps

| provider_id | owner_path | matrix_row | missing_capability | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | real Windows helper process and local analyzer round-trip | supervised Windows control-event and real workstation bsl-agent run are outside this offline run | runtime_apply_log, bsl_diagnostics, scenario_log | Windows process-control and real workspace diagnostics remain `unverifiable` | verify lifecycle, bounded replacement launch, and routes with an owned fake helper process; run the real pair on the supervised stand | `openspec/board/3.inprogress/team-host-agent-self-registration-and-bsl-supervision.md` | `.artifacts/openspec/native-helper-supervision-bsl-agent/2026-07-11/provider-gap-windows-bsl-agent.md` |
