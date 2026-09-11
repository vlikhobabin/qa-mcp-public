# Local ChangeRail wiring

## Purpose

Provide project-owned measured delivery without an external ChangeRail checkout,
while preserving historical planning and runtime safety boundaries.

## Requirements

### Requirement: Ordinary native delivery follows stock artifact ownership
New executable cards SHALL explicitly select `openspec-v1` and link one complete
stock OpenSpec change. ChangeRail SHALL preserve frozen historical artifact bytes
while admitting newly linked native artifact trees. Unowned additions and changes
inside frozen trees MUST be refused.

#### Scenario: New native plan is admitted
- **WHEN** the public `native-accept` command receives a complete locally linked native plan
- **THEN** dry-run validates without moving the card or writing an accepted-plan receipt
- **AND** ordinary admission retains its exact contract and moves only that card to todo
- **AND** semantic plan edits require explicit reacceptance rather than rewriting the receipt

### Requirement: Native review follows semantic sync and exact archive
The native runner SHALL assign unfinished task groups to fresh implementation
sessions and require checked upstream tasks plus current QA evidence at completion.
A separate aggregate session SHALL semantically synchronize delta specs before
independent review. The host SHALL archive only the reviewed artifact tree,
preserving canonical and product bytes, and continue the same reviewer thread
and cycle for the final fingerprint. QA observation contracts remain mandatory.

#### Scenario: Native card reaches final verification
- **WHEN** the independent active-change review returns a preliminary GO
- **THEN** the host performs stock archive with previously synchronized specs and retains the exact move
- **AND** fingerprint-invalidated QA evidence is refreshed without claiming old checks ran again
- **AND** the reviewer continues on archived paths before a final GO can authorize the configured floor

#### Scenario: Stock archive is interrupted after moving files
- **WHEN** the exact archive move completed but its final receipt was not retained
- **THEN** the runner reconciles the existing destination against its pre-move intent, raw artifact hashes and unchanged outside payload
- **AND** it refuses an unrelated edit instead of repeating sync or declaring an unproven archive complete

### Requirement: Static evidence-plan admission

Fresh board admission SHALL require one closed `qa-mcp.card-evidence.v1`
declaration. Every top-level Acceptance bullet SHALL use a unique `[C<number>]`
ID; Design SHALL declare risk decisions; tasks/admission SHALL map every ID once
and assess all six risk kinds exactly once using inert repository-relative file
locators. This structural check SHALL not execute locators or certify observed proof.

#### Scenario: Invalid new declaration is refused without changing recovery

- **WHEN** a fresh candidate has a missing, malformed or versionless declaration
- **THEN** direct and FF admission reject it before a todo transition with a
  concrete migration diagnostic rather than SPLIT_REQUIRED
- **AND** exact retained recovery continues through its existing branch without
  a new legacy waiver or mutation.

### Requirement: Operator-controlled numerical budget enforcement

The profile SHALL distinguish numerical delivery ceilings from mandatory
authority/evidence gates. With `budgets.enforce_limits=false`, admission size
estimates, session elapsed time, investigative command counts and delivery
review/repair counts SHALL not stop authorized work. Measurements and inherited
attempt history SHALL remain available; the old limits SHALL not be reported met.

#### Scenario: Work exceeds a reference budget

- **WHEN** numerical enforcement is disabled and an otherwise valid card or session exceeds a stored reference
- **THEN** admission and useful authorized execution continue without budget-only SPLIT_REQUIRED, timeout, verdict-only or cycle-exhaustion failure
- **AND** real command/time/review usage is retained and incomplete verdicts are not accepted
- **AND** malformed cards, unsafe evidence, role violations, invalid recovery and unauthorized publication/runtime operations still refuse.

### Requirement: Exact retained recovery proof

Recovery SHALL admit only a sole active card whose current whole dirty worktree
exactly matches a regular, run-local retained manifest: card and run identity,
baseline HEAD, complete payload fingerprint and exact per-path fingerprint map
all agree. A delivery-manifests pointer is discovery metadata, not proof.

#### Scenario: Retained proof is missing or stale

- **WHEN** a retained manifest has missing, malformed, duplicate, extra or
  mismatched fingerprint fields, an unsafe run/path/source symlink, changed
  bytes, mode/type/link-target drift, a renamed card, an unlisted dirty file or
  a changed baseline HEAD
- **THEN** doctor and recovery refuse read-only before a new run or model call
- **AND** no manifest, counter or historical record is regenerated or changed.

#### Scenario: An older exact source survives an empty aborted placeholder

- **WHEN** a newer empty aborted-run placeholder or inconsistent pointer exists
  beside an older exact run-local manifest
- **THEN** recovery may select only the exact older run-local source and never
  derives proof from the pointer.

### Requirement: Local workflow authority

The project SHALL own its scripts, skills, schemas and executable wrappers.
Codex SHALL discover local chrl skills; Claude commands SHALL delegate measured
delivery to Codex. Domain/project skills SHALL retain their owners.

#### Scenario: Local startup

- **WHEN** the QA launcher composes its runtime home
- **THEN** local chrl and existing project/domain skills are available
- **AND** no workflow skill or helper requires /opt/changerail.

### Requirement: Explicit role routes

The runner SHALL request gpt-6-astra/high for FF and fresh review, and
 gpt-5.6-terra/high for implementation and repair, retaining CLI route evidence.

#### Scenario: Resumed planning and repeated review

- **WHEN** FF resumes or the runner requests a delta review
- **THEN** the configured Astra/high route is supplied explicitly
- **AND** missing routes and unsupported reasoning fail without silent fallback.

### Requirement: Preserve legacy lifecycle

New work SHALL use complete board cards and direct canonical-spec updates.
Pre-migration lifecycle artifacts SHALL remain byte-identical to their inventory.

#### Scenario: Legacy history coexists with board-only planning

- **WHEN** the inventoried legacy files are unchanged
- **THEN** their presence does not block an otherwise admissible new card
- **AND** new, changed or deleted lifecycle files are rejected.

### Requirement: Exact historical activity classification

The workflow SHALL recognize only the four original path/hash identities pinned
in `FROZEN_BOARD_RECORDS`: OSS-06-S1, OSS-06-S5 and OSS-07 as
`superseded-no-go`, and OSS-06-I13 as `suspended-not-verifiable`. It SHALL check
current regular-file bytes and non-symlinked ancestry before every exclusion;
missing, moved, edited or symlinked originals SHALL fail closed without hash
regeneration or caller-configurable waivers.

#### Scenario: Historical records coexist with an active lane

- **WHEN** the four exact unchanged originals are present
- **THEN** doctor and the shell start guard report the two historical groups separately from actual activity
- **AND** an unlisted fifth card, including a similarly named copy, counts as active and blocks another start
- **AND** recovery still requires the sole matching real active card, retained manifest and explicit bounded objective
- **AND** a dependency on a historical source remains unsatisfied without substituting its successor.

#### Scenario: A caller tries to revive a frozen source

- **WHEN** a frozen source is selected for admission, FF/resume, start/recovery, review, handoff or publication
- **THEN** the entrypoint rejects it before lifecycle edits, evidence writes, agents or publication
- **AND** the already-inprogress and dry-run branches of board-do also reject it
- **AND** ready-looking metadata or retained verdict/recovery state grants no execution authority
- **AND** read-only inspection may explain disposition, without certifying I13 or treating I16 omission as replacement.

#### Scenario: Normal transitions maintain links without rewriting history

- **WHEN** normal FF or publication moves a live card
- **THEN** live references are updated while all four originals remain at their exact paths with identical bytes
- **AND** only outbound links inside verified frozen sources cease to be live-maintained
- **AND** ordinary live/product dangling links still fail and original integrity is checked before exclusions
- **AND** frozen paths stay fingerprint-visible while lifecycle inventory and completed/canceled history remain unchanged.

### Requirement: Verification and authorization boundaries

The runner SHALL bind verdicts and evidence to the payload, retain bounded
recovery and require fresh GO and final checks before publishing. Runtime/auth
state SHALL remain excluded. The migration pilot SHALL require prior agreement.

#### Scenario: Installation readiness does not authorize a pilot

- **WHEN** local wiring and offline migration checks pass
- **THEN** the result is installation readiness only
- **AND** no real card, runtime action, commit or push starts automatically.

### Requirement: Focused checks retain terminal run-bound proof

The existing focused argv entrypoint SHALL require actual owning run/card
metadata and retain unique running/terminal `qa-mcp.check-result.v1` records.
The closed schema and one schema-backed reader SHALL reject malformed,
unknown/duplicate-key, unsafe, foreign, stale and incomplete proof. Recorded
process exit SHALL remain distinct from the wrapper verification result.

#### Scenario: A focused child exits zero while changing payload

- **WHEN** a real focused child changes the tracked payload and exits zero
- **THEN** before/after fingerprints and actual exit zero are retained but the caller fails with unconfirmed proof
- **AND** spawn/interruption and retention failures never invent successful process completion
- **AND** terminal success is published only after complete regular log retention with byte size/SHA-256, including valid silent zero-byte output.

#### Scenario: Focused readers consider current or historical evidence

- **WHEN** repeat detection, summaries or metrics encounter focused results
- **THEN** current proof requires matching owner/invocation/lane/exact command, unchanged current payload and intact log through the sole validator
- **AND** component-safe regular-file access precedes record/index/log content reads; bounded reads never authenticate a truncated prefix
- **AND** intact repeats refuse with their retained reference, while invalid proof is no cache hit and original records/logs remain unchanged
- **AND** metrics remain compatible observations; legacy and carried recovery/review projections stay historical/unconfirmed without cross-run adoption or changed accounting/eligibility.

#### Scenario: Focused proof coexists with other workflow boundaries

- **WHEN** focused terminal proof is enabled
- **THEN** configured verification/final-log behavior and intentional changed-payload repair retain their separate existing contract
- **AND** no condition-proof binding, single-flight, command/model/budget/role change, finalizer enablement, pilot or publication authority is implied
- **AND** endpoint identity does not prove no transient edit/revert, semantic test adequacy, hostile-writer resistance or all-environment reproducibility.

### Requirement: Pre-review success requires complete owning command proof

Configured pre-review commands SHALL use the shared check-result schema and
reader, with exact shell text/argv retained before launch. Unique attempts SHALL
belong to their run/cycle outside focused evidence. Actual outcomes SHALL remain
separate from verification success, including failed retention after exit zero.

#### Scenario: Pre-review execution and reuse

- **WHEN** preverify executes or a handoff/review/final prerequisite consumes preverification
- **THEN** current success requires the exact ordered configured sequence of unique, owning pre_review receipts, each with unchanged current payload and intact regular log
- **AND** unsafe or malformed owner/index/record/log content is refused through bounded component-wise no-follow reads
- **AND** per-command drift or unconfirmed execution stops later commands, independently of the aggregate before/after comparison
- **AND** intact reuse launches no child; invalid proof is not a cache hit and new authorized attempts preserve historical cycle indexes, records and logs.

#### Scenario: Pre-review proof preserves adjacent boundaries

- **WHEN** configured pre_review proof is enabled
- **THEN** metrics remain safely typed unconfirmed observations without focused double-counting or historical proof adoption
- **AND** a missing or damaged log preserves safely decoded command/exit/duration/time observations and does not hide intact sibling rows; invalid numeric durations contribute no timing
- **AND** preliminary and repeated owner reads in final/review prerequisite paths use the same bounded no-follow reader before content consumption
- **AND** deliberate scoped import repair can succeed with changed payload but cannot establish unchanged verification proof
- **AND** no condition binding, model/budget/role/floor change, pilot, finalizer or publication authority is introduced.

### Requirement: Run-local verification attempts are serialized

Focused evidence, pre-review proof and final proof SHALL share one nonblocking,
regular no-follow kernel lock per owning run. The holder SHALL retain that lock
from owner/payload/command revalidation through cycle and attempt allocation,
child completion and receipt/index publication. The shared-floor adapter SHALL
acquire the same boundary when called directly and SHALL not recursively acquire
it when an entrypoint already owns it. A direct shared-floor caller SHALL decide
whether an existing validated completed result matches its current lane, commands
and payload while it owns that boundary and before it allocates a cycle or
launches a child. Internal helper delegation SHALL require
an active process/run-scoped lock capability, not a caller-supplied flag.

#### Scenario: Concurrent and interrupted check entries fail closed

- **WHEN** a second check entry reaches the same run while a configured child is held
- **THEN** it launches no duplicate child and reports busy or reuses only after its own locked revalidation
- **AND** changed commands, payload or owner observations before lock acquisition do not authorize stale reuse or allocation
- **AND** a safely decoded running receipt from any lane remains unresolved after its parent dies, even if the kernel lock is free or its child PID is absent, reused or later exits
- **AND** an observed terminal failure releases the lock for a later already-authorized call, while damaged terminal proof never becomes success and prior cycles/attempts remain byte-preserved.
- **AND** a start-intent bound to the existing receipt identity remains unresolved when its receipt is absent, unreadable, invalid, `running`, `interrupted`, or `unknown`; only observed exit or spawn-failure outcomes release that ownership.
- **AND** direct shared-floor calls re-read the configured command set under the acquired lock and refuse stale supplied command text before cycle allocation or child launch.
- **AND** a contender observed after a child exits but before terminal receipt or aggregate-index publication remains busy until the holder publishes; only then may an unchanged completed configured request reuse validated proof without a second cycle.
- **AND** this adds no orphan cleanup, automatic retry, scheduler, cross-run adoption, condition binding, finalizer, pilot or publication authority.

### Requirement: Complete final proof and exact-byte delivery summaries

Configured final commands SHALL use the same receipt schema, executor and ordered
set predicate as pre_review, with an explicit final lane. Every current reuse,
summary and publisher evidence decision SHALL require complete current owning
proof, not a loaded mapping or an exit-only aggregate.

#### Scenario: Final execution, reuse and reporting

- **WHEN** the existing runner-owned final caller executes after its fresh GO, manifest and preverification gates
- **THEN** exact shell identity and before-payload precede each launch, and real terminal outcomes and complete regular logs precede atomic terminal proof
- **AND** per-command drift, failed execution or retention stops subsequent commands independently of aggregate start/end equality
- **AND** reuse requires the exact ordered unique final receipt set and current payload; equal pre_review commands cannot supply final authority
- **AND** every due final test observation names the exact final-lane receipt,
  attempt, command identity and selected-node spans from that current validated
  set; a focused/pre_review or unrelated final receipt cannot cover it
- **AND** bounded component-wise no-follow reads protect owner, index, record and log content, including preliminary and repeated reads
- **AND** authorized reruns allocate fresh cycles without rewriting historical proof; final metrics retain typed unconfirmed observations without lane double-counting.
- **AND** foreign lane/run/card/invocation references do not contribute execution count or duration, while damaged own logs preserve their observed fields and intact siblings; distinct invocations with repeated command text remain separately counted.

#### Scenario: Publication consumes the same validated bytes

- **WHEN** the existing publisher consumes final evidence before card or Git mutation
- **THEN** incomplete, malformed, foreign, stale or damaged final proof refuses admission while preserving the card and index
- **AND** the receipt and pytest summary consume the exact bytes returned by that complete-set decision without reopening logs or trusting a decoded mapping
- **AND** silent output and commands without pytest do not fabricate a summary; a required pytest summary missing from validated bytes prevents finalization
- **AND** existing publication transactions, role gates, focused/pre_review proof and deliberate changed-payload repair remain unchanged; no FIX-02 enablement or new publication authority is introduced.

### Requirement: Versioned observed proof covers every declared condition

New delivery runs SHALL select `qa-mcp.observed-proof.v1` before their first
metadata write. One current source-card hash-bound inventory SHALL feed handoff,
review context/verdict, final verification and the pre-mutation publisher gate.
V1 records remain readable only on their recorded legacy path; a caller flag,
missing field or copied summary SHALL not downgrade a newly selected run.
The v1 path SHALL additionally require its independently pinned run, manifest,
card, baseline and current whole-payload recovery admission. A closed
continuation may name that exact source before recovery metadata is written; it
shall not rewrite the source contract, counters, manifests, sessions or history.
That creation record SHALL retain a closed successful-admission snapshot. Later
continuation consumers SHALL independently revalidate the immutable origin
authority as well as immediate-predecessor admission; a self-described
selection/admission hash is not an origin anchor. They revalidate immutable
source run/manifest provenance, but
authorize Result/Log and implementation changes through the continuation's own
current manifest, receipt, role and fingerprint gates rather than comparing the
mutable live card to the original source-card hash.
Migration is a separately explicit scoped fixture/internal interface and never
follows from an omitted field. A v2 context SHALL reject raw `bootstrap_plan`
metadata rather than treating it as an unadmitted inventory source.

#### Scenario: A condition crosses implementation, review and final boundaries

- **WHEN** a current versioned run records or consumes a condition observation
- **THEN** source path/hash, namespaced condition, declared method/stage, owning
  run/payload, recorder role and retained artifact bytes are revalidated
- **AND** handoff requires only implementation rows, review requires meaningful
  typed references and semantic decisions, and final rows remain `pending_final`
  until the outer final lane records them
- **AND** missing, duplicate, foreign, stale, failed or planned-only rows refuse
  before handoff reuse, verification reuse or publisher mutation
- **AND** typed integrity does not classify test relevance or risk adequacy;
  those remain the independent reviewer's explicit assessment.
- **AND** a test observation binds actual selected receipt nodes and byte spans
  to declared test-file or exact-selector locators, and binds current inspected
  before/action/after assertion-source fragments; headers, totals, unrelated
  log text and exit zero are unconfirmed.
- **AND** every supported nested inspected-source reference is a closed safe
  path/nonnegative-integer-size/SHA-256 reference validated before a read or
  equality comparison; runtime observations support an empty source list only.
- **AND** final proof is supplied only by the explicit outer dispatch under its
  existing lock through validated receipt/typed-artifact boundaries; reuse
  revalidates implementation, review and final proof without recreating a
  deleted or corrupt final observation.
- **AND** offline reports retain the same closed informational observation
  shapes only under their owned offline root. They reject measured cross-import
  in either direction and do not establish handoff, GO, runtime or publication
  authority.

### Requirement: Explicit offline-amendment finalization

The CHRL-FIX-02 implementation SHALL keep this lane default-disabled.
Readiness, independent acceptance and execution authority are
separate: historical checkpoint counts do not establish current acceptance,
and offline verification never enables either public entry mode.

The runner SHALL accept only the closed `qa-mcp.offline-finalization.v2` request
for this lane. A read-only check binds no-follow request/source/plan bytes,
source run and manifest digests, terminal root lineage with complete inherited
usage, baseline, complete payload, typed mode/kind/deletion amendments, frozen-
aware sole activity, supporting-plan hashes, inert observation drafts and a
pinned remote/ref identity before reserving anything. A request's claimed
authority records scope only; execution authority is never inferred from it.
Authority/objective narratives and every amendment reason SHALL contain
non-whitespace text without normalizing the request bytes used for admission.

After all checkpoints are independently accepted, the implementation MUST retain
one root-keyed attempt and a nonblocking no-follow flock over all child/receipt/
publication work. Its source history MUST be immutable; unknown child ownership,
terminal NO-GO/red floor, corrupt proof or byte drift MUST refuse rather than
repair or allocate a successor. A distinct `finalizer` producer MAY record only
implementation-stage observations through its checked attempt admission;
ordinary roles and review/final ownership are unchanged. The existing publisher
MUST journal parent, transform scope, tree, commit and pinned remote/ref before
their effects and use an explicit non-force ref push.
Every finalizer producer and proof consumer SHALL bind the physical attempt to
the root-derived reservation and immutable creation selection. Finalizer-owned
writes require current root-lock ownership; an ordinary retained proof cannot
gain finalizer authority through a coherently changed role and index hash.

Execution SHALL require nonempty explicitly trusted configured
`offline_finalization.evidence_commands` before reservation; inert Verify
locators and request drafts SHALL NOT select commands. Each post-child consumer
SHALL revalidate original request/source/plan bytes and full observed coverage
before the next child or publication effect.

An interrupted review MAY be reused or retried only through its actual
launcher allocation and exact context/verdict destination. Its termination
receipt SHALL bind the owning intent, reaped session metadata and usage-event
bytes. GO reuse additionally requires the exact completed verdict receipt;
incomplete retry requires demonstrated termination, intact current evidence
and retained cumulative usage. Live/unknown ownership, foreign or corrupt
session material and terminal NO-GO/red floor SHALL refuse without a new child.
Completed reviewed/final/publication stages, including original-view recovery
after card movement, SHALL retain and validate that same owner and completion
closure. Completed session accounting inputs SHALL remain byte-identical and
cannot be deleted or extended to revise cumulative usage. Offline launcher
metadata/events and review receipts SHALL use no-follow owned descriptors,
exclusive temporary files, regularity/race checks and file/directory fsync;
certified dependencies SHALL be durable before receipt and parent advancement.
The dependency closure SHALL retain and revalidate the flushed file objects,
content and no-follow ancestry through receipt and parent installation; matching
bytes on a replacement inode SHALL NOT inherit an earlier object's fsync.
Parent advancement SHALL consume dependency references from checked completion/
termination receipts rather than renew their digests from later file contents.
Installed parent, session-receipt and setup/history outputs SHALL remain bound
by descriptor/object/content through every enclosing directory flush before
their writer returns; validating only input dependencies is insufficient.
Offline review setup/history outputs (lock, cycle manifest, payload diffs,
context and retained verdict history) SHALL use that owned storage boundary,
refusing unsafe/conflicting output ancestry, leaves and temporary entries before
model launch when present at setup. Ordinary delivery writers remain separate.
Offline history SHALL use the exact verdict reference certified by the completed
review-result writer, verify the supplied history bytes against it, and retain
its source through the history output's last flush. A later independent read
SHALL NOT mint the expected identity or record an unissued verdict.
The offline context SHALL bind producer-byte references for its generated cycle
manifest and every indexed diff. Their complete input group SHALL remain held
with the context through its last flush and SHALL be revalidated by completion
and recovery consumers, without deriving expected hashes from substituted files.
Before terminal manifest installation, a distinct closed manifest producer intent
SHALL persist the creation-pinned initial manifest reference, exact produced after
reference, fixed publish metadata/timestamp and known produced pushed-journal
reference. It is not a completed receipt. Recovery SHALL validate the current
before/after bytes and deterministic transition against that retained expectation,
not hash an unpinned installed output to renew authority. Missing intent after
installation, changed bytes, another valid timestamp or unsafe/conflicting inputs
SHALL refuse before later writes unless independently retained legacy pins already
certify the output. An uninstalled producer draft SHALL NOT pin a never-produced
timestamp. The producer parent SHALL hold its exact before, same checked origin
and journal through its own last flush. Manifest installation SHALL hold the
known certified producer parent, origin, journal and produced output through its
own last flush/return, re-flushing admitted producer records on recovery.
The terminal run writer SHALL hold its checked or producer-bound publication
manifest through installation and all enclosing flushes. Its manifest reference
SHALL be persisted before run installation, retained with the completed run
reference in terminal accounting, and checked on restart rather than renewed.
A distinct closed incomplete run-write intent SHALL retain the exact manifest
reference and before/after producer identities before run installation. Intent
is not a completed receipt. Its before identity SHALL come from the retained
creation producer, not current run bytes, and the checked creation snapshot
SHALL itself remain held by the parent and outer dependency groups. The intent
origin comparison and dependency retention SHALL consume the same checked
snapshot, not a new expected hash from a subsequent creator read. The intent
parent SHALL hold its exact before input through its own last flush, then retire
that phase-local lease before intentional run replacement. Installation SHALL
check and re-flush expected-before, including an accepted same-byte replacement.
Manifest pin and intent SHALL be installed atomically in one parent record.
A legitimate interruption before this later run-intent group has neither member,
but the previously installed manifest SHALL retain its separate producer intent.
Restart SHALL validate the creation-pinned run before-state before further writes. A retained manifest-only
group without intent SHALL refuse even while run remains before-state; neither
lost intent nor changed current bytes SHALL renew the producer expectation.
Restart
SHALL compare against the retained before/after identity and validate the producer
transition while before-state exists. Installed output without that intent or
an independently completed legacy pair SHALL refuse, not establish its own pin.
The run writer SHALL hold its known certified producer parent, manifest, origin
and installed output through its own last flush/return, not rely on a later outer
refusal. Both required expected-before receipt writers SHALL revalidate inputs
after flushing the before file and retain output object/content and no-follow
ancestry until return. Only the obsolete before-file lease ends at replacement;
ordinary generic writers remain unchanged.
The outer terminal closure SHALL share the parent's complete certified review
dependency definition, including context, cycle manifest, every indexed diff,
verdict and completed session records, with terminal manifest/run/parent outputs.
That entire group SHALL remain held through the outer last flush on direct
public recovery, without relying on a later redundant parent write.
Producer-temp, producer-installed, manifest-installed, pre-run-intent and
installed-run-intent/installed-run persistence failures
SHALL preserve exact restart without another
review/check/commit/push; substituted dependencies SHALL refuse advancement.
Recovery after interrupted receipt installation SHALL re-flush the validated
completion dependencies before advancing; readability alone is not durability.
Conflicting evidence SHALL be preserved on refusal.

Both public `finalize-offline` modes remain default-disabled pending parent-
owned independent review and final-floor evidence. The disabled entrypoint is
not pilot, publication, or finalizer authority.

For fixture-scoped offline publication, the existing publisher SHALL resolve and
pin exactly one effective push route, reject multiple routes and URL rewriting,
retain no raw route URL, and revalidate it before a non-force `commit:ref` push.
Its durable journal SHALL precede card/reference/index effects and bind the
admission, parent, original/expected scope, transformations, tree, commit intent
and upstream. A retry MAY accept only an absent remote ref, the recorded parent,
or the exact recorded commit.
Before each resumed local effect it SHALL validate the branch/full ref,
upstream, exact allowed index/worktree and HEAD. An advanced HEAD is admissible
only as the independently recognized exact intended commit. Commit creation
SHALL control author/committer overrides, and recognition/push SHALL compare
both actual identity digests to the pinned intent, alongside message and times.

#### Scenario: Changed payload receives one fresh bounded decision

- **WHEN** an exact stopped delivery payload is adopted through an eligible request
- **THEN** the old run and its review counters remain unchanged and one profile-owned fresh review, final floor and existing publisher operate on the adopted payload
- **AND** old GO/evidence, unlisted paths, stale bytes, another active card, dirty index, symlinks, a failed review/floor or a repeated lineage attempt prevent publication
- **AND** an interrupted reviewer resumes the same attempt, while a retained commit with an uncertain push does not create a second review or commit.
