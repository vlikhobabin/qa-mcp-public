# Retain verifiable terminal results for existing checks

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03b

## Order Index

406.222

## OpenSpec Stage

offline design draft: SPLIT_REQUIRED; measured attempt command_safety_stop, not admitted or implemented

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03-persist-and-enforce-card-evidence-contract.md`, retained-evidence boundary.
- CHRL-FIX-03A passed offline delta acceptance, not a done transition. Its static plan does not authenticate execution results.
- Current `run_evidence` records only the after-fingerprint. `_run_full_floor` already compares its start and finish payload, but `_successful_verification_matches` does not validate retained log identity. Preserve the existing floor comparison; do not claim it is absent.
- `run_shell_verification` is also used by deliberate deterministic import repair. A changed payload there is expected; do not turn all shell checks into an unconditional unchanged-payload gate.
- Exact rejected-attempt assessment: `.runtime/changerail/offline-fix03b-retry-IKbVci/orchestrator-assessment.md`. Candidate probes, baseline probes and `rejected-candidate/` there are historical evidence, not active implementation. Restored product bytes and the earlier 286-test baseline do not validate this design.
- Measured candidate cost was +230/-30 Python lines and 84 schema lines, 840.751 seconds, first edit after five reads. The late checkpoint followed attempted consumer integration. These 314 additions reject that design/estimate, not every possible compact design.

## Summary

Make a retained successful check mean that the owning runner observed terminal
completion against unchanged input bytes and retained the exact complete log.
Reuse existing command entrypoints and readers. This independently fixes false
current-proof/cache claims, even before condition-level proof enforcement.
Serialization is CHRL-FIX-03C; semantic proof binding is CHRL-FIX-03D.

## Acceptance

### Requirement: Record observed execution, not an after-only success stamp

#### Scenario: A focused check or configured verification command finishes

- [C1] WHEN an existing focused/pre-review/final check is invoked, THEN a run-local record identifies the invocation, run/card, lane, exact command form and input payload before launch; terminal evidence records start/end times, actual process exit and before/after fingerprints. A zero process exit with payload drift, incomplete output retention, spawn failure or interruption cannot become verified success; the caller reports failure/unconfirmed while preserving the actual process outcome separately.
- [C2] AND each attempt has an independently allocated path and a complete regular log with retained byte size and SHA-256. Completion is published atomically only after the log is retained; an incomplete/start-only record, absent log, altered/truncated log or unknown/malformed/duplicate-key record cannot establish success. A deliberately silent command may have a valid zero-byte log; empty output alone is not failure.

### Requirement: Consume only matching retained proof

#### Scenario: Existing readers consider a successful result for reuse

- [C3] WHEN focused summaries/repeat detection, pre-review/final reuse or final-log consumption encounter a result, THEN one bounded validator checks the supported record, invocation/run/card/lane, exact command identity, terminal outcome, current payload and safe log identity. Missing, foreign, stale or ambiguous proof is unconfirmed, never repaired by trusting a prose report or replaying command text from the record.
- [C4] AND an unchanged valid result retains existing entrypoint semantics: focused duplicate execution is refused with its retained reference; pre-review/final verification reuses a matching complete configured set. Missing proof cannot be called a cache hit. Original logs/records are never overwritten to make validation pass; existing authorized entrypoints alone decide whether to execute a new attempt.

### Requirement: Preserve role and historical boundaries

#### Scenario: A legacy record or a deliberate repair is encountered

- [C5] WHEN a record predates this execution contract, THEN it remains readable as historical/unconfirmed evidence and is not silently upgraded to current proof. Exact recovery eligibility, retained manifests, verdicts, counters and old run directories remain unchanged; any already-authorized new check writes to its current run only. Deliberate import repair still reports its real exit and before/after change without being presented as unchanged verification success.
- [C6] AND this change neither executes plan locators, maps conditions to results, changes review/final-floor ownership or command lists, nor enables the finalizer or a pilot. It makes no single-flight or all-environment reproducibility claim. Offline fixes still finish with checks/report, not a fabricated measured handoff or publication.

## Scope

Future production owner: `scripts/changerail/local_delivery.py`, bounded to
`run_evidence`, `focused_evidence_summaries`, `run_shell_verification`,
`_run_full_floor`, `_successful_verification_matches`,
`pytest_summary_from_verification` and narrow result read/write helpers.
Audit retained-focused-result consumers in `build_review_context` and recovery
evidence indexing so old/copied summaries cannot acquire a stronger status;
change only their result projection/validation, not recovery or review policy.

- Proposed `tools/changerail/schemas/check-result.schema.json`: small closed `qa-mcp.check-result.v1` execution record, separate from the unchanged plan schema.
- `tests/test_local_changerail_delivery.py`: extend actual existing producer/consumer fixtures and add the declared regression cases.
- `openspec/specs/changerail-consumer-wiring/spec.md` and `docs/development/local-changerail-delivery.md`: the observable result contract and its limits, only during authorized implementation.
- This card's Result/Log during that implementation. No other board record.

## Non-Goals

- Single-flight, process ownership/reaping, cross-run adoption or restart retry policy: CHRL-FIX-03C and the separate FIX-02 authority design own those questions.
- Condition evidence maps, inspection/runtime attestations, additional-plan admission or review-verdict version changes: CHRL-FIX-03D.
- A new executor, daemon, general ledger/Markdown module, dependency, global JSON-loader rewrite or changes to the recovery-source decoder.
- Running commands read from a plan/result document, hashing secrets/environment contents, signing evidence against a malicious local writer, live/Windows qualification, automatic Git operations or rewriting old records.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03a-validate-evidence-plans-before-admission.md`

This is the actual existing dependency path, not a fictitious done path. Offline
acceptance of 03A does not satisfy the runner's literal done dependency gate.

## Change Set

- `chrl-fix-03b-record-terminal-check-identity`
- `chrl-fix-03b-validate-retained-check-consumption`

## Design

Decision: SPLIT_REQUIRED for the complete unchanged C1-C6 promise. A simpler
single-owner design is feasible in principle, but the bounded estimate below
is 310-405 production/schema lines and 40-50 minutes including verification,
not credibly within both configured 300-line/30-minute limits. This conclusion
comes from the remaining compatible consumers and real fixture work, not from
assuming the rejected candidate's 314 additions are a lower bound. Do not raise
the limits or reduce Acceptance to obtain READY.

The existing Change Set and both Change sections are preserved historical task
ordering, OBSOLETE / NOT IMPLEMENTATION-READY. In particular, producer/schema
work followed by a later consumer integration is not a usable checkpoint.
The actual successor Tasks/Verify plans linked below now supersede that task
ordering for their respective lanes. This parent's unchanged Verify remains
an aggregate historical declaration, not an executable delivery plan.

### Compact mechanism and owner

Keep the owner in `scripts/changerail/local_delivery.py`, the proposed
`tools/changerail/schemas/check-result.schema.json`, existing delivery tests,
and the already named canonical contract/runbook. Extend existing producers
and `write_json`; no executor, module, framework, dependency, global loader
rewrite or hand-maintained structural validator. Use the existing jsonschema
package: one closed `qa-mcp.check-result.v1` record and one schema-backed reader.
Declare all allowed properties in the same closed object; state conditionals
only require/constrain those properties. Never extend an
`additionalProperties: false` base through `allOf`. Close every nested object,
use integer process exits (booleans are invalid), nonnegative finite durations,
UTC date-time strings with an active FormatChecker and UTC constraint, and
explicit command/state variants. Reject non-JSON numeric constants and decoded
duplicate keys at every depth with the bounded record decoder. Unknown versions,
unknown fields and malformed structure are unconfirmed. Only semantic
identity/payload, digest/size and safe-path checks live outside the schema.

Before launch, require actual owning run/card metadata, derive lane explicitly
at the authorized caller (`focused`, `pre_review`, `final`), allocate an opaque
attempt ID and exclusively create its run-local location. Never infer lanes
from equal command lists or directory substrings, accept optional arbitrary
foreign-run binding, or substitute missing identity with fallback/null values.
Record identity, exact argv array for focused commands versus configured shell
text and shell invocation, before-payload and UTC start in a running record.
Keep readable display fields `label`, `command`, `exit_code`,
`duration_seconds`, `observed_at`, `fingerprint` and `log` where applicable;
these projections describe observation, not independent proof. The exact argv
or configured command remains the identity used by the reader.

Terminal states distinguish observed exit/signal, spawn failure, interruption
and wrapper/retention failure. Schema variants explicitly represent a process
that never started or has no observed terminal result; they never fabricate
exit zero or certify unknown metadata. Store UTC finish, elapsed duration,
after-payload, actual process outcome and a separate wrapper result/reason.
For a zero-exit drift child, retain actual exit 0 but return nonzero/unconfirmed
to the caller. A nonzero/signal result remains the actual process result even
if a later log or JSON write fails. Preserve that observation in the failure
record if writable and in the caller diagnostic otherwise; failed storage
cannot promise durable evidence. Running or explicitly failed records cannot
be reused as success.

Retain stdout/stderr bytes using the existing producers' defined concatenation
order, without claiming temporal interleaving. Close the complete regular log,
then record its locator, byte size and SHA-256 and atomically publish terminal
completion with the existing writer. A valid zero-byte log is success-capable;
missing, truncated, altered or partially written output is not. If retention
fails, publish an explicitly unavailable-log failure variant only when possible,
otherwise leave the running record unconfirmed. Unique destinations prevent
attempt overwrite; current lookup files are indexes, never a second authority.
Do not rewrite original records/logs, including to repair validation failures.

Before ANY record, aggregate or log content read, reject absolute/traversing
locators and unsafe ancestors/leaves within the trusted run root. Use bounded
component-wise no-follow opens, directory checks and regular-file fstat before
reading; checking resolved containment after read is insufficient. Reuse this
safe reader for focused enumeration, metrics, aggregate indexes and final logs,
without changing the global/recovery-source decoder. Validate structure, exact
run/card/invocation/lane/command, terminal wrapper success, unchanged current
payload and exact log bytes together. Index projections alone never authorize
reuse. Commands from plans/results remain inert: authorized entrypoints alone
supply commands to execute and decide whether a new attempt is permitted.

### Consumer compatibility matrix

| Consumer | Required compatible behavior and authority | Vertical boundary |
| --- | --- | --- |
| Focused repeat in `run_evidence` | One reader validates each candidate before refusing a duplicate, returning its retained reference. Invalid/legacy proof is no cache hit; unique new attempts occur only through the existing entrypoint. Actual process exit and wrapper return remain distinct. | A |
| Current `focused_evidence_summaries` | Safely read records before projection; retain readable fields, classify valid current proof versus historical/unconfirmed, and tolerate failed/running records without crashes or false success. | A |
| Metrics / `deterministic_commands` | Adapt focused enumeration in the same switch; command/exit/duration/finished-time remain readable. Safely handle absent terminal values and legacy records; metrics are observations, never proof authority. Configured command rows keep their readable fields when B switches them. | A focused; B configured |
| `build_recovery_context` / `build_review_context` carried projection | Fingerprint equality alone is not current proof. Preserve historical fields with explicit historical/unconfirmed classification; only authoritative records validated in their owning context support an observed-proof description, never cross-run reuse. Do not upgrade copied summaries, alter recovery eligibility/counters or rewrite stored contexts. | A |
| Configured `_run_full_floor`, `_successful_verification_matches`, preverify/verify and preverification guard | Pass explicit lane and current owner to the same reader. Require the exact complete ordered configured set of terminal records and intact logs for one frozen payload. Preserve existing aggregate before/after comparison in addition to per-command validation. Existing aggregate shapes are readable indexes; an old `ok` or exit list cannot grant reuse. | B |
| Final `pytest_summary_from_verification` | Require validated current final-lane proof before reading the safe regular log. Parse the summary from those same validated bytes, not a reopened path. Missing/tampered/foreign proof yields no authoritative summary. | B |

Deliberate `run_safe_handoff_repair` remains a general shell operation whose
real exit zero plus actual payload change can mean repair success. Keep that
behavior and its readable result fields; do not label it unchanged verification
proof or silently apply the verification drift gate to `run_shell_verification`
as used by repair. B owns verification wrappers around the general helper.
Neither boundary changes existing command lists, review/final-floor ownership,
finalizer gates, plans, manifests, counters, old run directories or recovery
eligibility. Historical legacy data stays readable/unconfirmed, never migrated.

### Behavioral evidence and the first checkpoint

Before schema-name or new-field assertions, execute a real controlled fixture
child which changes a tracked payload and exits zero; assert caller failure.
Separately reproduce a configured cache hit whose log is missing through its
real reuse reader. Retain these behavioral RED outcomes, then positive controls
for unchanged execution and a silent valid zero-byte log. Existing
`_verification_fixture` mocks the shell producer and
`_write_matching_preverification` fabricates exit-only proof; they cannot serve
as acceptance evidence. Adapt proof-requiring fixtures to actual produced
records/logs and genuine run/card metadata while preserving unrelated guard
tests. Keep real Git payload hashing, schema validation, subprocess and log I/O;
no validator or hash mocking and no schema-only RED counted as the regression.

The first implementation checkpoint is BEFORE enabling a new producer format
or integrating later readers/floors: retain behavioral RED, a field-to-reader
inventory and measured shared schema/reader delta with real running/terminal
composition controls. This is an internal sizing checkpoint, not a deliverable
or a producer-only switch. Record elapsed time, production/schema additions and
remaining compatible-reader/test costs. For A, shared core above 190 lines or
more than 12 minutes consumed here invalidates the proposed 30-minute envelope;
also stop earlier whenever measured work plus remaining work exceeds 300 lines
or 30 minutes. Retained overrun or a necessary extra authority surface means
NO-GO/replan, not a delayed checkpoint or raised budget. Do not proceed to B
inside A. No implementation measurement is claimed by this design stage.

Within A, prove real producer -> schema -> wrapper caller -> repeat -> summaries
-> metrics -> carried/recovery classification in the same fixture, including
successful and drift cases. Within B, prove producer -> schema -> aggregate ->
reuse -> final-log summary, with missing-log and payload-drift negative controls.
Pass a genuinely produced completed record through the actual closed schema,
then every relevant reader; a broad green count does not replace this chain.

Both boundaries need applicable malformed JSON, unknown version/field and
duplicate decoded keys (including escaped spelling) at all nested levels;
boolean exit, invalid UTC dates, negative duration; spawn failure, interruption,
log-write and completion-write failures; running-only, empty-valid, missing,
tampered and truncated logs. Cover foreign run/card/invocation/lane/command,
stale payload, unsafe relative/absolute paths, symlink ancestors and leaf,
nonregular record/log paths BEFORE reads. Use outside-read sentinels to prove
refusal order while leaving the validator/digest real. Preserve actual observed
process results during retention failure. Recheck unchanged valid repeat/cache
with a counted real child and byte-identical old evidence. B additionally tests
equal configured lists in different lanes and real intentional import repair.

### Risks, limits and vertical coverage

Input safety (C2/C3): closed schema, duplicate-key decoder and safe opens before
content reads. Mutation/restart (C1/C2/C4/C5): pre-launch identity, before/after
payload, unique attempts, terminal-after-log publication and explicit failure.
Concurrency (C2/C6): attempts do not overwrite; redundant execution/single-flight
belongs to 03C. Publication (C3/C6): validated final proof, unchanged publisher
and role gates. External effects (C1/C3/C6): only authorized existing command
entrypoints; planned tests use controlled offline children. No live/provider,
Windows, protocol captures/frames/replay or runtime cleanup applies here.
Local trusted-runner observation cannot prove absence of transient edit/revert,
environment reproducibility, test sufficiency or malicious-writer resistance.

Disjoint delivery boundaries, now recorded in the successor cards below:

- A: Fully usable focused execution proof, including the shared schema/safe
  reader, producer AND every affected focused repeat/summary/metrics/carried
  consumer. Configured floor behavior remains its prior contract until B;
  A must not claim the parent's configured acceptance is complete. This is
  usable on its own because every reader of its new format moves together.
- B: Configured pre-review/final execution proof, complete-set reuse and final
  log consumption, depending on A's shared contract. Adapt configured metric
  projections and real floor fixtures together, preserve aggregate drift and
  deliberate repair behavior. No second validator or authority is introduced.

| Parent obligation (preserved in full) | A coverage | B coverage |
| --- | --- | --- |
| C1 | Focused pre-launch identity, terminal observation, caller failure | Both configured lanes and wrapper outcome |
| C2 | Shared closed record, safe unique retention and focused fault matrix | Configured attempts, aggregate indexes and fault matrix |
| C3 | Focused repeat/current summaries/metrics and carried historical projection | Complete floor/reuse and validated final-log reading |
| C4 | Intact focused repeat refusal with retained reference | Intact exact configured-set reuse and invalid-cache refusal |
| C5 | Legacy focused history, no rewrite/adoption or recovery/counter change; general repair API preserved | Legacy configured history and real changed-payload repair regression |
| C6 | No condition binding, loaded-command execution, new role authority or single-flight | Same constraints; unchanged final-floor/finalizer/pilot/publication ownership |

Reject producer-only or schema-only runtime switches, a second manual validator,
and a framework refactor. The shared core is necessary within A, not a separate
independently usable sibling. A and B partition delivery by usable check lanes,
not by function; together they retain the complete parent promise.

### Actual successor plans and dependency gates

- A is `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`: one complete focused producer/consumer boundary; 30 minutes/280 production-schema lines, with the internal shared-core 190-line/12-minute stop before producer activation.
- B is `openspec/board/5.canceled/chrl-fix-03b2-retain-configured-verification-proof.md`: configured proof/reuse/final logs and real intentional-repair regression using A's sole contract; incremental 25 minutes/125 lines, dependent on the actual A card.

Each sibling has its own ordered Tasks, checkpoint and complete Verify JSON;
their C1-C6 IDs correspond to the same-numbered parent obligations restricted
to the A/B coverage table above. A C5 preserves configured/repair behavior;
B C5 additionally proves the real intentional changed-payload repair. Both C6
retain the unchanged authority and claim limitations. Nothing is dropped from
the parent's Acceptance, and no producer-only checkpoint becomes a delivery.

This parent remains a SPLIT_REQUIRED aggregate in backlog, not a future literal
done dependency. 03C and 03D now depend on both actual successors instead of
this non-executable parent. 03A remains A's actual existing prerequisite; its
offline acceptance does not satisfy the runner's done gate. The older Budget
Notes describe the prior design stage before successor creation; the linked
plans now supply the tasks/Verify reconciliation it requested, not admission.

## Delivery Budget

- primary_invariant: A retained current check success requires terminal unchanged-payload execution and an intact run-bound log.
- expected_wall_minutes: 45
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 2
- estimated_production_loc: 355

## Budget Notes

These are honest aggregate estimates, not increased configured limits or an
admissible budget: the configured ceiling remains 30 minutes / 300 production
LOC. The prior 280-line/30-minute estimate is superseded by this DESIGN verdict.
Count schema additions as production; no minification, net-deletion accounting
or exclusion of necessary consumer work to force a pass.

Compact A estimate: schema 60-75 lines, shared safe decoder/validator and
retention helpers 95-115, focused producer/compatible projections 65-90:
220-280 production/schema lines. B increment: configured wrappers/explicit
lane and aggregate reuse 65-85, final-log/metric adapters 25-40: 90-125 lines.
The coherent total is 310-405 (central estimate 355), even after sharing the
schema and writer and avoiding a new executor. These ranges are design estimates,
not facts inferred by subtracting the rejected implementation.

A wall estimate is 27-30 minutes: roughly 3 behavioral RED, 9 shared core,
5 complete focused integration, 5 negative/compatibility tests and 5-8 for
contract/runbook, focused evidence, independent review and the configured floor.
B estimate is 20-25 minutes: roughly 6 configured integration, 7 real fixture/
reuse/final-log/repair matrix, 2 contract documentation and 5-10 review/checks.
The aggregate 40-50 minutes allows shared setup/check savings; tests/docs and
review/floor time are included, not hidden outside implementation. The earlier
840.751-second attempt did not deliver this matrix or the final floor and is
not a throughput guarantee. A has little margin and is a candidate for successor
planning, NOT READY admission. A measured shared-core or verification cost that
exceeds the first checkpoint means even shared core plus the first vertical
slice does not fit: report NO-GO/replan honestly, never ship the core alone.

The next outer planning action must establish actual successor plans and Verify
coverage, then reconcile tasks and check their own configured admission. No
successor is created or admitted here. The parent's Acceptance C1-C6 remains
unchanged and is not complete until both boundaries have evidence.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

These are future test locators, not present passing evidence. Keep real Git,
payload hashing, record/log I/O and validation; fake model/network/publication
boundaries. Use a tiny controlled subprocess to change a fixture file while the
check is running; do not stub the fingerprint comparison being tested.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"focused and configured producers","precondition":"stable fixture and a check that changes its payload before exit zero","action":"run real check wrappers and compare recorded before/action/after state","expected":"stable terminal control verifies; drift and unfinished execution remain unconfirmed with actual process exit retained","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_result_terminal_and_payload_binding"},"stage":"implementation"},
    {"condition":"C2","seam":"record and log finalization","precondition":"running-only, malformed, duplicate-key, missing, empty-valid and changed log cases","action":"complete attempts and validate retained proof","expected":"only complete regular matching logs verify; failed writes and damaged logs never publish success","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_result_log_integrity"},"stage":"implementation"},
    {"condition":"C3","seam":"real proof consumers","precondition":"valid proof plus foreign identity, unsafe path and stale variants","action":"read through focused, pre-review, final and summary consumers","expected":"matching proof is usable; all invalid forms refuse without outside reads or executing recorded commands","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_result_consumers_fail_closed"},"stage":"implementation"},
    {"condition":"C4","seam":"existing reuse paths","precondition":"valid completed check followed by repeated request and missing-log variant","action":"invoke ordinary repeat and configured-cache paths with a counted fixture child","expected":"existing valid reuse semantics spawn no duplicate; invalid proof is not a cache hit and old records are preserved","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_result_reuse_requires_intact_proof"},"stage":"implementation"},
    {"condition":"C5","seam":"legacy evidence and deliberate repair","precondition":"exact retained legacy fixture and an intentional import-only repair","action":"inspect old evidence and exercise authorized current check and repair wrappers","expected":"old records/counters stay byte-identical; no automatic upgrade; repair change is not unchanged verification success","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_check_result_legacy_and_repair_boundaries"},"stage":"implementation"},
    {"condition":"C6","seam":"scope and role ownership","precondition":"final scoped diff and ordinary handoff/finalization guards","action":"inspect delta and run existing relevant guard fixtures","expected":"no execution from locators, new role authority, finalizer enablement or single-flight claim","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"Closed decoded-key validation and safe regular run-local log reads precede digest use.","conditions":["C2","C3"]},
    {"kinds":["mutation","restart"],"applies":true,"decision":"Unique attempts, before/after fingerprints and terminal-after-log publication retain failures and reject incomplete proof without rewriting history.","conditions":["C1","C2","C4","C5"]},
    {"kinds":["concurrency"],"applies":true,"decision":"Attempt paths cannot overwrite; no single-flight promise until 03C. Uncertain attempts never become reusable success.","conditions":["C2","C6"]},
    {"kinds":["publication"],"applies":true,"decision":"Final-verification consumers validate intact proof; no publisher Git transaction or authority change.","conditions":["C3","C6"]},
    {"kinds":["external_effects"],"applies":true,"decision":"Reuse existing authorized command paths only; fixtures run local controlled children and prohibit model/network/publication calls.","conditions":["C1","C3","C6"]}
  ]
}
```

Planned focused command: `uv run pytest -q tests/test_local_changerail_delivery.py -k check_result`.
Then the ordinary delivery/FF/board/evidence-plan harness, whitespace,
compilation, strict canonical specs and wiring. The outer runner owns the one
configured non-live coverage floor after fresh GO for authorized delivery;
this planning pass runs no product tests or delivery commands.

## Related

- `openspec/board/5.canceled/chrl-fix-03-persist-and-enforce-card-evidence-contract.md`
- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`
- `openspec/board/5.canceled/chrl-fix-03b2-retain-configured-verification-proof.md`
- `openspec/board/5.canceled/chrl-fix-03c-serialize-verification-attempts.md`
- `openspec/board/5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md`
- `docs/development/local-changerail-delivery.md`

## Result

Offline implementation attempted; SPLIT_REQUIRED, not accepted or active.
The candidate passed a 287-test harness but isolated orchestrator probes found
that produced terminal records violate their own schema, payload drift still
returns wrapper success, malformed terminal fields pass the reader, and the
new producer breaks the existing metrics reader (`KeyError: 'command'`).
The unchanged summary reader also reads a foreign symlinked record before
refusing it. C1/C2 are therefore not accepted; C3-C6 remain unimplemented.

The rejected candidate and exact probe results are retained under
`.runtime/changerail/offline-fix03b-retry-IKbVci/`. Its production/test edits were
restored byte-for-byte to this task's pre-implementation baseline and its new
schema was removed from the working payload, with a recoverable copy retained.
Earlier authorized changes, the stopped pilot and retained history are intact.
This card's plan, acceptance, budgets, Verify and status remain unchanged.

Refinement must establish a coherent producer/consumer compatibility boundary,
schema-backed validation and behavioural negative tests before another attempt;
do not treat a producer-only switch as a usable checkpoint. The estimate was
insufficient for the attempted design, and the required size checkpoint was
recorded only after attempted consumer integration. No board move, handoff,
GO verdict, publication, runtime operation or final coverage floor ran.

Design-stage conclusion: SPLIT_REQUIRED. Compared the simpler existing-jsonschema /
existing-writer approach before estimating the full compatible C1-C6 boundary.
The 310-405-line / 40-50-minute aggregate is not credibly within 300 lines /
30 minutes; propose A fully usable focused proof and B configured floor/reuse/
final-log proof with the full coverage matrix above. Neither is an admitted or
implemented successor. The historical statement about the unchanged plan above
refers to restoration after rejection; this entry supersedes that old design,
budget and Next, while preserving Acceptance, Verify and Change sections.

This measured stage is authorized offline board-only replanning in the occupied
checkout, not ordinary clean-start FF admission. Prior work stays intact. Only
the designated card planning sections changed; no product checks, model sessions,
lifecycle delivery/recovery/handoff or publication ran. Historical restored
286-test results are baseline evidence only, not validation of this new design.

Orchestrator outcome: the measured attempt stopped at 9 counted investigative
commands against hard limit 8, before successful session completion. The
planner's six-command statement below is its own count, not the retained meter.
One Astra/high model session did run; "no model sessions" above means no
additional sessions launched by that child. The saved split verdict validated
against the pre-note card snapshot, but does not erase the safety stop. It is
retained as historical at
`.runtime/changerail/ff-runs/offline-fix03b-design-eNVZfB/validated-stage-verdict.json`;
this outcome note changes the card fingerprint, so no current successful FF
verdict or admission is claimed. No new model attempt or budget reset followed.

Successor-planning outcome: actual backlog cards 03B1 (A) and 03B2 (B) now
contain standalone ordered Tasks/Verify, explicit budgets/checkpoints and the
full C1-C6 lane mapping. The parent stays an unimplemented SPLIT_REQUIRED
aggregate; its old Change Set/Change sections and Verify are retained history,
not delivery authority. 03C/03D dependency paths now name the two deliverable
successors. This board-only update is not another measured FF session, a
successful current verdict, admission, implementation or publication.

Later operator-approved routing update: 03B1 has independent offline acceptance
at `.runtime/changerail/offline-rereview-fix03b1-4x0gJ2/assessment.json`, not a
literal done transition. 03B2's real interface checkpoint rejected its old
125-line/25-minute estimate and it now remains a superseded aggregate with
full preserved C1-C6 coverage across actual successors:
`openspec/board/5.canceled/chrl-fix-03b2p-retain-pre-review-verification-proof.md`
then `openspec/board/5.canceled/chrl-fix-03b2f-retain-final-verification-proof.md`.
03C/03D follow the final successor, transitively pre_review; neither aggregate
03B nor 03B2 is a done dependency or runner input. Old two-successor estimates
and routing above are retained history; no total-work reduction or admission
is inferred from splitting lanes.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03b-record-terminal-check-identity`

### Why

An after-only fingerprint and process exit do not establish current verification.

### Goal

Produce terminal, uniquely retained run-bound records and intact logs.

### Scope

Existing producers and the small execution-result schema/helpers only.

### Ordered Tasks

1. Reproduce focused zero-exit drift and missing/incomplete log proof in real isolated fixtures; retain a failing regression before changing the producer.
2. Add the closed record and terminal-after-log writing; preserve general repair execution and the existing aggregate drift comparison.
3. Prove C1/C2 and repair compatibility; compare actual scope/size before Change 2.

### Acceptance

- C1/C2 and the repair portion of C5 have meaningful before/action/after proof.

### Depends On

- none

## Change 2: `chrl-fix-03b-validate-retained-check-consumption`

### Why

A trustworthy producer is insufficient if reuse still trusts old booleans.

### Goal

All existing consumers distinguish valid current proof from history/uncertainty.

### Scope

Result readers, summaries, focused-repeat and configured-floor reuse only.

### Ordered Tasks

1. Integrate one bounded validator into current consumers, including carried-summary classification, without altering recovery eligibility or command authority.
2. Prove C3-C6 with missing/damaged/foreign proof and valid-control fixtures; do not fake the validators under examination.
3. Update the canonical contract/runbook and Result/Log, retain final focused evidence, then use the authorized completion boundary.

### Acceptance

- C3-C6 pass without claiming concurrent duplicate prevention or condition-level proof completeness.

### Depends On

- Change 1

## Log

- 2026-09-06T12:56:20Z Operator-authorized board-only refinement of the parent's second boundary. Declared a 30-minute/280-line candidate after inspecting existing producer/reuse seams. No implementation, tests, FF movement, pilot or publication ran.
- 2026-09-06T13:32:22Z Ordinary offline Change 1 implementation retained a RED zero-exit payload-drift regression and added the focused producer/schema plus intact-proof repeat refusal. The attempted wider consumer integration was removed at the size checkpoint. Reported SPLIT_REQUIRED; no lifecycle or publication command ran.
- 2026-09-06T13:38:13Z Orchestrator rejected the partial candidate after real isolated producer/schema/reader probes. The first RED had stopped at a schema-name assertion, not the drift action; a separate preserved-baseline probe reproduced actual false-success and missing-log reuse. Retained the rejected candidate and restored only this attempt's code/tests/schema to their prior state. No acceptance or implementation completion is claimed; see the retained orchestrator assessment for the exact failures and preservation checks.
- 2026-09-06T13:57:23Z DESIGN only, offline board-only replan after rejected 03B: SPLIT_REQUIRED. Compared one closed jsonschema-backed record using existing producers/atomic writer; full compatible C1-C6 estimated 310-405 production/schema LOC and 40-50 minutes, exceeding unchanged 300/30 limits. Proposed A complete focused proof with all affected readers, then B configured floor/reuse/final-log proof; no sibling files created. Preserved Acceptance, Scope, Summary, Depends On, Verify, Change Set and both Change sections; marked old task ordering obsolete/not implementation-ready. Six investigative commands; no product tests, model sessions, implementation, clean-start admission, recovery/handoff, board movement or publication. Next is outer successor planning/tasks/Verify reconciliation, not delivery.
- 2026-09-06T14:03:01Z Orchestrator retained the design as an offline planning draft after command_safety_stop (9 counted commands, hard limit 8; the prior six-command statement is not the measured count). The saved split verdict passed read-only validation against card-stage.md before this status note; it is historical, not a successful/current FF completion. No model restart, budget reset, implementation, card movement or publication. Preserve the two vertical boundaries and C1-C6 coverage for successor planning; final deterministic checks and scope audit are retained in the same offline design directory.
- 2026-09-06T14:18:25Z Created actual 03B1/03B2 backlog successor Tasks/Verify plans with full parent C1-C6 lane mapping, honest budgets and early checkpoints. Linked them here and reconciled 03C/03D dependencies; preserved parent Acceptance, old task sections/Verify and all prior history. No measured FF restart, implementation, admission, card movement, pilot or publication.
- 2026-09-06T16:45:59Z Updated current routing after the operator-approved 03B2 lane split: independently accepted offline 03B1 source -> planned 03B2-P pre_review -> planned 03B2-F final. Preserved historical aggregate Acceptance/Verify/budgets/Change sections and prior outcomes; new descendant plans, not this aggregate, carry execution scope. No parent completion, admission, product edit or publication.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.
