# qa-mcp board

The project owns a local copy of the common ChangeRail runtime on pinned local OpenSpec 1.3.1.
The board controls high-level state:
1.backlog -> 2.todo -> 3.inprogress -> 4.done; 5.canceled closes work without
implementation. OpenSpec owns proposal, delta specs, design and tasks for each
new card. Completed/canceled history is not rewritten.

Use card-template.md for new work. Prepare its one linked change with the local
`./bin/openspec`, then use `./bin/chrl native-accept <backlog-card>`. The standard
artifacts are not duplicated in the card. Board-only and FF execution are removed; their records remain readable history.
./bin/chrl-run <todo-card> performs authorized full delivery including commit
and push. Accepted cards skip FF. Only the runner finalizes done after fresh GO
and final verification. Ordinary review does not authorize publication.

One card has one invariant, exactly one linked OpenSpec change, dependencies,
canonical specs, checks and Delivery Budget. Contiguous `## N. group-slug`
headings in `tasks.md` are the ordered ChangeRail checkpoints. Use Order Index where present;
filename prefixes alone do not define order. By operator policy,
`budgets.enforce_limits=false` makes numerical time/size/command estimates
informational. The shared maximum of two independent reviews remains mandatory;
semantic and failed-floor repairs use the same remaining allowance. Keep realistic Delivery Budget
estimates and measured usage; do not invent a fitting estimate or split solely
to satisfy an old ceiling. Scope, evidence, dependency and authority gates still
apply. Function-level steps can remain checkpoints inside one coherent card.

New cards use a unique `[C<number>]` prefix on every top-level Acceptance
bullet. Follow [card-template.md](card-template.md) and the closed
[`card-evidence.schema.json`](../../tools/changerail/schemas/card-evidence.schema.json):
one `## Design`, and one fenced JSON `changerail.card-evidence.v1` block in Verify
(optional explanatory prose/planned shell checks are allowed). Every condition
row has `condition`, `seam`, `precondition`, `action`, `expected`, `method`
(`test`, `inspection`, or `runtime`) and `stage` (`implementation`, `review`,
or `final`); method is an object with both `kind` and `target`. Assess `mutation`, `concurrency`, `restart`, `publication`,
`input_safety`, and `external_effects` exactly once in risk groups. Locators are
inert repository-relative files, never commands or evidence execution. Specs
checks IDs; design permits an empty/subset condition list; tasks/admission needs
the exact mapping. Each risk group has `kinds`, strict `applies`, `decision` and
`conditions`; concrete N/A decisions have empty condition references.
Invalid/incomplete fresh declarations are DeliveryError exit-2 migration
refusals: explicitly update the plan in place, not SPLIT_REQUIRED/rescue cards.
Static validity is not semantic proof; exact retained recovery is unchanged.

New executable cards require exactly `## Lifecycle` / `openspec-v1`. Explicit
`board-only` is readable history only and cannot execute. Unmarked backlog, todo
and in-progress cards fail closed; unmarked done/canceled cards remain readable
history. Never change the lifecycle of an active frozen run.

Legacy cards are not automatically admitted. Read
[the transition inventory](../../docs/development/legacy-board-transition.md)
before resuming them. Existing pre-adoption `openspec/changes/` content is
immutable context unless explicitly reconciled.

The hash-pinned in-progress originals listed in `.changerail/history.json` remain
non-deliverable historical sources, not active work. Doctor reports their retained `superseded-no-go` or
`suspended-not-verifiable` dispositions separately.
Their original paths and bytes are checked before exclusions; any drift blocks
the workflow. All other in-progress cards count as active. Historical sources
are neither done dependencies nor writable live-link sources, and cannot be
resumed through the runner. I13 is not certified by I16's omission.

The runner owns evidence fingerprints, review/repair and recovery. See the
[ordinary native route](../../docs/development/native-openspec-delivery.md) and
keep [historical exceptions](../../docs/development/historical-changerail-recovery.md)
out of new-card instructions.

Historical inventory, the stopped OSS-FIX-01 pilot, offline correction queue and
their non-publication boundaries are intentionally documented only in the
historical guide and their own board cards.


## Product verification policy (2026-09-09)

ChangeRail development is canceled in qa-mcp; the installed runtime is only an
executable dependency. Ordinary card verification selects changed qa-mcp modules
and affected consumers, separately for offline and integration checks. Full tests
require epic closure or explicit operator agreement. This operator policy
supersedes older per-card full-suite commands; do not revive historical tool
test suites. See [test-policy.md](../../docs/development/test-policy.md).
