## 1. Documentation Refresh

- [x] 1.1 Update `docs/protocol-research/status-report-2026-06-06.md` so the
  final V2 readiness state is clear and not contradicted by older baseline
  language.
- [x] 1.2 Update `docs/protocol-research/safe-ui-action-scope.md` prerequisite
  gates to state that V1 read-only no longer blocks V2 planning.
- [x] 1.3 Preserve evidence links for marker-contract and side-channel proof
  paths without copying raw runtime output.

## 2. Safety Wording

- [x] 2.1 State that V1 readiness unblocks V2 planning only; it does not accept
  any V2 safe-action protocol mapping.
- [x] 2.2 Keep diagnostic side-channel rows labeled as side-channel contracts,
  not direct wire marker observations.
- [x] 2.3 Check downstream V2 card references for consistency without editing
  those cards in this change.

## 3. Verification

- [x] 3.1 Run `bin\openspec.cmd validate refresh-v2-readiness-docs --strict`.
- [x] 3.2 Run `git diff --check -- openspec/changes/refresh-v2-readiness-docs docs/protocol-research`.
- [x] 3.3 If available, run the repository documentation/static check that does
  not start 1C runtime.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol lab readiness documentation | Offline docs/spec update and validation plan | OpenSpec strict validation; diff whitespace check; retained links to existing compact evidence | `docs/protocol-research/status-report-2026-06-06.md`; `docs/protocol-research/safe-ui-action-scope.md`; `openspec/changes/refresh-v2-readiness-docs/` | required | `project:qa-mcp` | N/A for live runtime apply: this change starts no 1C process | Low: docs can drift if later V2 cards skip the status report |
| Managed form layout | V2 safe-action target prerequisites | Statement that V1 read-only fixture evidence no longer blocks planning | Existing compact V1 evidence links only; no new form tree or screenshot in this change | `docs/protocol-research/safe-ui-action-scope.md` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A for new UI evidence: no target is opened in this change | Medium: later V2 actions still need their own retained UI evidence |
| Form module or command | Manager side-channel diagnostic acceptance caveat | Wording that distinguishes side-channel contract proof from direct wire marker proof | Existing compact side-channel evidence links | `docs/protocol-research/status-report-2026-06-06.md` | required | `project:qa-mcp` | N/A for command execution: no command is executed in this change | Medium: unsafe if later docs treat side-channel rows as direct protocol proof |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL source is changed | None |
