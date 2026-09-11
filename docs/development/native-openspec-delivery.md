# Standard native OpenSpec delivery

This is the ordinary route for new qa-mcp cards. ChangeRail owns board status,
QA evidence, implementation checkpoints, independent review, final verification
and publication. Pinned unmodified OpenSpec 1.3.1 owns proposal, delta specs,
design and tasks.

Project verification policy (2026-09-09): ordinary card final verification runs
only affected qa-mcp tests in separate offline/integration lanes. A full suite
is reserved for epic closure or explicit operator agreement. The installed
ChangeRail runtime is not developed or tested here. See [test-policy.md](test-policy.md).

## Entity ownership

| Entity | Owner and location |
| --- | --- |
| Epic/roadmap | board card under `openspec/board/` |
| Card | scope, acceptance, dependencies, budget, QA evidence policy and state |
| Change | `openspec/changes/<id>/` |
| Proposal/spec/design/tasks | stock OpenSpec artifacts in that change |
| Checkpoint | contiguous `## N. group-slug` in `tasks.md` |
| Canonical capability | `openspec/specs/` |
| Run receipts | ignored `.runtime/changerail/` |

One card currently links exactly one change. Native measured FF, multiple native
changes per card and an automatic epic scheduler are not implemented in the
runner. A supervising Codex session can drive sequential card delivery using
the existing commands; see [OSS-00 orchestration](oss-00-orchestration.md).

## Lifecycle and compatibility

Every executable card contains exactly:

```md
## Lifecycle
openspec-v1
```

The explicit value `board-only` is readable history only; its executor is removed.
Unmarked backlog/todo/in-progress cards are refused. Unmarked done/canceled
cards remain readable history. A frozen run cannot change lifecycle through
ordinary recovery.

## Local OpenSpec

`tools/openspec/package-lock.json` pins 1.3.1. Normal commands invoke only the
installed project dependency and disable telemetry/update/completion behavior:

```sh
./tools/openspec/bootstrap.sh --offline
./bin/openspec --version
```

Bootstrap is an explicit provisioning action and fails if the npm cache lacks a
locked tarball. Runtime commands never call npx, install, download, search PATH
for OpenSpec or use a global schema directory. This boundary does not make model
provider sessions or an authorized Git push offline.

## Prepare and accept

Create the change and follow its stock artifact instructions:

```sh
./bin/openspec new change <change-id>
./bin/openspec status --change <change-id> --json
./bin/openspec instructions proposal --change <change-id> --json
```

The card links it as:

```md
## OpenSpec Changes
1. `<change-id>`
```

Keep the card's `## Design` limited to QA evidence seams and safety/risk
decisions required by `changerail.card-evidence.v1`; implementation design belongs
only in the change's `design.md`. Group tasks with lowercase slugs:

```md
## 1. implement-route

- [ ] 1.1 Implement and assert the behavior.
```

After scope/artifact acceptance:

```sh
./bin/chrl native-accept openspec/board/1.backlog/<card>.md --dry-run
./bin/chrl native-accept openspec/board/1.backlog/<card>.md
```

Admission validates the pinned CLI, complete stock artifacts, strict change
syntax, task groups, QA evidence declaration and card budget. It freezes the
accepted plan under `.runtime/changerail/native-plans/` and moves backlog to
todo. It is structural admission, not independent review.

Admission can also rewrite board references; it does not commit these changes.
Review and commit/push the exact plan, admission and reference updates before
`doctor`/`chrl-run`, which require a clean tree. Keep this planning commit separate
from the runner-owned implementation/publication commit.

## Deliver

From an authorized clean `main` checkout:

```sh
./bin/chrl doctor openspec/board/2.todo/<card>.md
./bin/chrl-run openspec/board/2.todo/<card>.md
```

The run freezes `lifecycle_mode`, imports the accepted plan and moves the card
to in-progress. Each unfinished task group gets a fresh implementation session;
the runner checks actual task completion and current focused evidence at its
checkpoint. A separate finalization session follows the pinned stock semantic
sync instructions, merges delta specs into canonical specs, and records the
mapping with `chrl native-sync <card> --report <current-run>/sync-report.md`.
The receipt binds source/spec/report bytes; independent review judges semantics.

The reviewer follows the stock verify methodology. A preliminary GO is followed
by the runner's exact stock archive move using `--skip-specs`: sync was already
reviewed, so archive must preserve canonical and product bytes. A retained
intent supports reconciliation after interruption. A narrow QA-evidence refresh
then precedes continuation of the same reviewer thread and cycle for the final
fingerprint. The final floor and publication require that completed post-archive
GO. Later substantive repair uses a fresh independent review cycle.

The same versioned runtime is installable across projects; its exact source is
pinned in `.changerail/distribution-lock.json`. QA retains its profile, evidence
requirements and runtime authority. Fingerprint-invalidated focused checks rerun
by default. Explicit dependency reuse is available only for declared deterministic
local inputs; it cannot replace final-floor or runtime evidence.

At most two independent reviews cover the run and all ordinary continuations.
Repair after NO-GO or a failed final floor uses the same remaining allowance.
Timing and size are observations; scope, evidence and authority remain mandatory.

## Current rollout boundary

Native admission, lifecycle freezing, group sessions, local artifact context,
semantic sync and final-payload review gates are implemented. Observe a retained
run with `./bin/chrl status <run-dir>`. `./bin/chrl resume <native-run-dir>` delegates
to the shared exact-predecessor recovery and requires that exact predecessor.
The equivalent explicit recovery command remains:

```sh
CHRL_RECOVERY_OBJECTIVE='<remaining accepted work>' \
  ./bin/chrl run openspec/board/3.inprogress/<card>.md --recovery
```

For an already archived predecessor, recovery copies and revalidates its exact
archive receipt; it never recreates the active change or repeats sync/archive.
This is the QA runner's command spelling for receipt-proven continuation; it
preserves predecessor history and counters.

Previous exception contracts are read-only historical context documented in
[historical-changerail-recovery.md](historical-changerail-recovery.md).

## Tool verification and current transition

ChangeRail development tests run in its source repository. QA installs only
the executable distribution and verifies its hashes and `./bin/chrl wiring`.
No ChangeRail tests or test launcher are installed here or run by QA CI. Earlier
`tests/test_local_changerail*.py` evidence locators remain historical references;
the preserved receipts are not rewritten to suggest a new execution.
Integration tests use disposable Git repositories, pinned local OpenSpec and
controlled model substitutes. Passing them does not establish live model or
TestClient delivery. The install lock marks predecessor runs read-only; an update
neither completes nor cancels their product work. See the current local delivery
guide and distribution installation audit before selecting a new card.
