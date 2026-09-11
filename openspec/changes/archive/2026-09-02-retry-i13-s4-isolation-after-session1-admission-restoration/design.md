## Context

I13 proved the published-I11 source/input lineage and passed its S3 control, but
its first tracked S4 row exited before an observation receipt and the protected
scheduled-task-set hash changed. I14 then used the same source and immutable
inputs but could not admit a typed Session-1 canary, so it correctly invoked no
candidate. Its excluded-task lifecycle ruled out simple inclusion of the owned
task while leaving historical started-route behavior and external drift
indistinguishable.

I15 is the separately authorized evidence-only successor. It uses only the
original operator-approved contour and exact I13/I14 identities. No protocol
capture or replay, Vanessa MCP, EDT/meta snapshot, product/test edit, runtime
configuration change or license change is involved. Dynamic evidence is
limited to typed receipt presence, closed stage/class, exit code, duration,
counts, booleans and hashes. Raw UI, output, screenshots, task names,
credentials, connection strings and broad inventories remain excluded.

## Goals / Non-Goals

**Goals:**

- Rebind the attempt to the unchanged five published-I11 blobs and the exact
  candidate/platform/target/configuration/run-1-fixture/argv identities.
- Capture the initial configuration bytes, ACL, creation/write/access metadata
  and attributes, plus typed exact-owned task/stage/process/job/desktop/
  transport zero-state before any owned creation.
- Require one typed Session-1 canary receipt before any candidate invocation.
- After successful admission only, invoke the exact-source S4 candidate once
  and retain a closed public-safe result.
- Observe the protected task-set and bounded scheduler attribution over the
  original started route so harness/start behavior can be distinguished from
  external drift when evidence permits.
- Restore the exact before-image, remove only exact-owned state and prove a
  repeated cleanup no-op before fresh critical review.

**Non-Goals:**

- Retrying or completing the I13 six-row certification matrix or claiming I13
  certification.
- Provisioning, restoring, unlocking, re-binding, administering or substituting
  any host, principal, session, platform, target, candidate, fixture or argv.
- Changing product/test source, adding diagnostics to published paths, or
  adding public, wire, mutation, retry, fallback or wait behavior.
- Reading, retaining, mutating, stopping or removing unrelated private state.

## Decisions

### 1. Admission and candidate execution are separate fail-closed gates

Preflight first proves source/input/contour identity and an uncontended owned
surface. One exact-owned scheduled invocation then emits a constant typed
receipt from Session 1 containing only host/principal/session equality booleans
and a nonce hash. The candidate invocation count must remain zero unless every
canary predicate succeeds. A missing, late or mismatched receipt ends I15 as
`NOT-VERIFIABLE`/`BLOCKED`; the candidate is not invoked and no substitute route
or retry is allowed.

Combining the canary and candidate in one opaque task is rejected because a
missing candidate receipt would not prove whether Session-1 admission occurred.

### 2. The S4 ceiling is one exact-source run-1 isolation

After a successful canary, use one new exact-owned task on the same started
route to invoke the unchanged candidate with the exact I13 tracked run-1 S4
argv and inputs. Classify candidate output in memory and persist only a closed
stage/class, output hash, receipt presence, exit code, duration, counts and
booleans. The runner must persist a typed pre-invocation marker so invocation
count is provable even if the candidate exits before its own receipt.

Using the I13 matrix runner, another fixture, a rebuilt candidate or a second
attempt is rejected because I15 authorizes isolation only, not certification or
implementation rescue.

### 3. Topology attribution covers the original started route

Hash normalized identities for all tasks except the exact I15-owned identity
before creation, after creation, immediately after the started event and after
cleanup. Retain only aggregate hashes/counts and bounded added/removed identity
hashes. Correlate the exact start window with a bounded Task Scheduler event
projection whose task identities are hashed before persistence. Never retain a
raw inventory or select a foreign task for mutation.

When event attribution and hashes distinguish an owned start side effect from
an independently timed foreign change, classify accordingly. When the event
log or bounded projection cannot distinguish them, retain `NOT-VERIFIABLE` and
infer no topology cause.

### 4. Initial before-images and typed zero-state are mandatory

Before any owned creation, capture configuration bytes, ACL, creation,
last-write, last-access and attributes as privacy-safe hashes/typed values.
Also record typed zero-state for exact task/stage/process/job/desktop/transport
surfaces and the 1C process count. Missing initial last-access or typed
job/desktop/transport state blocks the attempt before candidate invocation;
I15 does not repeat I14's unavailable-continuity claim.

### 5. Exact restoration and double cleanup gate every outcome

Cleanup may unregister only the exact I15 task and stop/remove only state whose
owned stage and argv identity both match. Restore captured configuration state,
with last-access restoration as the final configuration operation. Remove the
exact stage, then repeat the same cleanup and require zero work. Any foreign
target, residual owned state, nonzero 1C process residue or before-image
mismatch blocks review and publication.

## 1C Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | N/A reason / residual risk | Provider owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | none | no source edit | none | `N/A` | `N/A` | No BSL changes; residual risk none. | suite |
| Common server business logic | none | no behavior edit | none | `N/A` | `N/A` | Evidence-only run against unchanged published bytes; residual risk is handled by the live row. | suite |
| New or changed metadata object | none | no source/import plan | none | `N/A` | `N/A` | No metadata changes; residual risk none. | suite |
| Managed form layout | unchanged private TestClient UI | no form change or screenshot | none | `N/A` | `N/A` | Raw UI/screenshots are forbidden; acceptance uses typed native harness evidence, so visual state is intentionally not claimed. | qa-mcp component |
| Form module or command | none | no interaction added | none | `N/A` | `N/A` | No managed-form command is changed; residual risk none. | suite |
| Role rights | none | no role matrix | none | `N/A` | `N/A` | No role-visible change; residual risk none. | suite |
| Document posting or register movement | none | zero business mutation | none | `N/A` | `N/A` | Passive S4 isolation authorizes no write/posting action; a nonzero action blocks the row. | qa-mcp component |
| Report or DCS change | none | no parameters/data | none | `N/A` | `N/A` | No report surface; residual risk none. | suite |
| Migration or data repair | none | no migration/rollback | none | `N/A` | `N/A` | No data migration; residual risk none. | suite |
| Delivery or runtime apply | original Session-1 started route and unchanged exact S4 candidate | one typed canary, conditional one-attempt candidate, exact before-image and recovery model | `scenario_file`, typed `scenario_log`, source/input hashes, scheduler/topology summary, `cleanup_evidence` | `.runtime/changerail/evidence/oss-06-s4-r1-i15-retry-i13-s4-isolation-after-session1-admission-restoration/` | `required` | No alternate target or provider fallback; unavailable exact admission remains a blocker. | project contour and qa-mcp component |

## Risks / Trade-offs

- [Session-1 admission regresses again] -> retain the typed fail-closed result,
  invoke no candidate and name successful exact-route admission as the resume
  condition.
- [Candidate exits before its observation receipt] -> use the typed
  pre-invocation marker and closed output classification without retaining raw
  output.
- [Scheduler history is unavailable or ambiguous] -> preserve bounded hashes
  and record topology as `NOT-VERIFIABLE` without causal inference.
- [Cleanup could touch foreign state] -> require exact task plus stage/argv
  ownership predicates; stop rather than widen cleanup.
- [Private values enter evidence] -> write only schema-limited typed JSON,
  validate the evidence index and run the public-surface scanner before review.

## Migration Plan

1. Validate the clean source lineage, exact input/runtime identities and initial
   configuration/zero-state before-images.
2. Stage only the bounded I15 controller and exact immutable inputs.
3. Run one typed Session-1 canary and stop without candidate invocation unless
   its receipt succeeds.
4. After success only, run one exact-source tracked run-1 S4 isolation while
   collecting bounded started-route topology attribution.
5. Restore configuration, double-clean exact-owned state and validate privacy,
   evidence schema and all offline/workflow gates.
6. Sync/archive the I15 decision capability and obtain a fresh critical/xhigh
   review. There is no rollout; cleanup is the recovery path for every outcome.

## Open Questions

None. Missing or ambiguous prerequisites are typed safety stops, not discretion
to widen the contour or action ceiling.
