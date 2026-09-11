## Context

I13 retained a privacy-safe failed-row receipt: the exact published candidate
exited `1` before `native-observation.json` existed, and its outer harness later
observed a different hash for the set of scheduled tasks that did not use the
I13 prefix. I13 correctly stopped before its remaining certification rows.

I14 is investigation-only. It can inspect the unchanged published source and
use only the exact operator-supplied SSH authority retained outside the public
payload. It cannot
edit product/test source, add instrumentation to published paths, retry the
certification matrix, expose raw UI/task/process identity, or alter unrelated
tasks. No TestClient protocol capture or replay is involved.

## Goals / Non-Goals

**Goals:**

- Bind every finding to the unchanged five published-I11 blobs and exact I13
  platform, target, fixtures and candidate argv identity.
- Classify the earliest evidenced S4 failure boundary without retaining raw
  candidate output or private UI data.
- Explain the unrelated-task-set hash change through bounded hashed-set and
  scheduler-event evidence, distinguishing harness effects from independent
  drift and ownership violation.
- Restore the exact configuration before-image and remove only an I14-prefixed
  task, exact stage and processes whose stage/argv identity proves ownership;
  repeat cleanup and require zero removals on the second pass.
- Publish a typed decision and name a separately authorized successor when a
  correction or fresh certification attempt is required.

**Non-Goals:**

- Completing or retrying I13 certification or starting its withheld S4/S5 rows.
- Changing any product/test byte, fixture, target, platform, argv contract,
  public API, wire field, runtime authority, retry, fallback or wait.
- Reading or retaining raw UI, screenshots, credentials, connection strings,
  raw task names or broad process/task/window dumps.
- Stopping, unregistering or otherwise mutating unrelated tasks or processes.

## Decisions

### 1. Static boundary analysis precedes one bounded investigation probe

First inspect the published test and harness control flow and bind its five
blobs to I11. Then run at most one I14-owned S4 isolation probe with the same
candidate arguments and environment identity as I13. The probe classifies raw
test output in memory into a closed enumeration and persists only hashes,
counts, booleans, exit code and the earliest available published diagnostic
stage.

Using I13's six-row runner is rejected because that would retry certification.
Adding a new Go diagnostic or rebuilding different candidate bytes is rejected
because I14 has no source or instrumentation authority.

### 2. Task topology is compared as a privacy-safe hashed identity set

Sample the non-I14 task set as hashes of normalized task path/name identities,
then record only aggregate set hashes, counts and bounded added/removed identity
hashes. Correlate any delta with a narrowly time-bounded Task Scheduler
operational-event projection whose task identity is hashed before output.

Raw task inventories are rejected as broad/private dumps. Treating the one
aggregate I13 before/after mismatch as proof of harness mutation is rejected
because it contains no ownership attribution.

### 3. Classification and successor authority are explicit

Each finding is classified as `contour`, `harness`, `published_behavior`,
`independent_system_drift` or `ownership_violation`. If evidence cannot
distinguish classes, the decision remains `not_verifiable`; it does not infer a
repair. A correction or a new certification attempt must have a separate card
and fresh critical review.

### 4. Cleanup is a hard investigation gate

Capture exact configuration bytes, SDDL-derived ACL hash, creation/write/access
timestamps and attributes before the probe. Cleanup may unregister only the
exact I14 task and stop only exact stage-bound processes. It restores the
captured configuration state, removes the exact stage, then repeats the same
cleanup and proves zero work. Any mismatch blocks review and publication.

## Risks / Trade-offs

- [Raw failure text could disclose paths or UI] -> Classify in memory against a
  closed list and retain only typed labels and hashes.
- [An unrelated task changes during the probe] -> Preserve hashed identity
  deltas and time-bounded scheduler evidence; never mutate the foreign task.
- [The failure does not reproduce] -> Record that result as contour variance;
  do not treat it as I13 certification or run another matrix row.
- [Cleanup targets a foreign process] -> Require both the exact stage boundary
  and argv/executable ownership before termination; otherwise stop.
- [Published behavior needs correction] -> Name a separate authorized successor
  and leave I13 blocked; do not patch in I14.

## Migration Plan

1. Validate source, SSH identity, platform, target, fixtures, candidate and argv
   hashes, plus an uncontended exact-owned surface.
2. Capture bounded configuration and hashed task-topology before-images.
3. Run one isolated I14-owned S4 diagnostic attempt and collect typed evidence.
4. Correlate bounded task-set changes and scheduler events without foreign
   mutation.
5. Restore and double-clean exact-owned state, then validate privacy and scope.
6. Sync/archive the investigation capability and submit the full payload to a
   fresh critical/xhigh reviewer. There is no runtime rollout or rollback.

## Open Questions

None. An unavailable or ambiguous prerequisite is a fail-closed result, not
authority to widen the investigation.
