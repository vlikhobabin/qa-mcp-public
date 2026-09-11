# Reconcile remaining retired-provider references

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Suite consolidation phase-2 pass (2026-06-24, root coordination).

## Summary
2026-07-06 reconciliation completed. Active provider/profile and protocol-lab
documentation no longer treats `edt-mcp` or `vanessa-mcp` as an active provider;
legitimate protocol-research history and dated evidence were preserved.

## Current Triage (2026-07-06)

Active MCP profiles are clean: `.mcp.json` and `.codex/config.toml` do not wire
`edt-mcp` or `vanessa-mcp`. Active docs/specs have been updated:

- `AGENTS.md` now lists the current project-local provider entries and explicitly
  excludes `edt-mcp` / `vanessa-mcp` as active providers.
- `openspec/specs/qa-mcp-protocol-lab/spec.md`,
  `docs/protocol-research/methodology.md`,
  `docs/protocol-research/corpus-evidence-contract.md` and
  `docs/protocol-research/semantic-source-inventory.md` now point at the current
  `config-mcp` / `meta-mcp` / `bsl-mcp` / `admin-mcp` / `live-mcp` support stack.
- `.ai1c/profile-windows-backup-20260612T092306Z/*` contains historical Windows
  profile backups with `edt-mcp`/`vanessa-mcp`; keep or move only as historical
  backup evidence, never as an active profile.

## Keep (legitimate — do NOT remove)
- Vanessa **protocol research** under `docs/protocol-research/` and
  `tools/protocol-research/` (the native TestClient protocol was reverse-engineered
  from the Vanessa stack).
- Lab **data identifiers** `vanessa_client` / `vanessa_manager` / `vanessa_qa`
  (infobase/project names on the lab server).
- "split out from `vanessa-mcp`" history and "superset beyond Vanessa" benchmark.

## Resolved Scope
- Active `.mcp.json` / `.codex/config.toml` profiles do not wire `edt-mcp` or
  `vanessa-mcp`.
- Active semantic-source wording now points at `config-mcp`, `meta-mcp`,
  `bsl-mcp`, `admin-mcp` and `live-mcp`.
- Lab EDT path names and Vanessa protocol history remain only as lab identifiers
  or historical evidence.

## Acceptance
- No spec/code/profile treats `edt-mcp` or `vanessa-mcp` as an active provider.
- Legitimate protocol-research, lab data-identifier and benchmark references are
  preserved. `./bin/openspec validate --all` and the test suite pass.

## Result
Completed 2026-07-06. Active provider/profile and protocol-lab documentation no
longer treats `edt-mcp` or `vanessa-mcp` as an active provider; historical
protocol-research and evidence references were preserved.

## Next
- None.

## Log
- 2026-06-24 card created from the suite consolidation phase-2 pass.
- 2026-07-06 triage before cleanup: active profiles were clean, but active
  specs/docs still named `edt-mcp` as a semantic source.
- 2026-07-06 done: active docs/specs reconciled to the current MCP support
  stack; card moved out of backlog.
