## Context

`run_doctor` currently has a hard-coded short timeout default. Root-generated
project profiles can provide real-base COM timeout values, but qa-mcp has no
central setting to consume that value for doctor checks.

## Goals / Non-Goals

**Goals:**
- Parse `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS` in `Settings`.
- Use the parsed timeout when no CLI/tool timeout argument is supplied.
- Keep explicit timeout arguments as overrides.
- Record the effective numeric timeout in the COM doctor check data.

**Non-Goals:**
- Change COM host-agent protocol payloads beyond the timeout value already sent.
- Execute live COM during offline tests.
- Add new protocol capture evidence or alter TestClient replay behavior.

## Decisions

- Store the setting in `Settings` with the existing short default. This keeps
  all `QA_MCP_*` parsing centralized and preserves behavior when the env key is
  absent.
- Change doctor entry points to treat omitted timeout as `None`, then resolve
  the effective timeout after settings are parsed. This is the only way to let
  environment configuration act as the default while preserving explicit
  override behavior.
- Keep the COM check data numeric and bounded to avoid leaking infobase
  credentials or host-agent tokens.

## Risks / Trade-offs

- [Risk] Existing callers may assume the MCP tool schema default is `3.0`.
  -> Mitigation: absent env still resolves to the same effective default.
- [Risk] A malformed timeout env should not crash discovery-only doctor paths.
  -> Mitigation: parse with the existing float parser path and cover normal
  numeric behavior in tests.

## Migration Plan

No data migration is required. Deployments can set
`QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS`; omitted environments keep the previous
effective default.

## Open Questions

None.
