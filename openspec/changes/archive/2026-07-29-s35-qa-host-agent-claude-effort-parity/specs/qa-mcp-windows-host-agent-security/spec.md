## ADDED Requirements

### Requirement: Host-agent preserves agent CLI reasoning effort

The Windows host-agent SHALL preserve the authenticated `/agent/complete` `reasoning_effort` semantic request field for every selected allowlisted agent that supports effort. Codex requests MUST render the value through Codex configuration, Claude requests MUST render the value through the Claude CLI `--effort` flag, and the endpoint MUST NOT silently drop a requested effort while returning a successful completion.

#### Scenario: Codex completion forwards reasoning effort

- **WHEN** an authenticated `/agent/complete` request supplies `agent: "codex"`
  and a non-empty `reasoning_effort`
- **THEN** the host-agent renders the allowlisted Codex command with the matching
  `model_reasoning_effort` configuration
- **AND** the prompt body and credential material are not written to argv, logs
  or error details

#### Scenario: Claude completion forwards reasoning effort

- **WHEN** an authenticated `/agent/complete` request supplies `agent: "claude"`
  and a non-empty `reasoning_effort`
- **THEN** the host-agent renders the allowlisted Claude command with
  `--effort <level>`
- **AND** the prompt body and credential material are not written to argv, logs
  or error details

#### Scenario: Unsupported effort fails closed

- **WHEN** the selected allowlisted agent or installed CLI cannot honor the
  requested `reasoning_effort`
- **THEN** `/agent/complete` returns `ok: false` with a bounded typed diagnostic
  such as `agent-effort-not-supported`
- **AND** no response text is returned as if the requested profile had been used

### Requirement: Host-agent agent selection remains explicit

The Windows host-agent SHALL execute only the `agent` explicitly selected by the authenticated `/agent/complete` request and MUST NOT fall back to another installed agent CLI when the selected agent is missing, unsupported or fails.

#### Scenario: Missing selected Claude does not fallback to Codex

- **WHEN** an authenticated `/agent/complete` request selects `agent: "claude"`
  but Claude CLI is unavailable while Codex CLI is available
- **THEN** the endpoint returns a bounded `cli-not-found` or readiness error for
  Claude
- **AND** it does not spawn Codex

#### Scenario: Missing selected Codex does not fallback to Claude

- **WHEN** an authenticated `/agent/complete` request selects `agent: "codex"`
  but Codex CLI is unavailable while Claude CLI is available
- **THEN** the endpoint returns a bounded `cli-not-found` or readiness error for
  Codex
- **AND** it does not spawn Claude

### Requirement: Agent completion reports bounded effective profile metadata

The authenticated `/agent/complete` endpoint SHALL return or retain bounded non-secret effective profile metadata for readiness consumers, including selected agent, response id, model when supplied, reasoning effort when supplied and normalized timeout. The metadata MUST NOT include prompt text, host-agent token values, local CLI credential paths, raw stderr beyond existing bounded diagnostics, or caller-supplied argv.

#### Scenario: Successful completion identifies effective profile

- **WHEN** `/agent/complete` returns `ok: true` for Codex or Claude
- **THEN** the response or retained bounded diagnostic identifies the selected
  agent, response id, supplied model, supplied reasoning effort and normalized
  timeout
- **AND** no prompt text or credential material is included

#### Scenario: Failed completion still identifies selected profile safely

- **WHEN** `/agent/complete` fails closed after authentication and request
  validation
- **THEN** the bounded failure diagnostic identifies the selected agent and
  non-secret requested profile fields needed for readiness triage
- **AND** it does not include prompt text, token values or raw CLI credential
  paths
