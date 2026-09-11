# Stabilize local TestClient readiness and cleanup

## Status

4.done

## Owner

Codex (qa-mcp)

## OpenSpec Stage

done (2026-08-17)

## Problem

The connected-project Linux smoke exposed two local lifecycle failures:

- `launch_test_client` returned `alive/listening=true` while 1C exited moments
  later on a client-license failure;
- `stop_test_client` refused to clean the owned Xvfb after the client PID had
  already disappeared.

## Acceptance

- Local launch proves a vacant/listening TPort and 20-second process stability
  without consuming the first manager protocol session.
- Late launch failure includes bounded password-redacted output diagnostics.
- A stale client PID can still clean a live Xvfb only when the retained
  ownership identity matches exactly.
- Unowned and PID-reused processes remain fail-closed.
- Focused and full offline tests plus a connected-project live rerun pass.

## Change Set

- `stabilize-local-testclient-readiness`

## Verify

- focused lifecycle/settings/doctor/descriptor tests: pass;
- full offline suite: `933 passed, 5 skipped`;
- Connected-project stdio MCP: 68 tools; Gherkin, smoke generation and OData pass;
- thick lifecycle and doctor TPort/smoke pass; cleanup pass;
- thin lifecycle returns a bounded license failure; cleanup pass;
- descriptor drift is correctly classified; with the target version injected,
  the current target form result is honestly `descriptor-empty`;
- strict OpenSpec validation and `git diff --check`: pass.

## Archive

- `openspec/changes/archive/2026-08-17-stabilize-local-testclient-readiness`

## Result

Implementation and runtime verification complete. No business-data mutation,
role matrix, BSL or metadata operation was required for this qa-mcp contour.

## Next

- none

## Log

- 2026-08-17T16:12:00Z reproduced transient readiness and stale-Xvfb cleanup on the connected development target.
- 2026-08-17T17:12:00Z completed stdio/runtime matrix and full offline suite; installed the missing Go toolchain and corrected ignored `.ai` directory ownership required by release tests.
