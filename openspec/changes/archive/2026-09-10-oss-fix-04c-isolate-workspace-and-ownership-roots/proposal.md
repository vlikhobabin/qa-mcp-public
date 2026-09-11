## Why

On `1046b9f`, three real factories with distinct or explicitly empty root settings
all resolve process-environment workspace/ownership roots. `_repo_root` and
`lifecycle._ownership_root` independently reconstruct Settings from env; marker
creation additionally follows launch out_dir while later lookup follows a root.
FIX-04B already supplies the configuration scope required to correct this family.

## What Changes

- Resolve composed workspace and ownership roots from active application Settings,
  keeping explicit absence separate from legacy environment fallback.
- Make composed owned-launch output/marker placement and later discovery agree,
  including an explicit ownership root distinct from the workspace.
- Preserve separately admitted bound evidence-root/retention authority, exact
  process identity and foreign-marker refusal.
- Prove real factory consumers, fake launch/stop ownership, env drift and context
  restoration with temporary files and fake process/native boundaries.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `qa-mcp-runtime-configuration`: application-owned workspace and ownership roots, coherent marker lifecycle and legacy precedence.

## Impact

`src/qa_mcp/mcp_server.py`, `src/qa_mcp/protocol/lifecycle.py`, affected tests and
consumer documentation. Reuse the existing config accessor without a new service.
No wire, dependency, retention TTL, observation, live or ChangeRail changes.
