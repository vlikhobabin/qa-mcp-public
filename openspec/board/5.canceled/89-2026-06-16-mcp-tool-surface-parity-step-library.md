# 89. Full MCP tool-surface parity + Gherkin step library

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): folded into **card 98** (Product boundary) as **changes 2 & 3** (MCP tool-surface
  parity + searchable step library). The full plan below is preserved as working detail; card 98 is the active surface.

## Order Index
89

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-16: roadmap card 82, stage 7. qa-mcp's MCP exposes 3 tools (`transpile`/`run_scenario`/`run_step`);
  vanessa-mcp exposes ~27 (state, window list, variables, breakpoints, command interface, results tree,
  infobase info, a searchable step library, …). Closing the surface is what makes qa-mcp a true drop-in.

## Summary
Bring the qa-mcp MCP tool surface and the Gherkin step vocabulary up to the parity an agent expects from
vanessa-mcp, so existing Vanessa-style scenarios/agents work against qa-mcp with minimal change.

## Acceptance
- MCP tools added to cover the practical vanessa-mcp surface: session/run state (`get_state`-equiv),
  window/active-window data, infobase info, test results, and the connect/screenshot tools from cards 84/85.
- A searchable step library (the Gherkin vocabulary the runner supports) with discovery
  (`search_for_steps`-equiv) and clear mapping to the native action kinds.
- A compatibility note documenting which vanessa-mcp tools/steps are covered, mapped, or out of scope.
- An existing Vanessa-style `.feature` runs against qa-mcp's MCP with only the documented adaptations.

## Change Set
- none yet

## Related
- cards 83 (write), 84 (client), 85 (screenshots), 86/87 (synthesis/introspection), 88 (coverage),
  `src/qa_mcp/mcp_server.py`, `src/qa_mcp/scenario/gherkin.py`. Reference surface: vanessa-mcp 27 tools.

## Log
- 2026-06-16T00:00:00Z card created.
