# 77. Python test-manager feature parity — agent_runtime capabilities

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): this card is a DECISION RECORD (agent_runtime = accepted non-scope of protocol
  decoding, built on demand). Folded into **card 98** (Product boundary) as **change 4**. The decision +
  per-member table below is preserved as working detail; card 98 is the active surface.

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-14: spun off from card 75 tail-coverage. With the UI-command tail closed (145/160,
  candidate=0), the 11 remaining `agent_runtime` uncovered members were reviewed. They are NOT
  UI-action protocol commands to decode/replay — they are the **test manager's own API surface**
  (session lifecycle + manager config/control). They are an intentional **non-scope of protocol
  decoding** but an explicit **scope of the Vanessa-replacement** (our Python test manager must offer
  equivalent capabilities for feature parity). This card records that decision + the per-member plan.

## Framing
`agent_runtime` = capabilities the test manager exposes to scenario authors (what Vanessa's 1C test
manager provides), distinct from the UI-action members (Click / Activate / ExecuteChoice…) that the
protocol-coverage effort maps. Some agent_runtime members are manager-local; some DO touch the wire
(handshake, file-dialog seeding, UI-action recording). Coverage % of the protocol inventory should NOT
count these — but the Python manager (`qa_mcp`) needs analogues to replace Vanessa.

## The 11 agent_runtime members — local vs wire + parity status
| Member | Local / wire | qa_mcp status | Parity priority |
| --- | --- | --- | --- |
| TestedApplication.Connect | **wire** (TCP + handshake) | **DONE** — `session.py open_and_bootstrap` (synthesized handshake) | n/a (have it) |
| TestedApplication.Disconnect | **wire** (teardown) | **DONE** — socket close | n/a (have it) |
| TestedApplication.SetMaxActionExecutionTime | manager-local timeout | partial — replay has read/idle timeouts; no per-action setter | low — add a knob when needed |
| TestedApplication.StartUILogRecording | **wire** (tells client to record UI actions) | none | low — only if a scenario records user-action journals |
| TestedApplication.FinishUILogRecording | **wire** (returns XML of recorded actions) | none | low — pairs with Start |
| TestedApplication.PauseUILogRecording | **wire** | none | low |
| TestedApplication.ResumeUILogRecording | **wire** | none | low |
| TestedApplication.CancelUILogRecording | **wire** | none | low |
| TestedApplication.ClearAccumulatedPerformanceIndicators | client perf reset (paired with the already-touched Get…) | none | low — perf metrics, nice-to-have |
| TestedApplication.SetFileDialogResult | **wire** (pre-seeds client file-dialog result) | none | **medium** — needed for tests that open file dialogs (otherwise they block) |
| TestedApplication.ClearFileDialogResult | **wire** (clears the seeded result) | none | medium — pairs with Set |

(The 3 remaining `read_only` uncovered — WaitForCondition, TestedFormField/Decoration.GetObject — are a
separate concern: WaitForCondition polls a manager-side predicate; the GetObject pair are typed child
accessors covered by the existing НайтиОбекъ/ПолучитьОбъект paths. Tracked as deferred/N/A, not here.)

## Decision
- These 11 are an **accepted non-scope of protocol-decoding coverage** (the 160-member inventory % need
  not include them) and a **deferred scope of the Vanessa-replacement** (Python-manager features).
- Connect/Disconnect are already implemented (handshake synthesis + teardown).
- The rest are built out **on demand** — when a real scenario needs file-dialog seeding (medium),
  UI-action recording, perf metrics, or a per-action timeout — not for a coverage number.

## Acceptance
- This card stands as the record of the decision (no immediate code change required).
- When a scenario needs one of these, implement the qa_mcp analogue and reference this card.
- First likely build-out: `SetFileDialogResult`/`ClearFileDialogResult` (medium) if file-dialog tests appear.

## Log
- 2026-06-14: card created; agent_runtime reviewed, framed as Python-manager feature-parity (non-scope
  of protocol decoding), per-member local-vs-wire + parity status recorded.
