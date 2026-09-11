## 1. Instruction Updates

- [x] 1.1 Update `AGENTS.md` safety language if it needs to name the V2
  safe-action boundary explicitly.
- [x] 1.2 Update `.codex/skills/1c-testclient-protocol-research/SKILL.md` so
  V2 action behavior requires the reviewed safe-action manifest contract.
- [x] 1.3 Review other local `.codex/skills/*.md` files for wording that could
  route V2 into broad clicks, text input, writes or business commands.

## 2. Routing Rules

- [x] 2.1 Add fail-closed wording for missing or incomplete V2 manifest rows.
- [x] 2.2 Name excluded V2 families and route them to later mutation/recovery
  cards.
- [x] 2.3 Preserve existing rules for owned PID cleanup, raw capture exclusion
  and evidence paths.

## 3. Verification

- [x] 3.1 Run `bin\openspec.cmd validate align-agent-v2-safety-instructions --strict`.
- [x] 3.2 Run `git diff --check -- openspec/changes/align-agent-v2-safety-instructions AGENTS.md .codex/skills`.
- [x] 3.3 If available, run the repository documentation/static check that does
  not start 1C runtime.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Agent safety instructions for V2 protocol research | Offline instruction update and validation plan | OpenSpec strict validation; diff whitespace check; reviewed instruction paths | `AGENTS.md`; `.codex/skills/1c-testclient-protocol-research/SKILL.md`; `openspec/changes/align-agent-v2-safety-instructions/` | required | `project:qa-mcp`, `/opt/ai-tools-1c` | N/A for live runtime apply: no 1C process is started | Low: instruction drift if future cards bypass the manifest |
| Form module or command | Click, command execution, input and write routing in agent instructions | Fail-closed route for actions outside V2 manifest allowlist | Instruction wording naming excluded families and later-card routing | `AGENTS.md`; `.codex/skills/1c-testclient-protocol-research/SKILL.md` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A for command execution: this change only updates instructions | Medium: ambiguous user requests still need careful classification |
| Managed form layout | Safe focus, activation, page, local row and menu/group action planning | Instruction wording requiring reviewed target markers and result markers | Instruction wording linked to safe-action scope docs | `.codex/skills/1c-testclient-protocol-research/SKILL.md` | required | `project:qa-mcp` | N/A for live UI evidence: downstream V2 cards produce evidence | Medium: target safety remains dependent on manifest quality |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL source is changed | None |
