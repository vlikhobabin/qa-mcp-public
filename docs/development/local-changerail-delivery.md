# Project-local ChangeRail

The installed runtime is the common ChangeRail distribution, pinned by
`.changerail/distribution-lock.json`. Shared files are owned by that manifest;
change them in the distribution source, then install a new verified archive.
The project profile, runtime rules and adapter configuration remain QA-owned.

## New delivery

Every new card uses `openspec-v1` and exactly one pinned local OpenSpec change.
Prepare its proposal, delta specs, design and ordered task groups with the local
`bin/openspec`, then use `chrl native-accept`, `chrl doctor` and `chrl-run` within
the authorized delivery scope. New cards follow `openspec/board/card-template.md`.
The explicit `changerail.card-evidence.v1` Verify plan maps every Acceptance ID
once to meaningful before/action/after evidence and a required stage.

The runner owns independent review, exact archive, final verification and
publication. At most two independent review cycles cover the entire run and its
ordinary continuations. Repair after NO-GO or failed final verification uses the
same remaining allowance. Archive continuation stays in its original review
cycle and thread. Timing, command and size estimates are observations; they do
not add reviews, weaken evidence or authorize publication.

## QA-owned policy

`.changerail/profile.toml` runs affected qa-mcp tests in separate offline and
integration lanes, changed-file compilation and strict OpenSpec validation.
A full suite with coverage >=60% requires epic closure or explicit operator
agreement; ordinary card finalization does not select it. See
[test-policy.md](test-policy.md). Product commands,
Codex launcher and runtime authorization are not imported from another project.
The default evidence policy is `reuse = "rerun"`: archive-invalidated focused
checks are executed again. Explicit local dependency reuse can be enabled for
an allowlisted deterministic command with complete input declarations; external
runtime state is never justified by file hashes.

Typed runtime observations preserve target/session identity, explicit runtime
intent, preflight and recovery references. Linux/Windows native behavior needs
its appropriate runtime proof. Passing generic ChangeRail tests is not a live
TestClient qualification.

## History and continuation

`chrl status` and `chrl metrics` read history without rewriting retained files.
Old board-only, FF and offline-finalization engines are removed. Installation
retains exact old run identities as read-only in its lock. It does not migrate
old GO, repair allowance, process identity, acceptance or publication authority.

Ordinary resume is available only to a new run whose installed core, profile,
accepted plan and retained evidence still match. Failed checks require changed,
evidenced repair. An interrupted final floor is not restarted automatically.
A committed checkpoint permits only the receipt-proven publication remainder.

`.changerail/history.json` retains exact historical board/artifact identities.
Existing unresolved product work stays in its retained state; a distribution
update is not product completion, cancellation, review GO or publication.

## Tool maintenance

QA consumes the executable distribution only. ChangeRail and OpenSpec wrapper
tests, fixtures and test launchers stay in the ChangeRail source repository;
they are absent from this checkout's installed payload and CI. Installation
checks compare the distribution hashes and run `./bin/chrl wiring`. The same
tested runtime does not require another complete tool test run in each project.
Product pytest collects `tests/`. Historical evidence locators remain historical;
old test paths are not converted into claims about newly run tests.
Git hooks perform fast wiring/diff checks; they do not silently run the tool suite.

See `DISTRIBUTION.md` for build, verification, adoption, drift checks, backups
and updates; `tools/changerail/README.md` defines the common execution contract.
This adoption is user-authorized unmeasured process maintenance without a new
board card. No measured model delivery is claimed by the installation itself.

The predecessor `.changerail/native-source.json` and `.changerail/legacy-lifecycle.json`
remain historical provenance; the installed distribution lock and current history
manifest own the new boundary. Stopped FIX-02 remains suspended product work,
with its original card and receipts preserved; installation does not mark it done.
