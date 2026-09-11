## MODIFIED Requirements

### Requirement: Host-agent executes only allowlisted local agent CLIs
The Windows host-agent SHALL expose `POST /agent/complete` as an authenticated sensitive endpoint that executes only allowlisted local model CLIs from semantic request fields. The endpoint MUST NOT accept or forward arbitrary argv, shell fragments, executable paths, prompt text in logs, or credential material from the request. The endpoint SHALL accept `timeout_seconds` as a JSON number whether encoded as an integer or decimal value, then normalize it through the host-agent timeout default, floor and maximum clamps before spawning a CLI.

#### Scenario: Authenticated Codex completion returns final text
- **WHEN** an authenticated request supplies `agent: "codex"`, a non-empty `prompt`, and a bounded `timeout_seconds`
- **THEN** the host-agent resolves the Codex CLI on the host, constructs the allowlisted Codex command internally, sends the prompt on stdin, reads the final output text from the host temporary output file, and returns `{ "ok": true, "text": "...", "response_id": "codex-cli" }`
- **AND** the prompt body and local CLI credentials are not written to logs or error details

#### Scenario: Authenticated Claude completion returns final text
- **WHEN** an authenticated request supplies `agent: "claude"`, a non-empty `prompt`, and a bounded `timeout_seconds`
- **THEN** the host-agent resolves the Claude CLI on the host, constructs the allowlisted Claude command internally, sends the prompt on stdin, strips one wrapping Markdown code fence when present, and returns `{ "ok": true, "text": "...", "response_id": "claude-cli" }`
- **AND** the prompt body and local CLI credentials are not written to logs or error details

#### Scenario: JSON float timeout is accepted
- **WHEN** an authenticated request supplies `timeout_seconds` as a decimal JSON number such as `300.0`
- **THEN** the host-agent decodes the request successfully, normalizes the timeout using the same clamp rules as an integer value, and proceeds to the allowlisted CLI dispatch path
- **AND** the request is not rejected as `invalid-json`

#### Scenario: Unknown agent is rejected before spawn
- **WHEN** an authenticated request supplies an `agent` value outside the host-agent allowlist
- **THEN** the endpoint returns a fail-closed response with `ok: false` and an `agent-not-allowed` error
- **AND** no process is spawned

#### Scenario: Missing or invalid token is rejected before prompt validation
- **WHEN** a request to `POST /agent/complete` omits `X-QA-MCP-Agent-Token` or supplies the wrong value
- **THEN** the endpoint returns the existing unauthorized response
- **AND** the request prompt is not validated, logged, or passed to any process

#### Scenario: Missing CLI fails closed for readiness
- **WHEN** an authenticated request selects an allowlisted agent whose CLI cannot be resolved on the host PATH
- **THEN** the endpoint returns `ok: false` with a bounded `cli-not-found` error suitable for readiness diagnostics
- **AND** no shell fallback or arbitrary executable path is attempted

#### Scenario: Timeout terminates the process group
- **WHEN** an authenticated request selects an allowlisted agent and the CLI exceeds the bounded timeout
- **THEN** the host-agent terminates the spawned process group where supported and returns `ok: false` with a bounded `timeout` error
- **AND** stderr detail is bounded and does not include the prompt body

#### Scenario: Authenticated health reports CLI availability
- **WHEN** an authenticated client calls `/health`
- **THEN** the response includes bounded Codex and Claude availability diagnostics based on host PATH lookup
- **AND** unauthenticated clients still cannot access detailed health through the sensitive endpoint boundary
