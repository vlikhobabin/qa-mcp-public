## Context

Clean published HEAD contains `observeHiddenDirectInWorker` with two direct
`inventoryHiddenWindowIsolation` calls, but lacks the four I5-authorized seam
families: `hiddenDirectFencedSample`, `observeHiddenDirectFencedSample`,
`observeHiddenDirectWindowsFencedSample` and
`hiddenDirectPreReceiptDiagnostic`. I5 Outcome A authorizes one private,
clean-base composition in seven existing paths, capped at three non-test and
four test files and 250 added non-test Go lines.

This is offline source work. There is no protocol capture, frame range,
dynamic runtime field or replay strategy. No process, endpoint, Windows
session or 1C runtime is started, so runtime cleanup is not applicable.

## Goals / Non-Goals

**Goals:**

- Fence each of the two real inventory boundaries with exact child, listener,
  job and response-TPort liveness snapshots before and after one inventory
  call.
- Keep one connected private pre-receipt diagnostic available across the
  worker/controller ownership acknowledgement while the existing local job
  handle is still held.
- Fail closed for unknown or changed liveness, inventory failure, empty
  inventory, missing/changed main identity and malformed diagnostics.
- Prove exact call counts, both worker boundaries, ownership lifetime,
  unchanged passive-UIA/admission behavior and privacy-safe diagnostics with
  injected offline tests.

**Non-Goals:**

- No public caller, adapter, route, wire field, marker derivation, classifier
  cause mapping, S5/S7 work, action, retry, fallback or live confirmation.
- No desktop/thread/window-station mutation, process/job ownership expansion,
  new package/module/dependency, fixture or unrelated predecessor byte.

## Decisions

### Model the fence as closed private status values

Use private liveness, inventory and fenced-status values plus bounded
snapshots. `observeHiddenDirectFencedSample` performs exactly: pre snapshot,
one injected inventory call, post snapshot, closed-vocabulary validation. It
does not retry and returns no raw error. A post snapshot unequal to the pre
snapshot is a refusal even when inventory succeeded.

Alternative considered: return raw errors or reuse the outer worker status.
Rejected because raw errors can leak dynamic identities and the umbrella
worker status cannot prove which private fence predicate refused.

### Keep Windows mechanics behind one injected wrapper

`observeHiddenDirectWindowsFencedSample` creates the exact process/job/TPort
snapshot closure from the response-bound child/listener and duplicated job,
then invokes the platform-neutral sample once. Windows primitives are exposed
through private variables only where hostile tests require injection. Handles
opened solely by the fence are closed on every path and close failure refuses.

Alternative considered: move production behavior into a new package or public
helper. Rejected by the I5 package/public/dependency ceiling.

### Connect exactly the existing two worker boundaries

Replace only the first and second inventory calls inside
`observeHiddenDirectInWorker`. Preserve its polling, sleeps, passive UIA,
admission and terminal outcomes. Each boundary reports a bounded private
diagnostic before a receipt exists; neither wrapper adds retry, fallback or
action behavior.

Alternative considered: unit-test the pure sample without editing the worker.
Rejected because I5 requires the actual two call sites and forbids a dormant
seam.

### Hold transferred-observer ownership after acknowledgement

Validate the observer against the exact response fields and request identity.
Invoke one private callback after response acknowledgement while the worker's
local job handle remains held; pass only the exact job and TPort ownership
needed for observation. The callback does not transfer, close or expand
ownership. Its injected test blocks long enough to prove the local handle and
listener remain valid, then releases normal cleanup.

Alternative considered: invoke before acknowledgement or after closing the
local job handle. Rejected because neither establishes the authorized
pre-receipt diagnostic ownership closure.

### Retain evidence bound to clean RED and exact staged GREEN

Record a curated privacy-safe evidence document with the baseline hash,
absence/presence counts, focused/full tests and vet, Linux tests, Windows
amd64/386 test cross-build hashes, path/LOC ceilings, hunk mapping and staged-
tree checks. No raw runtime identity or endpoint is retained.

## Risks / Trade-offs

- **[Risk] A helper silently adds another inventory attempt.** → Inject and
  assert exactly one inventory call per boundary and zero retry/fallback.
- **[Risk] Windows liveness tests become native-only.** → Put mechanics in the
  existing Windows test tree and require deterministic amd64/386 test
  cross-builds without executing Windows.
- **[Risk] Diagnostic state leaks raw errors or identities.** → Store only
  closed schema/stage/status/failure tokens and hostile-marshal diagnostics.
- **[Risk] Composition absorbs unrelated predecessor bytes.** → Use explicit
  path staging and map every Go hunk to an authorized predicate before review.
- **[Trade-off] The private seam does not classify detailed inventory causes.**
  → Preserve that later I4 concern; this card publishes only its prerequisite.

## Migration Plan

1. Retain clean-HEAD RED evidence before source edits.
2. Add the platform-neutral fence/diagnostic and transferred-observer
   validator, then the Windows wrapper/callback and exact two call-site edits.
3. Add hostile tests and run the full offline verification floor on the same
   tree and exact explicit staging plan.
4. After fresh GO review, publish one scoped commit.

Rollback reverses only the seven-path patch, removes the private helpers and
tests, and restores the two direct inventory calls. The seven paths must then
match clean baseline `875650a28c838580eb0b2b7516ddf7c274d8cb3d`.

## Open Questions

- None. I5 fixes ownership, dependency and verification boundaries; crossing
  any ceiling is a safety stop requiring a new investigation.
