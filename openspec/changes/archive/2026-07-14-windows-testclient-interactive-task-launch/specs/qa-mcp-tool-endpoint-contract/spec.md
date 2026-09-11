## ADDED Requirements

### Requirement: Remote TestClient launch reports the durable interactive mechanism

The remote `launch_test_client` result SHALL report bounded launch-context
metadata identifying the verified host-agent session mechanism while preserving the
existing alive/listening/readiness and early-exit classifications.

#### Scenario: Interactive host-agent session reaches readiness

- **WHEN** the verified active-session host-agent yields a live PID and the requested TPort remains
  listening through the readiness dwell
- **THEN** the result reports `launch_context.method` as
  `interactive_task_shell_broker`, `alive:true`, `listening:true` and
  `readiness:"ready"`
- **AND** it does not expose command lines, credentials or token handles.

#### Scenario: Interactive child exits early

- **WHEN** the host-agent starts 1cv8 but that PID exits before TPort readiness
- **THEN** the existing `testclient-exited-early` result remains fail-loud
- **AND** the result identifies the interactive host-agent-session mechanism.

### Requirement: Remote TestClient launch selects the exact QA platform build

The remote launch contract SHALL carry the exact four-component QA platform
version to the Windows host-agent, which SHALL resolve 1cv8 only from that
catalog version and SHALL NOT silently select a newer installed build.

#### Scenario: Requested platform is installed

- **WHEN** the provider requests `8.3.27.2130` and the station also contains a
  newer platform build
- **THEN** the host-agent launches 1cv8 from the `8.3.27.2130` catalog directory
- **AND** reports that resolved version in bounded launch metadata.

#### Scenario: Requested platform is invalid or absent

- **WHEN** `platform_version` is not exactly four numeric components or that
  exact catalog version has no resolved 1cv8
- **THEN** launch fails before process creation with
  `invalid-platform-version` or `platform-version-not-found`
- **AND** it does not fall back to a different installed build.
