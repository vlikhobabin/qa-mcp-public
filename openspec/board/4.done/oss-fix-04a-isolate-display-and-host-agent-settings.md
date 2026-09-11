# Use application-owned settings for display and host-agent lifecycle

## Status
4.done

## Lifecycle

openspec-v1

## Owner

qa-mcp

## Series

oss-fix-04a

## Order Index

406.231

## OpenSpec Stage

archived; independently verified under explicit operator exception

## Priority

P1

## Parent Epic

- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Source

- Published-stage review on 2026-09-05, finding R4, inspected commit `8e46aa565d9c7bd474f088079192092647100441`.
- Operator-authorized decomposition of `openspec/board/1.backlog/oss-fix-04-isolate-application-runtime-configuration.md`.
- 2026-09-10 source reinspection after T0–T5 and real-factory constructor reproduction, with network calls prohibited. Reproduction and limitations are restated in the linked design; ignored `.runtime/oss00-refresh-20260910/` is optional evidence, not a clean-clone prerequisite.

## Summary

Explicit Settings reach the application context but composed display selection,
host-agent guards and lifecycle construction still consult process environment.
A remote application can select local XTEST or a third host-agent, including when
its own remote address is intentionally empty. This is a current product defect
in standalone/shared-core composition; constructor selection was reproduced
without executing any Windows or X11 operation.

## Acceptance

- [C1] Interleaved real factories with conflicting process env use their own complete display/host-agent configuration: mode, address, token, version/hash policy, timeout, window and native client port. Local calls do not select remote HTTP; remote calls do not select local X11.
- [C2] Composed launch/status/stop and supported attach routes use the same application configuration and current admitted attachment. Replacement cannot retain a stale/foreign target; stopping A cannot signal or clear B. Existing rejection of unproven bound non-owned attach remains before any backend/native call.
- [C3] Explicitly absent remote configuration never inherits a process host or silently falls back to local mode. Availability guards and related public errors reflect the active application and expose no credentials/private configuration values.
- [C4] Nested, interleaved async and exceptional calls preserve application context and isolated attachment/backend state without mutating process env. Explicit legacy env adapters outside composition retain their pin, timeout and port behavior.

## Scope

- `src/qa_mcp/protocol/display_backend.py` and `src/qa_mcp/mcp_server.py`.
- `src/qa_mcp/core/application.py` only if needed for the explicit construction seam; current Settings fields suffice.
- Focused cases in `tests/test_shared_core_extension.py`, `tests/test_display_backend.py`, `tests/test_target_bound_lifecycle_admission.py`, `tests/test_target_bound_evidence_cleanup.py`; a dedicated composition test file is allowed if it keeps cases clearer. Reuse fresh builders from `tests/support/`.
- `docs/shared-core-extension.md` and the runtime-configuration delta/canonical contract.

## Non-Goals

No ChangeRail development, repair or tests. No relay/socket routing (FIX-04B),
workspace/retention roots (FIX-04C), new bound-attach observer, resumption or
adoption of stopped FIX-02, Windows bridge API/wire changes, deployment or
native certification. Do not restore omitted external-processor support.

## Affected Capabilities

- `qa-mcp-runtime-configuration`

## Depends On

- none

## OpenSpec Changes

1. `oss-fix-04a-isolate-display-host-settings`

## Design

Implementation design and verification matrix:
`openspec/changes/archive/2026-09-10-oss-fix-04a-isolate-display-host-settings/design.md`.

Conflicting configuration is an input-safety risk because display/lifecycle
consumers can direct effects to the wrong host. Test through real factories,
observing fake HTTP/X11/signals rather than replacing the constructor under test.
Launch/stop/input make mutation, restart and external-effects risks applicable;
C2 controls prove routing/ownership offline, without authorizing real effects.
Per-call attachment binding and nested/interleaved/exception controls address
concurrency. No package/release/endpoint publication is part of the behavior.
One Settings source must also reach availability and relevant error/install
advice; changing only the constructor leaves contradictory consumer behavior.

## Coverage And Boundary

Owns the display/lifecycle part of R4. FIX-04B and FIX-04C retain transport and
filesystem ownership. Preserve the current blocked bound-attach route regardless
of the stopped FIX-02 payload present in the inspected workspace; this card does
not certify that payload or close its dependency for FIX-03.

## Implementation Plan

Ordered tasks in the single change are the checkpoints: compose display settings,
route lifecycle consumers, then verify/document. The former two uncreated draft
slugs are replaced by this native change; no legacy change is migrated or resumed.

## Delivery Budget

- primary_invariant: Every composed display or host-agent lifecycle request uses only that application's Settings and current client attachment.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 180

## Budget Notes

Retained provisional estimates from the original draft, not a measured duration
or promise. Two primary Python files, a third only if needed; test/docs work is
additional. Numerical budgets are informational under current operator policy.
They neither truncate acceptance nor authorize execution/publication.

## Canonical Specs

- `openspec/specs/qa-mcp-runtime-configuration/spec.md`
- Context: `openspec/specs/qa-mcp-shared-core-extension/spec.md`
- Context: `openspec/specs/qa-mcp-standalone-host-bridge/spec.md`

## Verify

Planned checks for implementation, not completed evidence:

- Initial focused group: `uv run pytest -q tests/test_shared_core_extension.py tests/test_display_backend.py tests/test_target_bound_lifecycle_admission.py tests/test_target_bound_evidence_cleanup.py --qa-lane offline --durations=10 --junitxml=.runtime/qa-verification/oss-fix-04a/offline.xml`. During checkpoints select only affected nodes; create the evidence directory first.
- Inspect affected-module selection against the admitted baseline with `uv run pytest --qa-changed --qa-plan`; execute additional affected consumers only as justified. Keep any affected integration checks in a separate invocation/lane.
- Compile changed Python with `uv run python -m scripts.qa_compile_changed` against the reconciled card baseline.
- `./bin/openspec validate oss-fix-04a-isolate-display-host-settings --strict --no-interactive`; after spec synchronization validate the affected canonical contract.
- `git diff --check` for the owned payload.
- No full pytest/coverage floor for this card. Full tests only before epic closure or by explicit agreement, per `docs/development/test-policy.md`.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {
      "condition": "C1",
      "seam": "Real application factory to display backend and fake HTTP/X11 boundary",
      "precondition": "Two factories have distinct complete settings; process env selects a third host",
      "action": "Interleave local and remote display calls and inspect constructed requests",
      "expected": "Each call uses its own mode, address, token, pins, timeout, window and native port; no unintended real effects",
      "method": {
        "kind": "test",
        "target": "tests/test_shared_core_extension.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C2",
      "seam": "Composed host lifecycle and per-operation attachment binding",
      "precondition": "Two applications have distinct admitted fake identities; one attachment is replaced",
      "action": "Exercise distinct launch/status/stop and supported attach branches, plus stale/foreign controls",
      "expected": "Calls use current application identity; stopping A cannot affect B; unproven bound attach makes zero backend/native calls",
      "method": {
        "kind": "test",
        "target": "tests/test_target_bound_lifecycle_admission.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C3",
      "seam": "Availability guards and public configuration errors",
      "precondition": "Explicit remote address is absent while process env provides one, or a configured fake backend fails",
      "action": "Invoke composed display/lifecycle guards and serialize their errors",
      "expected": "No env host or local fallback; correct application mode and bounded errors without synthetic secrets/private values",
      "method": {
        "kind": "test",
        "target": "tests/test_shared_core_extension.py"
      },
      "stage": "implementation"
    },
    {
      "condition": "C4",
      "seam": "Application context restoration and explicit legacy adapters",
      "precondition": "Factories have different settings and attachments; legacy caller has a separate explicit env mapping",
      "action": "Nest and asynchronously interleave calls, raise inside one context, then use the legacy adapter",
      "expected": "Contexts and attachment state remain isolated; process env is unchanged; legacy pins, timeout and port behavior remain compatible",
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
      "decision": "Conflicting configuration may route UI/lifecycle calls to another host; inspect fake destinations and reject explicit absence without fallback.",
      "conditions": [
        "C1",
        "C3"
      ]
    },
    {
      "kinds": [
        "mutation",
        "restart",
        "external_effects"
      ],
      "applies": true,
      "decision": "Consumers include input and launch/stop. Fake HTTP/X11/signals prove selected ownership without real process or business effects; preserve blocked bound attach.",
      "conditions": [
        "C2"
      ]
    },
    {
      "kinds": [
        "concurrency"
      ],
      "applies": true,
      "decision": "Per-call attachment and context restoration prevent shared mutable target leakage across replacement, interleaving and exceptions.",
      "conditions": [
        "C2",
        "C4"
      ]
    },
    {
      "kinds": [
        "publication"
      ],
      "applies": false,
      "decision": "This behavior publishes no package, release or endpoint. Ordinary delivery publication remains a separate runner transaction.",
      "conditions": []
    }
  ]
}
```

## Runtime And Authority

Offline Python routing proof only: fake HTTP, X11, sockets, handles and process
signals. FIX-11/12 own separately authorized final-source Linux/Windows
qualification. The operator adopted `docs/development/prompts/oss-00-orchestrator.md` on
2026-09-10, authorizing native admission, implementation, focused checks, runner
review, commit and ordinary push to origin/main. No live runtime is authorized.
Baseline `637e3aa57a8fc7800f01761da1c739accd64ae6c` is clean primary main and
matches remote; it retains stopped FIX-02 without delivering or adopting it.

## Related

- `openspec/board/1.backlog/oss-fix-04-isolate-application-runtime-configuration.md`
- `openspec/changes/oss-fix-04a-isolate-display-host-settings/`
- `docs/development/native-openspec-delivery.md`
- `docs/development/test-policy.md`
- `docs/development/test-improvement-results.md`

## Result

2026-09-10: independent manual cycle 4 returned GO for C1–C4 under the
operator's five-repair grant, using its first repair iteration. The complete
list diagnostic family and safe failed-launch cleanup are verified; 67 new
regressions supplement existing coverage. Prearchive evidence proves 855
selected offline cases (854 plus the passing snapshot follow-up), one
integration case, compilation and 70 strict canonical specifications.
Nonblocking R5 evidence-index references are superseded by
`manual-evidence-corrected.json`; original evidence and verdicts remain intact.
The stock OpenSpec archive is
`openspec/changes/archive/2026-09-10-oss-fix-04a-isolate-display-host-settings/`.
Specs were already synchronized and revalidated; archive used `--skip-specs`.
Postarchive checks, same-session verdict confirmation and actual publication
receipts are retained under
`.runtime/qa-roadmap/oss-00/fix-04a-five-repairs/iteration-01/delivery/`.
This is an explicit manual operator exception, not a stock native completion
receipt. Prior three NO-GOs and their spent allowance remain unchanged.


Additional authorized repair 1 of 5 (2026-09-10): the operator granted five
sequential corrections after the root-cause analysis and requested the complete
list/display diagnostic family. Current changes route refresh/sweep errors,
uncertain-zero mode and window/visible-cell diagnostic gating through one
application-aware mode accessor. Typed errors share the public serializer;
generic exceptions expose fixed safe prose. Direct legacy calls retain their
environment adapter. Thirty-nine new real-factory/fake-effect cases cover all
four public list tools, both opposite app/env directions, missing remote config,
typed/unknown/generic errors, separate refresh/sweep failures, uncertain-zero
branches, diagnostic endpoints and legacy controls. The new regression fails
against exact pre-repair helper bodies in a disposable process. Final selected
checks and source-bound observations are retained under
`.runtime/qa-roadmap/oss-00/fix-04a-five-repairs/iteration-01/`.
The broader consumer run exposed a prior sanitization regression: failed launches
lost their cleanup handle. The repair now retains only validated ownership and
identity fields, with 28 real-factory HTTP/JSON controls for valid cleanup,
malformed/foreign/secret-bearing handles and subsequent stop. Legacy tests now
expect bounded diagnostics rather than arbitrary host-agent bodies. Separate
QA consumer maintenance corrects a test-helper package import, removes obsolete
publication fixture allowances, records the two synthetic test-selection emails,
and verifies snapshot contents against the installed native distribution/history.
No ChangeRail implementation or development tests are changed or executed.
Final rerun results are recorded in `final-checks.json` in the same evidence root.
This checkpoint is implementation evidence, not an independent GO. Earlier
three NO-GO verdicts and the previous terminal exception remain unchanged;
the new allowance is a separate operator grant.

Previous terminal checkpoint:

Terminal operator exception (2026-09-10): independent review cycle 3 returned
NO-GO. R1/R2/R3 are resolved and C1/C2/C4 pass; C3 still fails at composed list
diagnostics. With explicit remote Settings and process local mode, real-factory
`search_list(refresh=True)` returns `list_refresh.error.mode=local`, both for
configured host failure and explicit missing host address. The single offline
probe retained fake HTTP/native replay, prohibited sockets/X11, correct actual
request ownership and unchanged environment. Finding R4 identifies
`_display_backend_error_result`, `_list_uncertain_zero_error` and
`_remote_client_list_diagnostic` as remaining settings consumers. No archive,
final floor or publication occurred. The one-time exception is exhausted at
3/3; installing a future exception feature cannot replenish this spent attempt.
Verbatim verdict, probe, reviewed payload manifest and terminal accounting:
`.runtime/qa-roadmap/oss-00/fix-04a-operator-exception/terminal.json`.
Historical runner runs and both original NO-GO verdicts remain byte-identical.

Previous authorization and checkpoints:

Operator exception, 2026-09-10: the operator explicitly requested one targeted
local bypass and continuation. The supervising session owns this one manual
finalization of FIX-04A, including independent review cycle 3, stock archive,
post-archive confirmation in that same reviewer session, focused final checks
and ordinary commit/push under OSS-00 authority. Historical runner verdicts and
2/2 accounting remain unchanged; the separate exception journal records total
review allowance 3 and reserves the single additional attempt before launch.
A third NO-GO or new substantive repair after review ends this exception; no
fourth review or automatic replacement card is allowed. Installed ChangeRail
and its ordinary policy are unchanged. Journal:
`.runtime/qa-roadmap/oss-00/fix-04a-operator-exception/`.

Previous manual checkpoint:

Current operator-authorized manual checkpoint (2026-09-10): the retained run
ended with two NO-GO reviews (C3 failed); earlier handoff/recovery instructions
below describe previous attempts and do not grant another review. The operator
now explicitly authorized a distribution update and manual product fixes.
ChangeRail `2.0.0-rc.3` is installed from a verified release, preserving the old
runs as read-only history. R1 is addressed by a local public error-code allowlist
with constant fallback across HTTP/JSON display/lifecycle failures, plus bounded
HTTP status values. R3 now exercises an exception inside nested B, immediate
restoration of exact A context/attachment, and full URL/target/port pairing.
Fresh C2 evidence explicitly selects replacement/owned-stop and blocked-attach
controls. Manual validation and source-bound C1–C4 observations are retained in
`.runtime/qa-roadmap/oss-00/manual-fix-04a-and-upgrade/completion.json`.
This is a manual repair checkpoint, not a runner handoff or independent GO.
No archive, final floor or publication occurred; both reviews remain used.

Previous runner checkpoints:
Implemented C1–C4; repaired the first independent-review findings and awaiting
the runner-owned continuation review. Composed display and lifecycle calls use
only active application Settings and the current admitted attachment. Public
host-agent failures retain only bounded typed diagnostics; legacy environment
adapters remain direct-call compatibility paths. No Windows or Linux native
desktop qualification is claimed.


Operator recovery instruction (2026-09-10): native sync is complete, but two
finalize sessions exited without a successful aggregate handoff. Read the
CURRENT `CHRL_RUN_DIR`, `CHRL_NATIVE_CONTEXT` and `CHRL_RECOVERY_CONTEXT`; do not
reuse a predecessor path from earlier messages. Finalize MUST continue after
`native-sync`: record current focused evidence and meaningful C1–C4 implementation
proofs, then call `./bin/chrl handoff <this-card>` and persist until exit 0.
The native-deliver skill explicitly requires this handoff for aggregate
finalization. It is not review or publication. Do not stop merely because sync
is successful. Preserve immutable sections, especially Next; only Result/Log
may change. The corrected FIX-03 dependency link is authorized board maintenance.
Retain prior attempts and both unused review cycles.

## Next

- FIX-04A is complete under the explicitly recorded manual operator exception.
  Retain all three prior NO-GOs and cycle-4 GO; no native receipt is fabricated.
- Continue FIX-04B from a clean published main under its own native plan and
  ordinary review allowance. FIX-02 remains stopped; live qualification is separate.

## Log

- 2026-09-05T08:38:59Z Created by operator-authorized board-only decomposition of FIX-04; no admission, implementation, runtime, status move or publication.
- 2026-09-10 Reconfirmed R4 on current source and refreshed the native single-change plan, C1–C4 evidence and focused verification policy. Preserved backlog status and stopped FIX-02; no implementation, runtime or publication.

- 2026-09-10 OSS-00 orchestrator verified clean main/remote at `637e3aa`, no other QA writer, installation content hashes and wiring. Repeated the four real-factory constructor observations with HTTP/socket calls prohibited; the configuration defect persists. Dry-run admission READY; operator authorization covers the complete offline native delivery cycle. Retained start evidence: `.runtime/qa-roadmap/oss-00/fix-04a-start/`.
- 2026-09-10T06:48:56Z accepted native OpenSpec plan
- 2026-09-10T06:51:14Z started native OpenSpec delivery
- 2026-09-10 Checkpoint 1 proved C1/C3 through real factories against fake
  HTTP/X11 boundaries: application Settings selected the display mode, address,
  token, pins, timeout, window and native client port despite conflicting
  process environment; intentionally absent remote settings neither inherited a
  host nor fell back to local mode.  Checkpoint 2 proved C2/C4 with distinct
  lifecycle identities, attachment replacement, stale/foreign rejection,
  nested/interleaved/exceptional contexts and explicit legacy env adapters;
  no routing path mutated process environment or signalled a foreign target.
- 2026-09-10 Checkpoint 3 documented Settings ownership and the offline/native
  boundary.  `uv run pytest -q tests/test_shared_core_extension.py
  tests/test_display_backend.py tests/test_target_bound_lifecycle_admission.py
  tests/test_target_bound_evidence_cleanup.py --qa-lane offline --durations=10
  --junitxml=.runtime/qa-verification/oss-fix-04a/offline.xml` passed 114 tests
  in 20.86s (runner evidence duration 25.849s).  Affected-module planning
  selected only `tests/integration/test_mcp_stdio.py` for the integration lane;
  its one test passed in 3.32s (runner evidence duration 6.369s).  `uv run
  python -m scripts.qa_compile_changed` compiled 5 changed Python files;
  `./bin/openspec validate oss-fix-04a-isolate-display-host-settings --strict
  --no-interactive` passed; `./bin/openspec validate --specs --strict
  --no-interactive` passed 70 canonical specs; and `git diff --check` passed.
  Canonical semantic synchronization is reserved for the native finalize stage.
  Residual qualification is FIX-11/12's separately authorized Linux/Windows
  runtime evidence; no live runtime was run here.
- 2026-09-10 Repair after review cycle 1: C3 now bounds configured host-agent
  HTTP/transport failures before public serialization, retaining only typed
  code/status and application mode. C2 real-factory HTTP controls distinguish
  A-old, A-new and B lifecycle handles, route display to each current target,
  and stop only A-new. C4 nested/interleaved async real backend controls retain
  each attachment/target and restore the caller after an exception. Fresh
  offline evidence is retained for the repaired payload; no live runtime ran.

- 2026-09-10 Operator-authorized manual repair after final NO-GO: normalized
  untrusted public error codes, retained known protocol diagnostics, added
  HTTP/JSON display/lifecycle regressions and nested inner-exception routing
  assertions. Updated manual C2 proof selection without rewriting old receipts.
  Installed verified ChangeRail rc.3; old run history and 2/2 review accounting
  remain unchanged. Fresh focused evidence is separate under
  `.runtime/qa-roadmap/oss-00/manual-fix-04a-and-upgrade/`; no third review,
  archive, done or publication is claimed.

- 2026-09-10 Explicit operator instruction authorized one local exception for FIX-04A. A separate append-only authorization/reservation preserves old run bytes and both prior NO-GO verdicts; manual finalization uses one additional independent review with a hard total of three. No GO is claimed before the independent verdict.

- 2026-09-10 Operator exception exhausted: independent cycle 3 NO-GO (R4/C3 list diagnostic mode/availability). R1–R3 resolved; C1/C2/C4 pass. No source edits occurred during review; 3/3 total attempts accounted separately without rewriting native history. No further repair/review, archive or publication was executed.

- 2026-09-10 Additional repair 1/5: fixed the full R4/C3 list/display diagnostic family, unified typed-error mode selection and bounded generic errors. Added 39 real-factory regressions with only external/capture boundaries mocked. Retained an exact pre-repair failing control and current evidence separately; no old review or accounting was rewritten.

- 2026-09-10 Additional repair 1/5 consumer verification: retained the initial
  817-pass/10-failure affected-module run; repaired the cleanup regression and
  stale QA consumer expectations identified there. Added 28 real-factory launch
  error/cleanup controls. Final checks and exact input hashes are retained
  separately, without replacing failed logs or previous verdicts.

- 2026-09-10 Independent cycle 4 GO on all C1–C4 after additional repair 1/5.
  Corrected the minor evidence-index reference issue in a separate superseding
  artifact. Stock archive completed with checked tasks and already-synced specs;
  final checks and publication are bound to the delivery evidence directory.
