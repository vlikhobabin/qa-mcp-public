## Context

On 79d0b92, actual InitialUiContext/ActiveWindowContext.to_result through the
factory's default executor yields success/value={}. ScenarioRunner.run then
fails both matching MainFrame and absent expectations. The retained baseline is
.runtime/qa-roadmap/oss-00/fix-07-planning/reproduction.json. Existing product
integration tests instead supply a BaseContext with synthetic active=true.

## Goals / Non-Goals

Give bound active-window reads useful safe observation and assertion semantics,
using actual DTOs and the existing shared admission/normalization path. Retain
positive reconstruction, total failure, bounds, provenance and compatibility.
No new wire query/parser or native uniqueness claim, unrestricted UI strings,
form/element DTO redesign, evidence producer authority (FIX-08), or default
single-session BDD acquisition/caching/routing (FIX-09A). No live activity,
new dependency or ChangeRail changes.

## Decisions

1. Define the production read_active_window value as a small fixed observation:
   window_state is an exact local literal (observed, missing, ambiguous),
   marker_count is a bounded reference count, and an explicitly requested window
   predicate may supply assertion_passed as an exact boolean. Do not expose raw
   refs/markers/captions/paths or echo the expected string. These are DTO observation
   states: observed means a nonempty reference occurs in the returned marker list;
   missing means no reference and no markers; otherwise a well-formed but unresolved
   reference/marker combination is ambiguous. This does not infer window uniqueness
   from every marker or change protocol extraction. Malformed DTO field types and
   unsuccessful base status must not become a fabricated successful observation.
2. Project actual default-handler data at a trusted internal seam before public
   normalization. Keep selected executor control, current route admission, existing
   scope lifetime and one invocation. The finite production schema only accepts
   documented fields/classes/local literals; raw data or callbacks returned by an
   executor cannot replace schema/provenance or bypass the positive boundary.
   Preserve deliberate unbound/multi-session legacy behavior when no bound policy
   is requested. Avoid adding a permissive arbitrary-string container.
3. Carry the caller's requested window predicate internally to the trusted read
   computation (or an equally bounded private carrier). Match only actual window
   ref/marker strings, not serialized metadata, credentials, capture paths or the
   normalized result/provenance. Compute before redaction; expose just its boolean.
   ScenarioRunner.run for a read_active_window Step with expect_contains consumes
   that safe outcome. Absent/mismatching predicates are false and missing/ambiguous
   observations cannot be made successful assertions by matching public words such
   as success/observed or metadata. Empty/invalid predicate input fails closed.
   Do not send an internal predicate keyword to the native session API. Broader
   run_single_session/default MCP run_scenario integration remains FIX-09A.
4. Build acceptance fixtures using actual InitialUiContext, its actual descriptor
   and ActiveWindowContext.to_result (see tests/test_protocol_session.py), with
   hostile synthetic refs/markers/frames/paths. Construct real admitted application
   factories with default local/Windows-host executors and current attachment;
   exercise the shared operation through real registered shared-operation extension
   and ScenarioRunner.run, substituting only native session boundaries. Assert
   expected adapter type and exact session-call count/arguments. No fake BaseContext
   containing synthetic production fields or replacement default handler is a
   positive product oracle.
5. Separate the existing finite-class test harness from the real active-window
   value schema. Preserve its complete valid/type/subclass/domain, literal/URL,
   structural/size/artifact/node, schema-authority and provenance protections.
   Public generic class/URL matrices can use the already declared error.details
   fields; narrow unit schema fixtures remain test-only. Do not add a production
   synthetic operation, configurable schema or callback for testing. Modify the
   canonical same-path example explicitly so removal of synthetic value.referenceLabel
   does not contradict its earlier class-test contract; error.details literal
   behavior remains exact. Preserve the forty actual public URL cases. Existing
   boundary tests should change their fixture/path, not weaken their expected oracle.
6. Put all C1-C3 acceptance nodes in tests/test_bound_active_window_outcomes.py.
   Include observed/missing/ambiguous, matched/mismatched/absent marker predicates,
   metadata-only false-match control, errors and malformed/oversized raw executor
   results. Keep ordinary unbound direct/multi-session compatibility. Test safe
   output under sanitized and approved full_local without widening disclosure.
   Retain a scoped old-schema/after-redaction negative control with failing real
   acceptance assertion, using ignored/test-only patches, no production mutation.

## Risks / Trade-offs

- Privacy: matching against a public preview loses data; exposing raw data fixes
  assertions by leaking secrets. Compute the window predicate internally and
  publish fixed state/count/boolean only, including failures and StepResult channels.
- Input safety: malicious DTO fields or expected values must not invoke custom
  conversion/iteration callbacks or forge a success. Use exact types and existing
  complete typed failures; preserve schema/provenance/receipt rejection controls.
- Compatibility: synthetic schemas currently carry extensive protection tests.
  Move those test paths explicitly and retain the negative/boundary oracle rather
  than deleting the tests or making real production fields synthetic again.
- Concurrency/restart: no new shared cache/persistent state; any private expectation
  carrier is request-local and must restore context after success/failure. Test
  independent calls with different expected values if a carrier is introduced.
- Mutation/external effects: no live I/O or protocol change. Native reads replaced
  by synthetic sessions; temporary fixture files only. Frame hashes/replay claims
  are not introduced. Existing real-runtime qualification remains separate.
- Publication: ordinary runner-owned delivery, no release workflow change.

## Verification Matrix

| ID | Real observable behavior | Coverage |
| --- | --- | --- |
| C1 | Real DTO/default handler yields documented safe observed/missing/ambiguous state and count | Local/Windows-host bound factories, shared MCP operation and ScenarioRunner.run |
| C2 | Requested actual window match true, mismatch/missing false; metadata/public-word false matches rejected | Trusted pre-redaction predicate, safe StepResult preview/error and one native read |
| C3 | Exact fields/types/literals, malformed/oversized failures, unchanged provenance/receipt and generic class protection | Focused hostile tests plus adapted existing boundary/public matrices; unbound compatibility |

Use verbose terminal nodes/JUnit, current source hashes and meaningful before/
action/after assertions. Each typed Cn selector includes its complete tests in
the focused module. Reuse unaffected checks under the runner contract; run
changed offline/integration separately after final Result/Log. No full suite or
native Windows certification belongs to this card.

## Migration Plan

One native change/checkpoint. No persisted-data migration; scoped rollback restores
old projection if needed. Finalization performs semantic sync for all three deltas,
records its current native-sync mapping, updates Result/Log with actual UTC time
from the system clock, then refreshes command receipts AND typed C1-C3 records
before handoff. Archive refresh repeats only its required current proof work and
same-reviewer continuation. Never guess timestamps or confuse passing command
receipts with registered typed proof. Prior FIX-06 proof input structure is useful
reference, but derive every current hash/selector/node from this run. Serialize
chrl evidence/record writes; do not add aggregate stages as prerequisite checkboxes.

## Open Questions

None for the operator. The documented observation semantics above avoid a new
protocol diagnosis. Choose the smallest internal implementation consistent with
real DTO behavior, executor control, privacy and preserved compatibility.
