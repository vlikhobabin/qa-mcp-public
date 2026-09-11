# 102. EPIC — qa-mcp as a native SUPERSET beyond Vanessa Automation

## Status
4.done

## Order Index
102

## Owner
unassigned

## OpenSpec Stage
epic

## Source
- 2026-06-21: project review after epic 82 closed. Epic 82 delivered the protocol-driver that REPLACES the
  `vanessa-mcp` tool surface (52 MCP tools, 355 tests, capture-free, config-agnostic, cross-config-proven). The
  review found the remaining work is NOT in the protocol layer but (a) the BDD-FRAMEWORK layer around it
  (drop-in parity for existing Vanessa feature suites) and (b) a NATIVE SUPERSET — 1C-native testing capability
  Vanessa does not expose. The operator set the new north star: **превзойти Vanessa за счёт 1С-нативного
  функционала.**
- Predecessor epic: card 82 (`4.done`) — "100% Vanessa replacement" (protocol-driver scope). Memory:
  [[surpass-vanessa-native-superset-goal]], [[qa-mcp-capture-free-epic]].

## Summary
Two tracks turn "drop-in replacement" into "strictly better than Vanessa":

- **E-FW (Framework parity / drop-in).** Close the framework gap so unaltered Vanessa `.feature` suites and CI
  pipelines run on qa-mcp: broad Gherkin step vocabulary + BDD mechanics (card 103) and machine-readable
  reporting (card 104). This is the bigger remaining body of work for sense-B ("replace Vanessa Automation the
  framework", ~60-65% today).
- **E-XV (eXceed Vanessa / native superset).** Add 1C-native testing capability Vanessa lacks: data-layer
  cross-verification fused with UI driving (card 105), metadata-driven test generation (card 106), and — research
  spikes — code coverage (card 107) and performance/APDEX (card 108) during a UI run.

Parity with the `vanessa-mcp` TOOL surface (sense-A) is already ~95% done (epic 82); this epic is about the
FRAMEWORK and the SUPERSET.

## Children (priority order)
1. **103 — E-FW step-library + BDD** — drop-in узкое место №1 (vocabulary + Outline/tags/hooks/nested).
2. **104 — E-FW reporting** — Allure / JUnit for CI.
3. **105 — E-XV data-layer-assert** — OData/query/DCS cross-check (substrate ready: `live-mcp`).
4. **106 — E-XV metadata-test-gen** — auto-generate smoke tests from metadata (substrate ready: `meta-mcp`).
5. **107 — research: coverage via debug protocol** — feasibility spike (no Vanessa equivalent).
6. **108 — research: perf / APDEX** — feasibility spike (shares the debug-protocol substrate with 107).

## Acceptance
- E-FW: a representative real Vanessa feature corpus transpiles + runs on qa-mcp above an agreed threshold, with
  Scenario Outline/Examples, tags, hooks and nested scenarios working; a run emits CI-consumable reports.
- E-XV: ≥1 data-layer assert and ≥1 metadata-generated smoke suite run live on a real config; coverage/perf
  research spikes produce go/no-go findings.
- The `vanessa-mcp-parity.md` note is extended with a "beyond Vanessa" section documenting the superset.

## Change Set
- none yet — children (103-108) carry the changes. Run `/opsx:ff` on each child when it enters the phase in flight
  (planning cadence: detailed `## Change N:` only for the phase in flight + one look-ahead).

## Verify
- Offline — `pytest` 373 green; 55 MCP tools (from 52 at epic start); corpus transpile coverage 11.9% → 97.8%.

## Archive
- 2026-06-22 closed to `4.done` (roadmap-111 item 1, board hygiene). Both tracks delivered AND LIVE-verified on
  `vanessa_client`; all children 103–110 are `4.done`.

## Result
**DONE → 4.done.** Both tracks are delivered and LIVE-verified on the real `vanessa_client` (not just offline):
- **E-FW (drop-in parity):** 103 (step-library + BDD mechanics + runner execution, LIVE) + 104 (JUnit+Allure
  reporting, LIVE) + 109 (external-`.epf` open, LIVE) → real Vanessa corpus transpiles **100%**.
- **E-XV (beyond Vanessa):** 105 (data-layer assert + the flagship UI→DB roundtrip, LIVE) + 106 (metadata-driven
  smoke gen + autofill, LIVE) + 107/108 research → delivered as **110** (`measure_scenario`: code coverage +
  perf/APDEX via the `/e1crdbg/` debug protocol, LIVE + productized) — a capability Vanessa cannot do.
- State at close: **59 MCP tools, 426 offline tests green, corpus 11.9% → 100%.** `docs/vanessa-mcp-parity.md`
  carries the breadth/coverage + "beyond Vanessa" sections. All children 103–110 are in `4.done`.

The north star — превзойти Vanessa за счёт 1С-нативного функционала — is met at the capability/proof level. The
**successor roadmap is card 111** (`3.inprogress`): productize & harden the proven tool (live-regression harness,
version-resilience, doc/board hygiene, targeted refactor) + the next superset frontier.

## Next
- Successor roadmap: `openspec/board/3.inprogress/111-2026-06-22-epic-productize-harden-extend.md`.

## Related
- Predecessor: card 82 (`4.done`). Review source: `docs/vanessa-mcp-parity.md`,
  `docs/protocol-research/capture-free-epic-next-roadmap.md` (§ Success criteria — the framework note).
- Suite substrate: `live-mcp` (E-XV 105), `meta-mcp` (E-XV 106), the 1C debug interface (E-XV 107/108).
- Memory: [[surpass-vanessa-native-superset-goal]], [[qa-mcp-capture-free-epic]].

## Log
- 2026-06-21 epic created from the post-epic-82 project review. Two tracks (E-FW drop-in parity, E-XV native
  superset) + six children (103-108) framed; priority order set. Not yet ff-processed — children are thin
  backlog stubs per the breadth-thin/depth-deep planning cadence.
- 2026-06-21 OFFLINE delivery in-session (lightweight card-as-plan): children 103/104/105/106 implemented to
  their offline cores → `3.inprogress`. 52→55 MCP tools, 373 tests, corpus 11.9%→97.8%. Remaining = lab legs
  (103 Wave 3, live demos) + research (107/108). Recommend `$opsx-pub` next, then a lab session.
- 2026-06-22 CLOSED → `4.done` (roadmap-111 item 1, board hygiene). Over subsequent lab sessions every child was
  LIVE-verified on `vanessa_client` and 107/108 were delivered as card 110 (`measure_scenario`, coverage+perf via
  `/e1crdbg/`). Final state: 59 MCP tools, 426 tests green, corpus 100%; children 103–110 all `4.done`. Successor
  roadmap = card 111 (productize, harden & extend).
