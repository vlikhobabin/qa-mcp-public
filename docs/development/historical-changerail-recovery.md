# Historical ChangeRail recovery and one-off exceptions

This document preserves the pre-`openspec-v1` board-only workflow, frozen-run
rules, offline amendments and pilot-specific authorizations. It is not the
ordinary route for a new card and grants no permission by analogy. Use
[native OpenSpec delivery](native-openspec-delivery.md) for new work.

The stopped OSS-FIX-01 pilot remains historical; its one-off closure is recorded
in the done card and `native-transition.md`. The CHRL-FIX offline correction queue
retains its own Result/Next sections and original runtime receipts.
The roadmap checkpoint and `roadmap-continuation-prompt.md` are the current
handoff sources; no old GO or composed test summary authenticates later bytes.

The QA fork comes from meta-mcp commit
`69ad52f57607e3e1cc60f234b230edcd5fd49c9f`. Source hashes and MIT provenance are
in `tools/changerail/upstream-snapshot.json` and `ORIGIN.md`. Runtime code is in
`scripts/changerail/`, skills/schemas in `tools/changerail/`, settings in
`.changerail/profile.toml`. No delivery depends on another checkout.

## Installation and checks

```sh
uv sync --extra dev --locked
./bin/chrl install
./bin/verify-project
./bin/openspec validate --specs --strict --no-interactive
```

Install changes only this repository's `core.hooksPath` to `scripts/git-hooks`.
The old root hook only enforced external ChangeRail symlinks; the local hook
replaces that obsolete requirement with local wiring/history validation,
staged whitespace and focused harness tests when harness paths are staged.
It does not run the full product suite on every commit.

`bin/codex` retains the QA proxy/auth convention and composes a fresh local
runtime home under `.runtime/changerail/codex-home`, with the local workflow and
existing domain/project skills. `.codex/config.toml` remains the project config;
its tracked changes participate in payload fingerprints. Auth/session material
stays excluded. Claude exposes `/chrl:ff`, `/chrl:deliver`, `/chrl:review` and
the corresponding `/changerail:*` command aliases. Measured execution and
publish-valid fresh reviews use Codex; Claude advisory review cannot mint a GO.

## Planning and authorized delivery

```text
chrl-ff: proposal -> specs -> design -> tasks inside one backlog card
         -> deterministic admission -> todo
chrl-run: clean doctor -> ordered Change checkpoints -> focused evidence
          -> handoff/preverification -> fresh review -> bounded repair
          -> final floor after GO -> done -> one commit -> one push
```

`./bin/chrl-ff <backlog-card>` requires a tracked, clean card in primary main.
A complete operator-refined plan takes deterministic admission; accepted todo
cards skip FF. `./bin/board-ff --dry-run <card>` checks admission without moving
it. `./bin/chrl doctor --no-remote <todo-card>` is a read-only readiness check.
`board-do` is the runner's transition helper; its former `--exec` shortcut now
fails before mutation. It must not launch an unmeasured implementation session
or silently upgrade a code-only request into commit/push authority.

**`./bin/chrl-run <todo-card>` includes commit and push.** Invoke only when that
full delivery is authorized. `require_push=false` controls the remote preflight,
not publication; it is not a no-push switch. Ordinary implementation or review
does not imply publication authority. The migration pilot additionally needs
separate prior agreement, even after installation and offline checks are green.

One accepted card has one invariant, contiguous Change sections and the declared
Delivery Budget. Operator policy sets `budgets.enforce_limits=false`: numerical
admission ceilings, session timeouts, command stops/verdict-only thresholds and
review/repair cycle limits are informational. Keep realistic estimates and all
measured usage, including interrupted attempts; do not reset history or force
a split solely on time/size. The stored numerical references remain usable if
an operator explicitly re-enables enforcement. Card/evidence structure, scope,
clean-start/recovery integrity and all role/runtime/publication gates remain.
I/O size bounds, output truncation and process cleanup grace periods are safety
or transport constraints, not delivery budgets, and remain enforced.

Fresh admission also requires a static `qa-mcp.card-evidence.v1` declaration:
unique `[C<number>]` prefixes on all top-level Acceptance bullets, one Design
section, and one JSON block in Verify. It checks only closed structure, exact
condition/risk mapping and inert repository-relative file locators. A missing
or invalid declaration is an exit-2 migration refusal, not SPLIT_REQUIRED;
existing exact recovery deliberately skips fresh admission. Focused execution
receipts, final-floor proof and condition-to-observation enforcement are described
in the corresponding sections below. Static admission alone supplies no execution
proof.

### Focused execution receipts

`chrl evidence` requires the actual current run/card metadata before launching
its existing argv command. Each exclusive attempt retains a running record,
then complete stdout/stderr bytes (in concatenation order) and an atomic terminal
`qa-mcp.check-result.v1` record. Actual process exit is separate from the wrapper
verdict: exit zero with payload drift or failed retention returns failure.
Unknown/interrupted/spawn outcomes never imply observed exit zero.

One closed schema-backed reader checks owning identity, current before/after
payload and complete regular log size/SHA-256 before repeat refusal or a current
summary. All components below the repository are opened without following links;
JSON/index reads are bounded to 256 KiB, logs to 32 MiB. Exceeding a limit is
unconfirmed, never prefix-only proof. Silent zero-byte logs are valid. Intact
repeat refusal cites its retained record; invalid proof is not a cache hit and
an authorized new attempt never overwrites old evidence.

Metrics retain observation fields. Legacy and copied recovery/review summaries
are historical/unconfirmed; fingerprint equality alone cannot upgrade them or
grant cross-run reuse. Historical records, accounting and recovery eligibility
are not rewritten. Both configured lanes use the proof boundary described below.
Deliberate changed-payload
shell repair remains separate from unchanged verification success.
Receipts do not bind Acceptance conditions, prove test relevance, prevent
concurrent duplicate execution, detect transient edit/revert, authenticate a
hostile writer or establish environment reproducibility. They add no pilot,
finalizer, live-operation or publication authority.

### Pre-review configured proof

`preverify` explicitly opts into the same receipt contract, retaining exact
`bash -lc` argv and configured shell text before each child. Attempts live in
exclusive preverification cycles, not focused-evidence. Per-command drift,
nonzero/signal/spawn/interruption and retention failure stop the sequence; the
independent aggregate before/after gate remains in place.

Reuse and the shared handoff/review/final prerequisite safely read the owning
index and validate its complete ordered unique receipts and exact current
payload. Legacy exit-only indexes cannot authorize reuse. Only the current
index alias advances on a new authorized attempt; previous cycles and attempts
remain unchanged. Metrics expose typed unconfirmed observations, never a
second proof authority or focused count.
Broken log proof does not erase the safely decoded observation or later rows
in the cycle; malformed numeric durations are omitted from timing. Preliminary
and repeated owner reads in final/review paths use the same safe reader.

The existing scoped import sorter may
still exit zero while changing imports; that is repair success, not unchanged
verification.

### Run-local serialized verification attempts

Focused evidence, `preverify`, `verify` and a direct configured-floor call use
one nonblocking regular no-follow `flock` per retained run. The holder rereads
the owner, payload and configured commands after acquisition, then retains the
boundary through cache/reuse decision, cycle and receipt allocation, child
completion, and index publication. Entry points pass that ownership to the
shared floor; a direct floor call takes it itself, so the lock is never nested.
That delegation uses an active process/run-scoped capability, not a boolean or
caller assertion; direct focused/floor helpers acquire the same boundary before
they can allocate or launch. The direct floor rereads its lane's configured
commands after acquisition and refuses stale supplied text. Before allocation it
also uses the existing completed-result validator with that current
lane/command/payload binding, so a caller that was waiting to acquire after a
successful peer reuses the validated result instead of allocating another cycle.

The boundary is observable through actual child exit and real terminal receipt
publication, and through configured aggregate-index publication. A contender in
either post-child window remains busy; after publication, unchanged configured
preverify/final callers may reuse the validated result. A payload-only change at
acquisition never reuses a proof with the former fingerprint: final gates refuse
stale prerequisites, while a direct current-state call may create a fresh current
cycle under the same lock. These checks introduce no cache format, scheduler or
publication authority.

A busy contender launches no child. A safely decoded `running` receipt in any
check lane is an unresolved invocation, not evidence of completion: it refuses
later checks even if the original verifier parent has died, the kernel lock is
free, the child PID is missing/reused, or the child later exits. The runner does
not kill, adopt, reconcile or automatically retry that child. A normal durable
terminal failure is different and releases the lock for a later authorized
call. Existing receipt validation remains the sole proof format; corrupt
terminal receipts cannot become reuse. This run-local boundary changes neither
final-role/GO/manifest/preverification gates nor FIX-02, publishing, pilots or
cross-run authority.

Each new receipt also has a small run-local start-intent bound to its existing
attempt identity. It records ownership, not proof or log integrity. A missing,
corrupt or invalid receipt therefore cannot erase an unresolved start. Terminal
`interrupted` and `unknown` observations remain unresolved; only an observed
process exit (including nonzero/signal) or a spawn failure releases the intent.
Damaged proof for an already observed terminal outcome still cannot become
success, but it does not turn normal authorized retry into an orphan refusal.

### Final configured proof and delivery summaries

The existing runner-owned `verify` retains its role, fresh GO, manifest and
current preverification prerequisites. It uses the same producer and complete
ordered-set predicate with an explicit `final` lane. Each child and the entire
sequence must preserve their respective before/after payloads. Equal command
lists do not transfer proof between lanes. Missing or damaged logs invalidate
reuse; only an authorized caller may create a fresh cycle. Historical attempts
remain unchanged and final metrics stay typed, unconfirmed and lane-separated.
Observation salvage is identity-scoped: foreign lane/run/card/invocation or
out-of-run receipt references do not count as local final executions. Damaged
own logs still retain observations; distinct invocations with identical command
text are counted separately.

At the existing publisher evidence gate, owner/index/record/log reads are
bounded, regular and component-wise no-follow, including preliminary/repeated
owner reads. A private set result carries validated records and their exact log
bytes into the receipt/pytest parser. A decoded index is not that result, and
the parser never reopens a log. The result is local to that decision, not a
durable reusable certificate; a later decision revalidates retained bytes.
No pytest summary is invented for silent/non-pytest output, and an expected
pytest summary absent from validated bytes still prevents finalization.
Test receipt and ordinary-offline readers use only direct `pytest`, `python -m
pytest`, or explicit `uv run` forms. Shell composition, expansion, redirects
and a command that merely prints pytest-looking text are not an invocation.
Evidence rejection precedes card movement, staging, commit and push. This
adapter changes neither those transactions nor authority: FIX-02 remains
disabled and offline implementation is not permission to publish.

## Roles, evidence and recovery

### Observed condition proof

New measured runs pin the observed-proof contract at creation. The runner derives
one hash-bound inventory from current validated card bytes; it never executes a
declared locator. Implementation records implementation rows, independent review
records review rows, and only the outer runner records final rows. The proof index
is run-local, immutable-by-record and protected by the existing attempt lock.
Typed artifacts are bounded, regular, contained in the owner run and hash-checked.
Their nested `inspected_sources` references use the same closed path/size/SHA-256
reader as other references; `size` is a nonnegative integer, never `bool`.
Inspection sources are nonempty repository files. Runtime observations support
only an empty `inspected_sources` list: their run-owned provenance and fragments
are the supported runtime evidence surface.

Handoff demands implementation rows but leaves later stages pending. V2 verdicts
name every stage-specific scenario condition; `GO` cannot use a success string in
place of reviewed typed observations, and final-only rows remain `pending_final`.
Final verification and publication revalidate coverage before any mutation.
Offline reports may use the inventory shape under an offline root, but cannot be
imported into a measured run or grant finalizer/adoption authority.

A v2 review context uses only that checked inventory: raw `run.json`
`bootstrap_plan` data is an unadmitted source and refuses before context
publication. Test observations bind validated receipt bytes, selected node byte
spans and current inspected before/action/after assertion-source references;
pytest headers, totals, arbitrary log slices and exit zero alone are
unconfirmed. The runner's explicit outer verification dispatch prepares/supplies
final rows while holding the existing verification lock. It never treats a
direct floor as final acceptance, relaunches no child for valid reuse, and does
not recreate missing/corrupt historical proof.

FF and fresh reviews use `gpt-6-astra/high`; implementation and repairs use
`gpt-5.6-terra/high`. CLI arguments are explicit for new and resumed sessions.
Metrics describe the requested route; invisible provider rerouting is not proven.

The runner owns review invocation. With budget enforcement disabled, required
semantic/final-floor repairs continue without a numerical cycle stop; every
attempt and completed review remains counted. Incomplete reviewer attempts do
not become completed verdicts. Recovery inherits usage, exact dirty payload,
completed checkpoints and thread state. The optional enforced policy retains
two semantic cycles, one terminal repair and one post-floor review. Disabling
budgets does not reopen terminal offline-publication transactions or enable
FIX-02: their request/lineage authority and outcome gates are unchanged.

The implementation ends at a successful `./bin/chrl handoff <card>`. Finalize
Result/Log first, record focused evidence, then freeze the payload. The runner
performs preverification, review and final checks. A stale hash invalidates
evidence/verdict reuse. Review receives compact context and per-path diffs;
subsequent review receives changed paths plus the previous findings.

Use `./bin/chrl-ff resume <failed-ff-run-dir>` for an eligible FF recovery.
Delivery recovery uses `CHRL_RECOVERY_OBJECTIVE` with the runner's `--recovery`
option and requires an exact retained manifest for the sole active card. Exact
means the run-local retained source (not a delivery-manifests pointer copy)
matches the current baseline HEAD, card/run identity, complete payload
fingerprint and complete per-path fingerprints for the whole dirty worktree.
Missing, malformed, renamed, mode/type, link-target or byte-drift proof refuses
before a run is created; matching paths alone are not proof.
Read the generated recovery-context index instead of scanning older runs.

An exact retained v1 record is compatible only when independently pinned run,
manifest and card bytes, baseline HEAD and current whole dirty payload still
pass that admission. Its closed continuation is selected before new recovery
metadata and preserves the recorded v1 contract/accounting/history. Missing or
renamed version/selection fields, a copied owner or a caller flag never select
legacy. Explicit fixture migration may invalidate old proof but is not a
production migration authority.

At successful v1 continuation creation, the retained selection also freezes the
closed admission snapshot. Every continuation reader independently requires the
original external exact identity; a self-described selection/admission cannot
anchor it. Later readers still hash-check the original run and manifest
provenance, but they do not recompare the mutable live card with the
old card hash: authorized implementation Result/Log/code changes are current
only through the continuation's own manifest, receipts, role and fingerprint
gates. Corrupt original provenance or stale continuation evidence still refuses.
For A→B→C recovery, B first proves its own exact current manifest before C is
allocated; C retains that hash-bound predecessor admission separately from A.
Implementation/review may retain a closed inert final assertion draft with
`proof prepare-final`; only the outer verify/reuse dispatch binds it to a
validated configured-final receipt under its existing lock. Each final test row
must retain that receipt's exact command, attempt, record and selected nodes;
focused/pre-review or unrelated final receipts refuse. Lost completed proof refuses;
late first supply reuses the valid receipt without rerunning it.

The four fixed historical records declared in `FROZEN_BOARD_RECORDS` in
`scripts/changerail/local_delivery.py` are not that active card: OSS-06-S1,
OSS-06-S5 and OSS-07 are `superseded-no-go`; OSS-06-I13 is
`suspended-not-verifiable`. Every decision checks all original paths, regular-file
identity (including ancestors) and SHA-256 bytes. Missing, moved, symlinked or
edited originals fail closed. There is no configurable exemption or refreshed
hash cache. Other in-progress cards, including similarly named copies, remain
active and block a new start.

Doctor reports both historical groups separately. The read-only
`./bin/chrl board-guard [--start] <card>` adapter shares this policy with the
shell start guard; `--start` also requires an empty actual lane. Neither form
grants admission or recovery authority. Dependencies still require their literal
done-card targets; historical sources are never substituted by successors.
Admission, FF/resume, start/recovery, review, handoff and publication reject these
four sources before lifecycle writes. `board-do` rejects them even in its
already-inprogress and dry-run branches. Read-only refusal explains disposition.

FF/publication maintain ordinary live-card links but never rewrite the verified
originals. Only their outbound links are historical; dangling ordinary live or
product links still fail. These files remain visible in payload fingerprints,
and integrity validation precedes reference exclusions. I13 remains unqualified:
I16's omission is not replacement or certification. See the exact identities and
offline bootstrap boundary in the
[CHRL-FIX-01 card](../../openspec/board/5.canceled/chrl-fix-01-account-for-frozen-legacy-board-records.md).

Exact literal board references in changed tests remain checked, just like product
and documentation references. Synthetic test-board paths are constructed from
the explicit `FIXTURE_BOARD` root in isolated fixtures, so they are not presented
as links to this checkout. Preserve their exact runtime string/byte values and
negative scenarios. Do not add a blanket `tests/` exclusion, an ignore marker or
a fake board card to make the reference gate pass. Actual repository links in
tests stay literal and must resolve.

Runtime records live under `.runtime/changerail/{ff-runs,runs}`. They include
phase timing, model routes, token usage, command counts, stop reasons, evidence
and verdict fingerprints. Missing usage is unknown, not zero. Raw streamed
command text/output is not retained as a secondary credential log. Focused
verification logs still need public-safe commands and inputs.

## Explicit offline-amendment finalization

This exceptional lane is not recovery and is never inferred from a dirty tree.
An operator prepares a closed `qa-mcp.offline-finalization.v2` request naming
the terminal source run/card, source run and manifest digests, hash-bound root
lineage, unchanged baseline, complete payload, typed old/new mode/kind/deletion
amendments and reasons, supporting plan hashes, inert per-condition observation
drafts, and a pinned branch/remote/full ref plus credential-safe remote digest.
The authority statement, objective and each amendment reason must contain
non-whitespace text. They document scope; the statement is not self-approval.

`./bin/chrl finalize-offline <inprogress-card> --request <request> --check` is
currently disabled in both modes pending independent review. It refuses before
request parsing, reservation, model/review, runtime writes or publication. Do
not use it for a pilot. Tests may enable the internal route only with an explicit
fixture-scoped patch in a disposable repository; production does not provide an
environment role, raw plan, fixture registry or bootstrap flag as finalizer
authority.

The fixture-only existing-publisher path pins one effective push destination
(`pushurl`, not the fetch URL), rejects multiple destinations and URL rewrite
configuration, and stores only a destination digest. Before board, index, commit
or network effects it fsyncs the original/expected scope, transforms, parent,
tree, commit intent and upstream. Retry accepts only an absent ref, the retained
parent or the intended commit, then uses an explicit non-force `commit:ref` push.
This remains default-disabled and is not independent acceptance.

The CHRL-FIX-02 implementation candidate covers exact request checking,
root-lineage serialization, caller-owned 03D evidence and existing-publisher
continuity. Independent review-08 rejected a preceding candidate because an
installed terminal manifest could lose its producer expectation before the later
run intent was saved, and the run writer could return with unsafe output ancestry
before its outer closure refused. The scoped repair retains the manifest producer
intent before output installation and holds each required writer's inputs/output
through its own last flush and return. Repair checks and independent assessments
are retained separately; earlier input/output/history repairs remain preserved.
This implementation description is not acceptance. Its flag
stays false even after offline tests; enabling either mode requires a separately
authorized reviewed change. The card's historical Stage/Next and prior Log are
preserved; its current Result and retained assessment identify readiness.

With fixture-scoped enablement, `--check` is read-only and never reserves an
attempt. Execution first requires a nonempty, explicitly reviewed
`offline_finalization.evidence_commands` list. These are trusted executable
configuration, not inert Verify targets or request-supplied commands. Empty
configuration refuses before reservation. Ordinary pre-review/final commands
and producer roles retain their existing ownership rules.

Execution acquires the root-lineage lock, rechecks the creation-bound request,
source history, complete payload and all adopted plans, and retains one attempt.
It runs real configured checks and turns only request-bound implementation
drafts into typed receipt/node/assertion-source proof. Review and final rows
remain with the actual reviewer and outer final verification. Every later
consumer revalidates the original sources and full namespaced coverage; raw
`bootstrap_plan`, copied owners, version removal, old GO and offline summaries
are not admission or evidence. Declaration migration remains separate.
The physical attempt directory must equal the root-derived reservation, with
the immutable creation selection intact. Consuming a retained `finalizer` role
requires the same admission as producing it; an ordinary proof index grants no
such capability. Finalizer-owned writes require the current root lock.

Restart validates actual artifacts rather than a stage label. Review intent
names the session actually allocated by the launcher, its exact context and
verdict destination. The reaped launch retains a termination receipt binding
its owner, session metadata and usage-event bytes; successful review additionally
retains its exact verdict receipt. Receipt-loss recovery reuses a completed GO
or exact final check set only when the lost receipt is the parent transition,
not one of the completed review's required dependencies. Later reviewed/final/
publication consumers also validate the retained allocated owner, context,
metadata, events, termination and result. Completed session inputs cannot be
changed, removed or extended to alter accounting. Offline session and receipt
writes use no-follow descriptors and exclusive temporary files; dependencies,
files and directories are flushed before parent advancement. Conflicting
evidence is preserved, not overwritten. The dependency closure keeps each
flushed file descriptor, inode/content identity and no-follow ancestry alive
through receipt installation. Parent writes reacquire and flush the validated
closure and retain it through their own installation, on normal and recovered
paths. Equal bytes on another inode cannot inherit an earlier file's fsync.
The installed parent/session/artifact output joins that held closure and remains
object/content-bound through its final enclosing directory flush. A safely
reacquired equal-byte output must itself be file-fsynced before certification;
later replacement refuses. Dependency-free parent writes have no enclosing
closure flush and use the common writer's checked final installation flush.
The parent takes its verdict reference from the checked completed-result receipt;
retry takes metadata/events/context from its pinned termination receipt. It does
not renew those certified digests from later file contents. Result creation
compares and hashes one snapshot of already validated metadata and verdict JSON.
The result writer returns that same certified verdict reference to offline
history creation. The history writer verifies its supplied bytes against the
reference and retains the safely read source with the installed history through
its last flush. A later temporarily substituted verdict cannot become an
unissued history even if the original source is restored before installation.
Offline review setup also uses owned no-follow storage for its lock, cycle
manifest, payload diffs, context and history; it rejects conflicting temporary
entries before model launch. Ordinary delivery writers are unchanged.
Review-lock release does not add directory writes after the individual artifact
writers' completed, output-validated flushes.
The offline context contains a closed input group for its generated cycle
manifest and every indexed diff. Their expected hashes come from the producing
bytes; all those objects remain held with the context through its final flush.
Termination/result/parent and recovery consumers explicitly revalidate and
flush that same certified group, including each indexed diff. Later file reads
do not supply new expected digests.
Terminal publication takes the initial manifest hash from `creation.json`, not
from an unpinned installed output. Before adding publish data to `manifest.json`,
it persists a distinct closed `terminal_manifest_intent`: creation-pinned before,
exact produced after, fixed publish metadata/timestamp and the known produced
pushed-journal reference. This intent is not a completed manifest receipt.
Recovery validates current manifest bytes against those known before/after
identities and the deterministic transition. Losing the intent after installation
cannot make changed bytes or a different valid timestamp become their own proof;
only independently retained legacy manifest/run pins keep their existing route.
The manifest-intent parent holds its exact before input, checked origin and
journal through its own last flush. Manifest installation then holds the known
certified parent-record reference, that origin and journal, plus its produced
output through the writer's own return. A recovered producer record is checked
and file-flushed again; readable bytes do not inherit an old inode's fsync.
An interrupted, uninstalled producer draft does not pin an unproduced timestamp.
Before
installing `run.json`, it persists a distinct closed `terminal_run_intent` with
the manifest reference and exact before/after producer identities. This is an
incomplete write intent, not a completed run receipt. Installation checks the
expected before-state and re-flushes any accepted same-byte replacement before
the intentional installation. The intent-producing parent retains that exact
before input through its own last flush; this phase-local lease ends before the
legitimate before-to-after replacement. The before hash comes from the retained
creation producer, never from the current run bytes. The checked `creation.json`
snapshot itself joins the parent and outer immutable dependency groups.
Origin comparison and dependency retention consume that same snapshot; a second
read cannot renew its expected hash between validation and parent installation.
The later completed manifest pin and run intent are installed together in one
parent record: a valid pre-run-intent interruption has neither member of this
later group, but the already installed manifest retains its separate producer
intent. A retained manifest-only group with
lost intent is refused even when the run is still attempt-active. Pre-intent
restart checks the creation-pinned before-state before further writes; changed
bytes cannot mint a replacement expectation. Restart accepts only the retained before/after identity
and checks the deterministic transition while before-state bytes exist. An
installed output with no intent or independently completed legacy pair refuses;
it cannot supply its own new expected digest. Completed terminal accounting
requires both manifest/run references.
The run writer itself holds the known certified producer parent, manifest and
origin with its output through its own last flush/return; a later outer refusal
cannot substitute for that boundary. Both required expected-before writers
revalidate inputs after the before-file flush and retire only that obsolete
before lease at replacement. Their output object/content and no-follow ancestry
remain held until return. Ordinary generic publication writers are unchanged.
The outer terminal closure shares the nested parent's complete certified review
dependency definition: context, cycle manifest, every indexed diff, verdict,
metadata/events/termination/result, plus terminal manifest/run/parent outputs.
All remain object/content-bound through the outer last flush, including direct
public recovery without a redundant later parent write. After producer-temp,
producer-installed, manifest-installed, pre-run-intent, installed-run or run-intent
persistence failures, restart matches the retained identities and
re-flushes exact accepted inputs/outputs; changed or unsafe evidence is preserved
and refused without repeated review/check/commit/push effects.
Recovery re-flushes its validated
completion dependencies before advancement: a readable receipt after an
interrupted directory fsync is not assumed durable. Only a demonstrably ended
incomplete reviewer with current proof can retry in that same attempt, retaining
all earlier usage. Unknown/live ownership, substituted or corrupt artifacts,
NO-GO, red floor and source drift refuse before further effects. Source history
is never refreshed, and no implementation/repair model or synthetic handoff is
introduced. Numerical budgets remain informational; usage is not reset.
Before resumed transformation, staging or commit, the publication path checks
branch/full ref, upstream, permitted index/worktree and HEAD. Only the baseline
or a fully matching commit-before-receipt state is admissible. Commit creation
explicitly sets both pinned identities; recognition and push compare their
actual digests, message and times in addition to tree and parent.

The tests distinguish real subprocess/Git restart scenarios from synthetic
storage-unit inputs. Process exits and injected persistence failures establish
those tested boundaries, not observed power-loss durability. Final acceptance
and the full non-live coverage floor remain separate from these mechanisms.

## QA verification and legacy transition

The fast lane runs whitespace, compilation and strict canonical-spec validation.
The final lane adds the CI non-live pytest/coverage floor. No mandatory PostgreSQL,
Metadata inventory, Ruff or mypy gate is inherited. Go/Windows and live TestClient
evidence remain required where the card's affected behavior needs them.

See [legacy-board-transition.md](legacy-board-transition.md) before resuming an
old card. The preserved lifecycle snapshot includes uncompleted plans; preserving
an artifact is not admission, acceptance or completion evidence.

## Astra instruction adaptation

The supplied OpenAI guide is the source for this migration:
[Using GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md).
The user supplied its text after official fetches returned 403.

AGENTS.md owns autonomy, permission boundaries, communication, task-sized checks
and delegation. Skills own stage-specific evidence and handoff contracts. Legacy
root lifecycle conflicts are explicitly overridden for this component. Runtime
lab details are linked only when needed. Shared instructions remain suitable for
Terra implementation. Deterministic boundaries are retained during prompt trimming.

The model migration keeps high reasoning; none/minimal is rejected for Astra.
The integration must use Responses for tool calls and omit unsupported sampling
and logprobs parameters. CLI/proxy compatibility is verified separately from
mock tests. Async tools, dynamic reasoning and cache-policy changes are optional
future work; this migration does not add a new API client.

## Separate pilot

Prepare a named small card, exact command, models/budgets, required target,
side effects (including commit/push), evidence location and stopping conditions.
Ask the user to approve that pilot before execution. Authorization to migrate,
test the harness or publish migration files does not authorize a pilot run.
Until approved, report installation/check results with `pilot: not run`.
