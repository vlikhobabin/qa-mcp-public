# Design

## Context

The product host-agent already implements `registry-*` flags and the T4
bootstrap previously rendered them by constructing a scheduled task directly.
The supported installer renders the BSL flags but not registry inputs, so an
installer-driven G12 claim cannot be observed without first closing that
production-entrypoint gap.

## Decision

Add an all-or-nothing registry input set to the installer: URL, immutable user,
per-user token file, bridge-token file, advertised endpoint, heartbeat and TTL.
Validate URLs, files and positive durations before copying the artifact or
registering the task. Render the existing host-agent flags into the scheduled
task and keep solo mode unchanged when no registry input is provided.

Build a new source-bound bundle after the installer/test edit, stage the bundle
and installer on both T4 stations, run the same installer with only declared
station-specific user/IP/token inputs, and retain sanitized summaries. A new
immutable preflight captured before mutation is the cleanup oracle; cleanup
must restore the pre-run stopped/absent resources exactly.

## Safety

The operator explicitly authorized the two-station install. Generated tokens
and product credentials stay in mode-0600 ignored state and are never written
to evidence. Cleanup targets exact tasks, executable paths, token files,
firewall rules, PIDs and compose resources created by this run; it preserves
the pre-existing stopped legacy station-B task and binary.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | n/a_reason | residual_risk | provider_owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Supported installer plus current source-bound host-agent on Windows 10.0.22631 and 10.0.26200 | RED/GREEN installer contract; immutable preflight; identical bounded install on both stations; exact cleanup | source_preflight, runtime_apply_log, artifact manifest/SHA equality, sanitized station summaries, cleanup_evidence | `../.artifacts/openspec/windows-host-agent-current-bundle-two-station-installer-proof/20260714T170159Z-initial/` | required | — | Station and team-server availability are external; all mutations are exact-owned and cleanup-gated | qa-mcp + root T4 |
| Managed form / TestClient | — | — | — | — | N/A | This proof installs registration/BSL supervision and performs no TestClient/UI action | none | qa-mcp |
| BSL | BSL helper supervision process, not BSL source | Verify ready state, version, restart configuration and no visible helper window | runtime_apply_log, health summary, process/window probe | same evidence root | required | — | Cold helper warmup can approach the bounded 480-second timeout | qa-mcp |
| Metadata | — | — | — | — | N/A | No metadata source or runtime metadata behavior changes | none | qa-mcp |
| Role | — | — | — | — | N/A | No 1C role rights change | none | qa-mcp |
| Posting | — | — | — | — | N/A | No document posting or data mutation | none | qa-mcp |
| Report or DCS | — | — | — | — | N/A | No report surface | none | qa-mcp |
| Migration or compatibility | Two supported Windows builds | Run the same installer contract and verify exact current digest on both builds | two-station runtime summary and immutable cleanup comparison | same evidence root | required | — | No data migration; compatibility is runtime-observed on the two authorized hosts | qa-mcp |
