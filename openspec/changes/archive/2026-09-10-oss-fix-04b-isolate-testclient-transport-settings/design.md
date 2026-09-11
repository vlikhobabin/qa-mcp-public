## Context

`relay_configuration()` currently reads `os.environ` when no mapping is passed.
`ApplicationContext` already binds synchronous and awaited asynchronous tools,
but low-level transport has no settings scope. Session, replay, foreground,
native write/mutation/XTEST and lifecycle probes import the shared connector.
A real-factory, no-network baseline reproduced process-relay selection in all
five explicit Settings cases. Retained diagnostic:
`.runtime/qa-roadmap/oss-00/fix-04b-planning/reproduction.json`.
This is defect confirmation, not passing acceptance evidence.

## Goals / Non-Goals

Goals are application-owned transport configuration, exact endpoint-bound
credentials, non-consuming listener probes, failure cleanup and context isolation.
Keep one production owner and one independently testable invariant.

No display/HTTP, artifact-root, wire-frame, relay server, target-admission,
business data, deployment or ChangeRail changes. Raw captures, frame numbers,
dynamic wire fields and replay reclassification are N/A: the existing relay
preface and TestClient frames are preserved, not newly researched.

## Decisions

1. Add a minimal context-local Settings accessor in `config.py`, activated and
   reset within the existing `activate_application_context`. The accessor has an
   explicit unbound sentinel, distinct from a bound Settings with empty relay
   fields. Avoid imports from transport into `core` or `mcp_server`. A second
   application registry would diverge; passing new arguments through every
   native caller would increase the migration surface without improving scope
   ownership. The new accessor stores configuration only, not mutable session
   or attachment identity. Reset both tokens in `finally`, including entry errors.
2. When a composed scope exists, it is authoritative. An explicit env argument
   must not override that scope. Outside composition, explicit env mapping is
   authoritative; only an unbound call without a mapping keeps the documented
   process-environment behavior. Do not change `Settings.from_env` semantics for
   other consumers. Do not manufacture fallback Settings on missing scope.
3. Resolve and validate relay fields before socket creation. Partial endpoint/
   token pairs and malformed endpoints or preface-unsafe tokens fail closed with
   bounded diagnostics. Exact requested host/port matching remains unchanged:
   transport does not rewrite direct endpoints or broaden auth via DNS aliases.
   Preserve bracketed IPv6 parsing. Unknown/rejected relay replies cannot echo
   configured tokens or arbitrary peer prose into public failures; close the
   failed socket and use a locally controlled diagnostic.
4. Keep listener-only readiness separate from authenticated protocol connect.
   Fake sockets assert no auth preface, TestClient payload or manager-session
   acquisition. Lifecycle readiness tests invoke its actual shared resolution
   path and retain proof that a different endpoint is not accepted as the relay.
5. Test actual consumers without replacing the configuration selector itself.
   Real factories and application binding exercise session/native helper and
   lifecycle paths with fake sockets, reply bytes and controlled downstream
   stopping points. Use at least one invocation of each shared connector family:
   session/replay, foreground, native write/mutation/XTEST, lifecycle/attach.
   Parameterized seam controls may share scaffolding; do not add live mutations.
   Assert destination, exact synthetic preface, timeout, close state and no
   cross-application state changes. Inner B failures must restore exact A scope
   before A's next connection. Async/thread dispatch tests follow actual binding
   semantics; background tasks with no application admission gain no authority.

## Risks / Trade-offs

- Input safety: partial and malformed configuration, token delimiters and hostile
  auth replies use synthetic values, validate before connect where applicable,
  and never serialize secrets; C1/C2/C3.
- Concurrency: nested sync/async calls and worker-thread invocation can lose or
  leak scope. Bind using existing activation and test actual factory dispatch,
  inner exceptions and restoration without process environment mutation; C4.
- Mutation/restart/external effects: native helper and lifecycle paths can reach
  sockets or signal processes. Proof substitutes these boundaries, asserts exact
  endpoint/ownership and non-consuming readiness, and does not infer new target
  admission from relay configuration; C1/C2/C3.
- Publication: no product release behavior changes. Native runner alone owns
  independent review, final floor and ordinary publication after valid admission.
  Planning receipts and successful tests are not GO.
- A context-local settings view adds a second context variable, but no second
  owner registry. Keep its lifetime wholly inside application activation and
  cover reset after every exit. A transport-only setting carrier would prevent
  FIX-04C from reusing the same minimal scope; filesystem consumers remain outside
  this change regardless of scope reuse.

## Verification Matrix

All artifact paths below are future evidence destinations; no completed proof
is claimed. Record commands, timestamps, selected nodes, source hashes and
before/action/after observations under `.runtime/qa-verification/oss-fix-04b/`.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason / residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Python native transport | Config scope, connector consumers, C1/C2/C3 | Synthetic factory/consumer regression cases | Offline JUnit, exact fake socket destination/preface/cleanup observations | `.runtime/qa-verification/oss-fix-04b/offline.xml` | required at implementation | qa-mcp | Does not certify a real TestClient/relay |
| Context concurrency | Existing sync/async activation and thread dispatch, C4 | Nested B failure, restored A, interleaving, explicit legacy mapping | Source-bound selected case evidence and unchanged environment/attachment observations | `.runtime/qa-verification/oss-fix-04b/context-proof.json` | required at implementation | qa-mcp | No new background task authority |
| Process integration | Affected MCP stdio consumer | Separately selected integration lane | JUnit and command/selection log | `.runtime/qa-verification/oss-fix-04b/integration.xml` | required if selected | qa-mcp | No broad suite fallback |
| Native Linux/Windows | Actual 1C relay/readiness qualification | FIX-11/FIX-12 target, preflight and cleanup plan | Separate authorized live bundle on final source | `.runtime/qa-verification/oss-fix-11/`, `.runtime/qa-verification/oss-fix-12/` | deferred to named cards | qa-mcp | No live target or native qualification in this Python slice |
| BSL/metadata/forms/roles/posting/reports/migration | None changed | Explicit N/A | None | `design.md` | N/A | qa-mcp | No infobase objects, UI commands, data or source import changed; future native qualification remains |

Card-size assessment: one Python configuration invariant, three production
owners/files, zero live contours. Ordered scope, transport and evidence groups
are checkpoints of one change; no runtime apply, form, role or posting work is
bundled. Any newly necessary product boundary must be replanned before admission.

## Migration Plan

Prepare artifacts and dry-run native admission while preserving FIX-04A history.
Before actual admission/delivery, recheck the source and frozen-plan boundaries
once FIX-04A has a supported disposition and the primary lane is clean. Use the
installed native runner for implementation, focused verification, semantic spec
sync, independent review, archive and publication. No manual canonical sync in
planning. Rollback is a normal scoped code revert with the same focused controls;
there is no data migration or live resource to clean up during planning.

## Open Questions

No product decision is outstanding. FIX-04A was completed and published; the
transport defect was reconfirmed on clean `bd64e5a` without sockets. Reconfirm
the exact selected consumer tests during implementation, without whole-suite
fallback. This card uses its own ordinary shared two-review allowance.
