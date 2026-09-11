# Scope native TestClient transport configuration to the active application

## Status
4.done

## Lifecycle
openspec-v1

## Owner
qa-mcp

## Series
oss-fix-04b

## Order Index
406.232

## OpenSpec Stage
archived; independently verified under operator-authorized manual completion

## Priority
P1

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source
- 2026-09-10 clean published HEAD `bd64e5a`: repeated all five real-factory observations after completed FIX-04A; the transport defect remains. No sockets executed. Current retained baseline: `.runtime/qa-roadmap/oss-00/fix-04b-start/reproduction.json`.
- Published-stage review R4, 2026-09-05, commit `8e46aa565d9c7bd474f088079192092647100441`.
- Operator-authorized decomposition of FIX-04; current OSS-00 continuation planning.
- 2026-09-10 real-factory probe on HEAD `a3774e8` plus retained manual FIX-04A payload: A/B/absent/partial/malformed Settings all selected the conflicting process relay. Sockets prohibited; environment restored. Diagnostic: `.runtime/qa-roadmap/oss-00/fix-04b-planning/reproduction.json` (not passing acceptance proof).

## Summary
`relay_configuration()` still defaults to process environment inside composed
calls. Session, replay, foreground, native write/mutation/XTEST and lifecycle
consumers converge on that connector. Explicit factory Settings must govern
transport, preserving exact endpoint auth and non-consuming readiness.

## Acceptance
- [C1] Real factories with distinct relay Settings and a conflicting process relay use only their own relay fields through actual session/replay, foreground, native write/mutation/XTEST and lifecycle/attachment consumers. Explicit absence remains absence; low-level env arguments cannot override an active application. Target/session admission remains unchanged.
- [C2] Partial or malformed application relay fields fail before socket creation without process fallback. Authentication refusal closes the failed connection before protocol use. Public diagnostics are bounded and contain neither configured tokens nor arbitrary peer reply prose.
- [C3] Only the exact configured relay host/port receives authentication before protocol bytes; different direct endpoints receive none. Listener-only readiness connects/closes without preface, protocol payload or TestClient manager-session acquisition, and rejects nonmatching endpoints as relay readiness.
- [C4] Nested, concurrent sync/async and actual thread-dispatched bound calls retain their application's configuration and attachment. A catches an inner B exception and immediately reconnects with exact A scope. No process environment mutation occurs; the caller restores and explicit legacy env adapters outside composition remain compatible.

## Scope
- `src/qa_mcp/config.py`, `src/qa_mcp/core/application.py`, `src/qa_mcp/protocol/transport.py`.
- Focused consumer tests in `tests/test_config.py`, `tests/test_testclient_relay_transport.py`, `tests/test_protocol_session.py`, `tests/test_shared_core_extension.py`, `tests/test_lifecycle.py`, `tests/test_native_write.py`, plus affected foreground/mutation/XTEST/replay tests selected by actual imports.
- `docs/shared-core-extension.md`, `docs/qa-mcp-tool-reference.md` where their relay contract changes; one linked native change and canonical runtime-configuration spec through native sync.

## Non-Goals
- Display/HTTP fixes (FIX-04A), artifact-root consumers (FIX-04C), protocol frame changes, private relay implementation, target-admission changes or secret-bearing diagnostics.
- No live 1C, process signalling, business mutations, release or ChangeRail development.
- No reopening of completed FIX-04A or stopped FIX-02; no inherited extra review allowance.

## Affected Capabilities
- `qa-mcp-runtime-configuration`

## Depends On
- none

## OpenSpec Changes
1. `oss-fix-04b-isolate-testclient-transport-settings`

## Design
- The linked `design.md` owns implementation choices. Real factories must reach actual shared connector consumers with fake socket/process boundaries; do not mock away settings resolution.
- Evidence must pair each destination with its synthetic preface/port and before/after context, rather than only count calls. C4 includes inner B exception and immediate exact A restoration.
- Typed proofs directly select all claimed consumer/control tests and retained source fragments. Failed baseline observations are distinct from passing current-payload evidence.
- Mutation/restart/external-effects risks are contained with fake boundaries and preserved admission. Native Linux/Windows qualification belongs to separately authorized FIX-11/FIX-12.

## Coverage And Boundary
Owns transport isolation from parent FIX-04 only. A minimal configuration scope
may later serve FIX-04C, but no filesystem consumers move here. FIX-04A has no
product dependency edge and is now completed/published (`54d7bac`). The shared
lane is clean on `bd64e5a`; the transport defect was reconfirmed on this source.

## Delivery Budget
- primary_invariant: Every composed native connect and relay readiness resolution uses only its application's transport settings while preserving exact authentication and isolation.
- expected_wall_minutes: 75
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 180

## Budget Notes
Measurements are advisory. One coherent change has three ordered task groups;
there is no split based on numerical ceilings. The ordinary two-review allowance
and all scope/evidence/authority gates remain mandatory.

## Canonical Specs
- `openspec/specs/qa-mcp-runtime-configuration/spec.md`

## Verify
Future checks, not completed implementation evidence. Start with explicit focused
nodes/files for changed behavior, inspect affected consumers with `--qa-plan`,
and retain actual selected nodes for all C1–C4 claims. Use separate lanes:
- `uv run pytest --qa-changed --qa-lane offline --durations=10`
- `uv run pytest --qa-changed --qa-lane integration --durations=10`
- `uv run python -m scripts.qa_compile_changed`
- `./bin/openspec validate oss-fix-04b-isolate-testclient-transport-settings --strict --no-interactive`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`
No whole-suite pytest or whole-project coverage floor is authorized by this card.
Retain current source-bound JUnit and observations after final Result/Log edits
under `.runtime/qa-verification/oss-fix-04b/`; runner records the actual receipts.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Real factory native consumer routing",
      "precondition": "A/B/empty Settings conflict with a third process relay",
      "action": "Invoke real session/replay, foreground, native write/mutation/XTEST and lifecycle/attach consumer paths with fake sockets",
      "expected": "Each active application supplies exact relay fields; empty stays direct; no target-admission bypass",
      "method": {
        "kind": "test",
        "target": "tests/test_shared_core_extension.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Pre-socket configuration and public refusal boundary",
      "precondition": "Partial or malformed scoped fields and hostile fake relay replies",
      "action": "Invoke shared connector via composed consumers and serialize failures",
      "expected": "Invalid configuration opens no socket; refused socket closes; diagnostics stay bounded and omit token and peer prose",
      "method": {
        "kind": "test",
        "target": "tests/test_testclient_relay_transport.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Exact auth endpoint and listener-only readiness",
      "precondition": "Configured relay, different direct endpoint and lifecycle readiness",
      "action": "Connect through actual consumer and readiness entry points at fake socket boundaries",
      "expected": "Only exact relay gets auth preface; direct gets none; readiness sends no bytes and acquires no TestClient manager session",
      "method": {
        "kind": "test",
        "target": "tests/test_testclient_relay_transport.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C4",
      "seam": "Nested sync/async and thread context lifetime",
      "precondition": "Two real applications with distinct settings and retained caller/attachments",
      "action": "Interleave, call failing B inside A, reconnect A, exercise actual dispatch, then explicit unbound legacy env adapter",
      "expected": "Exact A restores immediately; each destination/token/port belongs to its application; no env or attachment leak; legacy mapping retained",
      "method": {
        "kind": "test",
        "target": "tests/test_shared_core_extension.py"
      },
      "stage": "implementation"
    }
  ],
  "risks": [
    {
      "kinds": [
        "input_safety"
      ],
      "applies": true,
      "decision": "Validate scoped fields before sockets; synthetic tokens and hostile replies establish bounded secret-free diagnostics.",
      "conditions": [
        "C1",
        "C2",
        "C3"
      ]
    },
    {
      "kinds": [
        "concurrency"
      ],
      "applies": true,
      "decision": "Actual application binding owns config scope; nested failures, interleaving and thread dispatch prove reset and ownership.",
      "conditions": [
        "C4"
      ]
    },
    {
      "kinds": [
        "mutation",
        "restart",
        "external_effects"
      ],
      "applies": true,
      "decision": "Native helper/lifecycle call paths reach fake socket/process boundaries only; exact target and no-preface readiness controls preserve admission and avoid target session consumption.",
      "conditions": [
        "C1",
        "C2",
        "C3"
      ]
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "No release/publication surface changes; planned proof is offline and ordinary runner publication gates remain mandatory.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority
This card is a hermetic Python correction with fake effects, not native
certification. The OSS-00 mandate authorizes preparation and eventual ordinary
native delivery/commit/push once its actual gates are satisfied. This planning
checkpoint grants no live target authority and does not bypass stopped work.

## Related
- `openspec/board/1.backlog/oss-fix-04-isolate-application-runtime-configuration.md`
- `openspec/board/4.done/oss-fix-04a-isolate-display-and-host-agent-settings.md`
- `docs/development/oss-00-orchestration.md`
- `docs/development/native-openspec-delivery.md`
- `openspec/changes/archive/2026-09-10-oss-fix-04b-isolate-testclient-transport-settings/`

## Result
C1–C4 accepted by independent review cycle 2 after repair of both cycle-1 findings.
Application-scoped transport and exact factory/consumer evidence are complete;
malformed host configuration is refused before any socket. Prearchive affected
verification passed 1597 offline and 2 integration tests, compilation and strict
canonical specs. All four requirements/eight scenarios are synced and stock
OpenSpec archive preserves the reviewed artifacts. The final affected floor,
same-reviewer postarchive confirmation and publication are retained separately
under `.runtime/qa-roadmap/oss-00/fix-04b-manual-completion/` as they complete.
The operator-authorized manual exception preserves the original stopped native
run, admission and NO-GO; no successful native handoff/run receipt is claimed.

## Next
- FIX-04B is complete under the recorded manual exception; retain the original stopped run and cycle-1 NO-GO. Final confirmation/publication use the separate manual ledger.
- Continue OSS-00 from clean published main under the operator's autonomous mandate, completing retained FIX-02 final evidence before its dependent FIX-03.

## Log
- 2026-09-05T08:38:59Z Created by operator-authorized decomposition of FIX-04; no admission, implementation, runtime, status move or publication.
- 2026-09-10 Under OSS-00 continuation, reconfirmed five real-factory settings defects without sockets. Replaced unaccepted two-change draft with one native change and ordered task groups, closed C1–C4 evidence plan and focused verification. Prior draft slugs `oss-fix-04b-scope-transport-settings` and `oss-fix-04b-consume-scoped-relay-settings` had no active/archived artifacts; their content is preserved as checkpoints here. Kept backlog status and frozen predecessors unchanged.

- 2026-09-10 Revalidated clean main/remote at `bd64e5a` after FIX-04A publication. All five no-socket real-factory probes still select the process relay. Refreshed stale blocker references; C1–C4 and implementation scope remain unchanged. OSS-00 authorization covers this native offline delivery, commit and push.
- 2026-09-10T17:57:19Z accepted native OpenSpec plan
- 2026-09-10T17:59:10Z started native OpenSpec delivery
- 2026-09-10T18:20:11Z Completed checkpoint 3 documentation and initial focused verification: changed-module offline lane (1,533 tests), integration lane (2 tests), changed-file compilation, strict change/canonical OpenSpec validation, and diff hygiene all passed. No live runtime, review, archive, commit, or publication was performed. Fresh final-payload receipts and C1–C4 implementation proof records are retained before runner handoff.

- 2026-09-10T18:44:25.098877+00:00 Operator approved the prepared task-plan correction and manual completion, with autonomous OSS-00 continuation. Preserved original native/admission records, moved circular 3.4 out of checkpoint tasks and synced all four requirements/eight scenarios without altering product acceptance.

- 2026-09-10T18:59:16.867635+00:00 Before independent review, added `tests/test_composed_transport_isolation.py`: real A/B/absent factories through all native consumer families; exact destination/preface/timeout pairing, nested B failure then A native reconnect, thread dispatch and legacy controls. Seven new cases and 81 focused offline tests pass. No further production edits; failed test-authoring attempts retained in the manual ledger. Current complete affected-test evidence is recorded after this Log edit.

- 2026-09-10T19:13:47.099261+00:00 Independent cycle 1 returned NO-GO with F1 (malformed relay host reaches sockets) and F2 (factory destination/timeout oracle too permissive); C4 passed. Repaired both together: shared pre-socket host validation, 48 malformed-host/9 positive syntax cases, and exact per-owner/per-consumer connection observations. 137 focused tests pass; an unchanged sensitivity control passes and all eight deliberate regressions are detected. Full current evidence and independent cycle 2 remain required. Prior verdict and attempts are immutable.

- 2026-09-10T19:22:16.673001+00:00 Independent cycle 2 GO accepted C1–C4 and closed F1/F2. Stock archive moved the five exact reviewed artifacts with `--skip-specs`; source/test/canonical bytes are unchanged. Final affected verification and same-reviewer postarchive confirmation precede publication, with both review cycles retained.
