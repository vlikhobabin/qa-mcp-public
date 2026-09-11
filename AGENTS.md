# Repository Guidelines

## Ownership and entry points

This independent repository owns the native 1C TestClient QA manager/MCP,
BDD execution and evidence, and its Windows host bridge. Use its own Git status,
dependencies and tests. Preserve unrelated working changes.

- Runtime/provider: `src/qa_mcp/`; tests: `tests/`.
- Windows bridge: `host-agent/windows-display-agent/`; Linux orchestrates builds,
  while native Windows behavior needs Windows evidence.
- Protocol research: `docs/protocol-research/`, `tools/protocol-research/`.
- Consumer contracts: `README.md`, `docs/qa-mcp-tool-reference.md`,
  `docs/shared-core-extension.md`; dated counts are not current delivery proof.
- Board plans: `openspec/board/`; canonical contracts: `openspec/specs/`.
- Local captures/logs: ignored `runtime/`; delivery evidence: ignored
  `.runtime/changerail/`. Only curated public-safe reports belong in
  `docs/protocol-research/evidence/`.

Use Linux shell/Python entry points. Do not introduce PowerShell, cmd, bat or
WSL workflows. Keep credentials, auth/session state, full infobases, EPF payloads,
large captures, platform logs and customer data out of Git.

## Project-local ChangeRail

The common native runtime is installed locally under `scripts/changerail/` and
`tools/changerail/`, pinned by `.changerail/distribution-lock.json`. Shared source
changes belong in the distribution repository and arrive through verified
archives. `.changerail/profile.toml`, project adapters and runtime policy remain
project-owned. External source checkouts are not delivery authority.

New executable cards require `## Lifecycle` / `openspec-v1`, one local OpenSpec
change and ordered `tasks.md` groups. Prepare stock artifacts with `bin/openspec`,
then use `chrl native-accept`, `chrl doctor` and authorized `chrl-run`. The runner
owns implementation, independent review, archive, final verification, done and
publication. Full delivery requires user authority including commit and push.
There are at most two independent review cycles across a run and its ordinary
continuations. Semantic repair and failed-floor repair consume the same remaining
allowance. Timing, size and command estimates are advisory; they never add reviews.

Board-only, FF and offline-finalization execution are removed. `chrl status` and
`chrl metrics` read retained history without rewriting it. Install-time history
snapshots cannot resume under the new runtime. Ordinary new native resume requires
the exact frozen core, profile, accepted plan and evidence. No lifecycle change,
old GO or prior publication authority is inferred from installation.

Use clean primary `main`, one active writer and satisfied dependencies. Preserve
unrelated changes. Project history exclusions in `.changerail/history.json` are
hash-pinned sources, not done dependencies. New Verify plans use the closed
`changerail.card-evidence.v1` schema: every Acceptance ID has meaningful typed
proof, risk decisions and inert project-relative locators. Runtime proofs retain
QA target/session, intent, preflight and recovery requirements.

Pinned OpenSpec lives under `tools/openspec/` with no runtime download/global
fallback. Validate canonical specs with `bin/openspec validate --specs --strict
--no-interactive`. This project consumes the executable ChangeRail distribution;
ChangeRail tests, fixtures and test launchers stay in its source repository.
Do not install or run its development suite here or add it to QA CI. Verify
installation hashes and `bin/chrl wiring`; product pytest collects `tests/` only. Git hooks perform
fast wiring/diff checks, not implicit tool suites. See
`docs/development/local-changerail-delivery.md`,
`docs/development/native-openspec-delivery.md` and `DISTRIBUTION.md`.
Historical recovery guides describe previous contracts only; they are not
execution instructions for this installed runtime. Domain skills stay owned by
agent-core; QA-specific authoring skills stay local.

## Autonomy, roles and communication

Operator policy updated by explicit user authorization in this maintenance
session: time, size and command measurements are advisory. The shared maximum
of two independent reviews is mandatory even with `budgets.enforce_limits=false`.
Repair never creates a separate review allowance. Retain all attempt accounting;
never reset it on resume. Scope, acceptance, evidence integrity, one active writer,
runtime authority and publication gates remain mandatory. An estimate or numeric
waiver cannot authorize a pilot, commit or push.

Infer routine details from the card and evidence; complete authorized work.
Planning, inspection and review requests do not authorize implementation or
publication. An implementation request permits in-scope edits and relevant checks
without repeated permission questions. Ask when missing information materially
changes scope, result or authority; first prepare the independent authorized work
and a concrete decision.

User instructions take precedence over skill guidelines within applicable system
and safety constraints. If a skill causes a permission request, pause or divergence,
link its exact SKILL.md, quote the rule and explain how it applies. Distinguish
an interpretation from a deterministic gate error.

In measured runner sessions, implementation completes with successful
handoff; review with a complete validated verdict and unchanged payload. The
outer runner alone advances between roles and publishes. Persist within that
boundary and use retained recovery context instead of restarting discovery.
An ordinary authorized offline fix completes with its relevant checks and report;
it does not require creating a runner context or invoking handoff.

The runner owns independent review. Additional subagents require an independent
bounded task and harness support for shared budget accounting; never create
competing writers or uncounted review cycles. Parallelize useful independent reads;
keep dependent operations sequential.

For operator-authorized roadmap orchestration, follow
`docs/development/oss-00-orchestration.md`. A supervising Codex session selects
and refreshes cards, commits plan/admission updates before clean-start delivery,
then invokes the existing runner and verifies its result. Outside an active run,
it may delegate a bounded minor product fix without a card, review its evidence
and commit/push within the operator's authority. Such fixes cannot bypass a
runner review or revive stopped work. Keep one active writer; update the roadmap
and next card only after that writer finishes. ChangeRail maintenance is excluded.

Lead updates with findings and the next step. Use concise connected prose and
lists for useful comparisons or sequences. Report results, checks and material
limitations; preserve every required card and verdict field.

## Verification

Install with `uv sync --extra dev --locked`. Use focused tests for changed
behavior; add cases for acceptance, reproduced regressions or stable public
invariants. Broaden/repeat checks only for changes, failures or concrete uncertainty.

Operator policy (2026-09-09): this repository only consumes executable ChangeRail.
Do not develop, repair or test ChangeRail here. Remaining ChangeRail work is
canceled; its development tests and fixtures must not be installed or run.

Ordinary checks select only changed qa-mcp modules and their affected consumers:
`uv run pytest --qa-changed --qa-lane offline --durations=10`. Run the separately
reported `integration` lane for affected subprocess/build/display consumers.
Use `--qa-plan` to inspect selection. Explicit test file/node arguments are
focused requests. `pytest` without selectors also selects changed modules; it
must never silently become a full suite. Missing dependency mappings require
an explicit map/focused check, not a fallback to every test. Git diffs include
staged, unstaged, new, deleted and both renamed paths; CI supplies its base SHA.

A full suite is permitted only before closing an epic or with explicit operator
agreement: `--qa-full=epic --qa-reason <epic-card>` or
`--qa-full=approved --qa-reason <agreement>`. Full offline coverage >=60% belongs
to that explicit run; partial module checks have no whole-project coverage floor.
Neither per-card final verification, push/PR CI nor a release tag independently
authorizes a full suite. Keep independent review and actual selected-test proof.
Record focused evidence after final card Result/Log edits; reuse unchanged
checks only under the installed runner's supported evidence contract.

Live Linux/Windows 1C checks are separate from offline and subprocess integration.
They require concrete runtime authorization and preflight. Use explicit
`live-linux` / `live-windows` lanes, retaining start/end timestamps, target identity,
result, duration and cleanup evidence. Host Go tests/builds remain product checks;
Windows-native behavior requires Windows evidence. No live test is inferred from
its filename or from successful cross-compilation. See
`docs/development/test-policy.md` and `docs/development/test-inventory.md`.

## Runtime safety and routing

Support providers serve fixture authoring, metadata and read-only diagnostics;
native protocol operation must not depend on them. Consult
`docs/development/runtime-lab-context.md` when lab/provider context is needed,
and verify current paths and target identity. COM is not the Linux QA contour.

- Live capture/replay/probes require explicit runtime intent and successful Linux
  preflight; record failure as `runtime_gap` before execution.
- For Linux `vanessa_client` file-infobase contention, use
  `launch_test_client(manage_apache=true)` / `stop_test_client` to release and
  restore Apache around boot, after checking current ownership.
- Follow `docs/protocol-research/corpus-evidence-contract.md`: read-only and safe
  actions require their proof class; mutations/dialogs require recovery/rerun
  evidence. New protocol claims retain frame numbers, dynamic fields, normalized
  hashes, command labels and replay results.
- Clean only processes/PIDs/resources created or explicitly owned by the run.
  Preserve unrelated 1C sessions, Docker resources and user data.
- V2 safe-action research accepts only reviewed rows with
  `mutates_business_data=false`, allowlisted action family, target marker,
  pre-state, post-state, recovery expectation and expected result markers.
  Value changes, business commands, save/post/delete/fill/import/export and
  external effects require the applicable mutation/recovery card and authority;
  V2 rejects operations absent from its safe-action manifest.
