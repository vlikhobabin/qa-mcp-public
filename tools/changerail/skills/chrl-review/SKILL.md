---
name: chrl-review
description: Independently review one in-progress card in a fresh Codex CLI session and write a fingerprint-bound GO or NO-GO verdict without modifying its tracked payload.
---

# Local ChangeRail Review

For an `openspec-v1` card, independently review the linked proposal, delta
specs, design and tasks named by the retained manifest/context in addition to
the board acceptance and evidence. Task checkboxes and completion events do
not substitute for code/evidence, and structural OpenSpec validation is not GO.

Review the `[C<number>]` Verify plan as a coverage map: assess meaningful
before/action/after observations and N/A credibility. Structural validity does
not replace semantic review or create another review cycle.
Require the payload to identify mocked pieces versus real policy/state checks:
a call-order-only stub does not establish a before/action/after invariant.
For a v2 observed-proof verdict every generated stage decision is mandatory:
inspect typed observations and assess relevance, before/action/after assertions,
risk reasoning and mocked seams yourself. Keep final-only rows `pending_final`;
a receipt exit code is not semantic acceptance.
Use only the context's checked condition inventory. Historical records are
read-only context and cannot grant execution or new proof authority.

You are the independent reviewer. You did not plan or implement this payload.
Repository startup already supplies the applicable `AGENTS.md`. Read
`$CHRL_REVIEW_CONTEXT` first. It names the card, fingerprint-bound manifest,
verdict schema, per-path scoped diffs, compact evidence index, prior-cycle
artifacts when they exist, and the investigative shell-command budget. Consult
the consumer-owned board instructions named by the project or review
context only for a board rule not covered here. A board README is optional;
do not assume `openspec/board/README.md` exists. Do not scan
the repository or list runtime directories to rediscover any of these paths.

## Review

1. Run `./bin/chrl verdict fingerprint <card>`, then read the context, card,
   manifest, and schema without concatenating the payload diffs into that same
   output. `payload_diffs` contains one prebuilt artifact and byte size per
   selected path. Read those artifacts separately; for a large entry, use
   bounded line ranges instead of printing it whole. Do not reconstruct a diff
   command or dump complete changed files already represented there.
2. When `previous_cycle` is null, no prior verdict lookup is needed. Otherwise
   read only the exact prior verdict and manifest paths named there, including
   when `cross_run=true`; `selected_paths` already contains only added, removed,
   or hash-changed paths. Concentrate on the prior findings and failing
   acceptance surface and carry forward acceptance evidence for unchanged path
   hashes.
3. Map every verdict acceptance entry to observable code and focused evidence
   under the current run directory. For structured OpenSpec acceptance, each
   entry identifies one complete Requirement/Scenario pair: evaluate all of its
   `WHEN`/`THEN`/`AND` clauses together. Evaluate every scenario even after
   finding a blocker; do not stop the review early. Review test adequacy: a test
   is useful only if breaking the required behavior would make it fail.
4. You may rerun one cheap finding-specific check. Do not run the full pytest
   suite or repository verification floor; the fast static pre-review lane is
   already green and `./bin/chrl verify` owns the post-`GO` full floor.
   Start from the context's diff and evidence index. Read an individual evidence
   log only for a specific missing or failed assertion. Read adjacent callers or
   dependencies only for a specific acceptance or correctness question; use
   symbol searches and bounded excerpts instead of broad repository scans.
   Command and timing targets are observations. Complete the review within
   its accepted scope; record unresolved required evidence as concrete findings.
   Do not reset accounting or create another independent review implicitly.
5. Use `blocker` only for a real acceptance failure, correctness defect,
   mandatory missing evidence, unsafe behavior, or scope violation. Important
   non-blocking cleanup is `major` or `minor` and does not force `NO-GO`. Return
   the complete set of blocker, major, and minor findings together in the one
   verdict; finding a blocker does not end finding collection. Every finding
   must populate the schema's `preconditions`, `expected`, `observed`, and
   `repair_scope`. Make the precondition concrete enough to reproduce the gap,
   distinguish the actual observed state from the required state, and enumerate
   every assertion or code boundary needed for repair. Do not use a broad label
   such as “replacement evidence is incomplete” when the missing before-state,
   mutation, and after-state checks can be named precisely.
6. Create the verdict at the path printed by
   `./bin/chrl verdict template <card>`. Preserve its fingerprint exactly,
   include one acceptance entry per generated scenario or compact criterion,
   and then run
   `./bin/chrl verdict validate <card>`.

A focused re-review starts fresh, reads the prior verdict, concentrates on its
blockers and affected surface, and still confirms that all acceptance entries
remain supported. Apply AGENTS.md autonomy and communication rules within this
review role; successful review ends with the validated verdict.

Do not modify tracked files, stage, commit, push, move the card, or edit the
manifest. The review launcher rejects any tracked-payload fingerprint change.
