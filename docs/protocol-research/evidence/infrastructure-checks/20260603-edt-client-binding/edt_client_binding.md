# EDT Client Binding Evidence

Date: 2026-06-03.

## Scope

This note records the client-only EDT binding preflight for the qa-mcp protocol
lab. The manager infobase was not imported in this step.

## Inputs

- EDT workspace: `C:\1C_BASES\EDT\vanessa_qa`
- EDT project: `vanessa_client`
- Client infobase: `C:\1C_BASES\vanessa_client`
- EDT target id: `client`
- Role: `client`
- Access mode: `INFOBASE`
- Username/password: provided from the local ignored target env; not recorded

## Result

- `vanessa_client` access preflight succeeded through `ibcmd config generation-id`
  with explicit infobase credentials.
- `C:\1C_BASES\EDT\vanessa_qa` was created as an EDT workspace.
- Existing infobase import completed successfully.
- Imported project path:
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_client`
- Import operation id:
  `import-20260603T182357Z-cd59981f235f`
- Import summary path:
  `C:\1C_BASES\EDT\vanessa_qa\.runtime\.artifacts\infobase-import-operations\import-20260603T182357Z-cd59981f235f\summary.json`
- `list_projects` for the external workspace returned `vanessa_client`.
- Project-local Codex files were generated under
  `C:\1C_BASES\EDT\vanessa_qa`.
- Target context was registered in:
  `C:\1C_BASES\EDT\vanessa_qa\.edt-mcp\target-contexts.json`

Registered target:

```json
{
  "targetId": "client",
  "workspace": "C:\\1C_BASES\\EDT\\vanessa_qa",
  "project": "vanessa_client",
  "role": "client",
  "infobaseName": "vanessa_client",
  "infobaseConnection": "File=\"C:\\\\1C_BASES\\\\vanessa_client\";",
  "projectRoot": "C:\\1C_BASES\\EDT\\vanessa_qa\\vanessa_client"
}
```

## Current Limitations

- The active Codex MCP session was still running `edt-mcp` with
  `agent-default`, so admin tools were not visible in-session. The project
  `.mcp.json` and `.codex\config.toml` were updated to request
  `admin,agent-default` for the next MCP start.
- After checking the restarted session, the active MCP server still reported
  `requestedProfiles=["agent-default"]` because Codex was using
  `.codex\config.toml`, not only `.mcp.json`. A direct `edt-mcp` runtime check
  with `EDT_MCP_TOOL_PROFILES=admin,agent-default` listed project
  `vanessa_client` and configured target `client`.
- After updating `.codex\config.toml`, the next restarted MCP session reported
  `activeProfiles=["admin","agent-default"]` and exposed admin tools including
  `list_target_contexts`, `connect_existing_infobase_workspace` and
  `validate_project_infobase_binding`.
- That restarted session was still pointed at the repository workspace
  `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp`, so
  `list_target_contexts` correctly returned no targets for that active
  workspace. `.codex\config.toml` and `.mcp.json` were then updated so the
  next MCP start points `EDT_MCP_WORKSPACE`,
  `EDT_MCP_DURABLE_PROJECT_WORKSPACE`, runtime, artifact and temp roots at
  `C:\1C_BASES\EDT\vanessa_qa`.
- A subsequent Codex start reported `MCP startup incomplete (failed: edt-mcp)`.
  Manual `edt-mcp.cmd -PrintConfig` with the same environment succeeded and
  reported workspace `C:\1C_BASES\EDT\vanessa_qa`, profiles
  `admin,agent-default` and ready project Python. Two stale
  `edt-mcp.cmd -> powershell -> python -m edt_mcp.cli` process trees from
  failed startup attempts were stopped. `startup_timeout_sec=90` was added for
  `edt-mcp` in both `.codex\config.toml` and `.mcp.json` to avoid Codex
  declaring startup failed while the Windows wrapper is still initializing.
- After the next restart, `edt-mcp` started successfully with
  `activeProfiles=["admin","agent-default"]`, active workspace
  `C:\1C_BASES\EDT\vanessa_qa`, project `vanessa_client` and target
  `client`.
- `validate_project_infobase_binding(target_id="client")` reached a ready probe
  plugin/runtime, but returned `status=mismatched`: expected project
  `vanessa_client` and infobase `vanessa_client`, actual EDT linked state
  `not_linked`.
- `live-mcp` started and listed `client` and `manager` COM connections.
  `check_com_connection(connection_id="manager")` passed. `client` failed
  runtime COM check with invalid username/password because the live connection
  is configured without client credentials.
- `meta-mcp` started and `metadata_sources(operation="list")` returned ready
  status with zero registered sources.
- `validate_project_infobase_binding(target_id="client")` did not complete
  because probe plugin readiness attempted to rebuild
  `lab.edt.bslprobe_0.0.1.jar`, but the jar was busy. The import itself
  succeeded.
- Persisting EDT infobase access settings through the probe plugin also failed
  for the same readiness reason. Future plugin-backed mutations should re-run
  readiness after the busy EDT/plugin process is cleared.
- On 2026-06-04, after MCP restart, `get_infobase_access("vanessa_client")`
  showed EDT runtime access still persisted as `OS`. The session successfully
  updated it through `configure_infobase_access` to `Infobase` access with the
  local infobase user and empty password.
- Re-running `validate_project_infobase_binding(target_id="client")` after the
  access update still returned `status=mismatched`: expected project and
  infobase `vanessa_client`, actual linked state `not_linked`, association
  absent and `infobaseCount=0`.
- Source inspection found the supported repair primitive
  `associate_infobase(project, infobase)`, but that tool belongs to the
  `diagnostic` profile and is not visible in the current
  `admin,agent-default` MCP session.
- `.mcp.json` and `.codex\config.toml` were updated to request
  `admin,agent-default,diagnostic` for the next MCP start.
- After restart, `edt_capabilities(include_legacy=false)` reported
  `activeProfiles=["admin","agent-default","diagnostic"]` and exposed
  `associate_infobase`.
- `associate_infobase(project="vanessa_client", infobase="vanessa_client")`
  repaired the EDT association. The `afterState` reported `linked=true`,
  `defaultInfobase="vanessa_client"` and `deployAllowed=true`.
- The following `validate_project_infobase_binding(target_id="client")` still
  returned `status=mismatched`, although linked state was present. The response
  showed a provider normalization defect: `actual.infobase` contained the
  stringified structured infobase object instead of its `name`.
- A focused fix was applied in sibling provider checkout `edt-mcp` so target
  binding validation extracts the name from structured infobase payloads. The
  focused test command `python -m pytest edt-mcp\tests\test_target_contexts.py`
  passed with 11 tests.

## Next Step

After restarting Codex/MCP to load the `edt-mcp` provider fix, run:

1. `edt_capabilities` and confirm active profiles include `admin` and
   `diagnostic`.
2. `validate_project_infobase_binding(target_id="client")`.
3. If binding is matched, continue with controlled fixture processing authoring
   in `target_id=client`.

Then author the controlled read-only fixture data processor in
`target_id=client`.
